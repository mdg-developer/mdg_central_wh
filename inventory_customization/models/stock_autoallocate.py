from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
from odoo.tools.misc import format_date, OrderedSet
from itertools import groupby
from operator import itemgetter

class StockMove(models.Model):
    _inherit = "stock.move"
    
    def _push_apply2(self):
        exist_locations =[]
        for move in self:
            # if the move is already chained, there is no need to check push rules
            if move.move_dest_ids:
                continue
            # if the move is a returned move, we don't want to check push rules, as returning a returned move is the only decent way
            # to receive goods without triggering the push rules again (which would duplicate chained operations)
            domain = [('location_src_id', '=', move.location_dest_id.id), ('action', 'in', ('push', 'pull_push'))]
            # first priority goes to the preferred routes defined on the move itself (e.g. coming from a SO line)
            warehouse_id = move.warehouse_id or move.picking_id.picking_type_id.warehouse_id
            if move.location_dest_id.company_id == self.env.company:
                rules = self.env['procurement.group']._search_rule(move.route_ids, move.product_packaging_id, move.product_id, warehouse_id, domain)
            else:
                rules = self.sudo().env['procurement.group']._search_rule(move.route_ids, move.product_packaging_id, move.product_id, warehouse_id,domain)
            # Make sure it is not returning the return
            if rules and (
                    not move.origin_returned_move_id or move.origin_returned_move_id.location_dest_id.id != rules.location_id.id):
                rules._run_push(move,exist_locations)
    
    def _action_confirm(self, merge=True, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        for move in self:
            if move.state != 'draft':
                continue
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        procurement_requests = []
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            origin = (move.group_id and move.group_id.name or (move.origin or move.picking_id.name or "/"))
            procurement_requests.append(self.env['procurement.group'].Procurement(
                move.product_id, move.product_uom_qty, move.product_uom,
                move.location_id, move.rule_id and move.rule_id.name or "/",
                origin, move.company_id, values))
        self.env['procurement.group'].run(procurement_requests, raise_user_error=not self.env.context.get('from_orderpoint'))

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves._assign_picking()
        self._push_apply2()
        self._check_company()
        moves = self
        if merge:
            moves = self._merge_moves(merge_into=merge_into)
        # call `_action_assign` on every confirmed move which location_id bypasses the reservation
        moves.filtered(lambda move: not move.picking_id.immediate_transfer and move._should_bypass_reservation() and move.state == 'confirmed')._action_assign()
        return moves
    
    def _action_assign(self):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `product_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """

        StockMove = self.env['stock.move']
        assigned_moves_ids = OrderedSet()
        partially_available_moves_ids = OrderedSet()
        # Read the `reserved_availability` field of the moves out of the loop to prevent unwanted
        # cache invalidation when actually reserving the move.
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        #customization
        existing_locations=[]
        
        for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
            rounding = roundings[move]
            missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
            missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity, move.product_id.uom_id, rounding_method='HALF-UP')
            if move._should_bypass_reservation():
                # create the move line(s) but do not impact quants
                if move.product_id.tracking == 'serial' and (move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                    for i in range(0, int(missing_reserved_quantity)):
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=1))
                else:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                            ml.location_id == move.location_id and
                                                            ml.location_dest_id == move.location_dest_id and
                                                            ml.picking_id == move.picking_id and
                                                            not ml.lot_id and
                                                            not ml.package_id and
                                                            not ml.owner_id)
                    if to_update:
                        to_update[0].product_uom_qty += missing_reserved_uom_quantity
                    else:
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=missing_reserved_quantity))
                assigned_moves_ids.add(move.id)
            else:
                if float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                    assigned_moves_ids.add(move.id)
                elif not move.move_orig_ids:
                    if move.procure_method == 'make_to_order':
                        continue
                    # If we don't need any quantity, consider the move assigned.
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=rounding):
                        assigned_moves_ids.add(move.id)
                        continue
                    # Reserve new quants and create move lines accordingly.
                    forced_package_id = move.package_level_id.package_id or None
                    available_quantity = move._get_available_quantity(move.location_id, package_id=forced_package_id)
                    if available_quantity <= 0:
                        continue
                    taken_quantity = move._update_reserved_quantity2(need, available_quantity, move.location_id, package_id=forced_package_id, strict=False, existing_locations=existing_locations)
                    if float_is_zero(taken_quantity, precision_rounding=rounding):
                        continue
                    if float_compare(need, taken_quantity, precision_rounding=rounding) == 0:
                        assigned_moves_ids.add(move.id)
                    else:
                        partially_available_moves_ids.add(move.id)
                else:
                    # Check what our parents brought and what our siblings took in order to
                    # determine what we can distribute.
                    # `qty_done` is in `ml.product_uom_id` and, as we will later increase
                    # the reserved quantity on the quants, convert it here in
                    # `product_id.uom_id` (the UOM of the quants is the UOM of the product).
                    move_lines_in = move.move_orig_ids.filtered(lambda m: m.state == 'done').mapped('move_line_ids')
                    keys_in_groupby = ['location_dest_id', 'lot_id', 'result_package_id', 'owner_id']

                    def _keys_in_sorted(ml):
                        return (ml.location_dest_id.id, ml.lot_id.id, ml.result_package_id.id, ml.owner_id.id)

                    grouped_move_lines_in = {}
                    for k, g in groupby(sorted(move_lines_in, key=_keys_in_sorted), key=itemgetter(*keys_in_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_in[k] = qty_done
                    move_lines_out_done = (move.move_orig_ids.mapped('move_dest_ids') - move)\
                        .filtered(lambda m: m.state in ['done'])\
                        .mapped('move_line_ids')
                    # As we defer the write on the stock.move's state at the end of the loop, there
                    # could be moves to consider in what our siblings already took.
                    moves_out_siblings = move.move_orig_ids.mapped('move_dest_ids') - move
                    moves_out_siblings_to_consider = moves_out_siblings & (StockMove.browse(assigned_moves_ids) + StockMove.browse(partially_available_moves_ids))
                    reserved_moves_out_siblings = moves_out_siblings.filtered(lambda m: m.state in ['partially_available', 'assigned'])
                    move_lines_out_reserved = (reserved_moves_out_siblings | moves_out_siblings_to_consider).mapped('move_line_ids')
                    keys_out_groupby = ['location_id', 'lot_id', 'package_id', 'owner_id']

                    def _keys_out_sorted(ml):
                        return (ml.location_id.id, ml.lot_id.id, ml.package_id.id, ml.owner_id.id)

                    grouped_move_lines_out = {}
                    for k, g in groupby(sorted(move_lines_out_done, key=_keys_out_sorted), key=itemgetter(*keys_out_groupby)):
                        qty_done = 0
                        for ml in g:
                            qty_done += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
                        grouped_move_lines_out[k] = qty_done
                    for k, g in groupby(sorted(move_lines_out_reserved, key=_keys_out_sorted), key=itemgetter(*keys_out_groupby)):
                        grouped_move_lines_out[k] = sum(self.env['stock.move.line'].concat(*list(g)).mapped('product_qty'))
                    available_move_lines = {key: grouped_move_lines_in[key] - grouped_move_lines_out.get(key, 0) for key in grouped_move_lines_in.keys()}
                    # pop key if the quantity available amount to 0
                    available_move_lines = dict((k, v) for k, v in available_move_lines.items() if v)

                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(lambda m: m.product_qty):
                        if available_move_lines.get((move_line.location_id, move_line.lot_id, move_line.result_package_id, move_line.owner_id)):
                            available_move_lines[(move_line.location_id, move_line.lot_id, move_line.result_package_id, move_line.owner_id)] -= move_line.product_qty
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        need = move.product_qty - sum(move.move_line_ids.mapped('product_qty'))
                        # `quantity` is what is brought by chained done move lines. We double check
                        # here this quantity is available on the quants themselves. If not, this
                        # could be the result of an inventory adjustment that removed totally of
                        # partially `quantity`. When this happens, we chose to reserve the maximum
                        # still available. This situation could not happen on MTS move, because in
                        # this case `quantity` is directly the quantity on the quants themselves.
                        available_quantity = move._get_available_quantity(location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
                        if float_is_zero(available_quantity, precision_rounding=rounding):
                            continue
                        taken_quantity = move._update_reserved_quantity2(need, min(quantity, available_quantity), location_id, lot_id, package_id, owner_id,strict=True,existing_locations=existing_locations)
                        if float_is_zero(taken_quantity, precision_rounding=rounding):
                            continue
                        if float_is_zero(need - taken_quantity, precision_rounding=rounding):
                            assigned_moves_ids.add(move.id)
                            break
                        partially_available_moves_ids.add(move.id)
            if move.product_id.tracking == 'serial':
                move.next_serial_count = move.product_uom_qty
        self.env['stock.move.line'].create(move_line_vals_list)
        StockMove.browse(partially_available_moves_ids).write({'state': 'partially_available'})
        StockMove.browse(assigned_moves_ids).write({'state': 'assigned'})
        if self.reference:
            if ('INT' in self.reference and self.mapped('picking_id').location_dest_id.pick_face):
                return
        self.mapped('picking_id')._check_entire_pack()
    
    def _update_reserved_quantity2(self, need, available_quantity, location_id, lot_id=None, package_id=None, owner_id=None, strict=True, existing_locations=None):
        """ Create or update move lines.
        """
        self.ensure_one()

        if not lot_id:
            lot_id = self.env['stock.production.lot']
        if not package_id:
            package_id = self.env['stock.quant.package']
        if not owner_id:
            owner_id = self.env['res.partner']

        taken_quantity = min(available_quantity, need)

        # `taken_quantity` is in the quants unit of measure. There's a possibility that the move's
        # unit of measure won't be respected if we blindly reserve this quantity, a common usecase
        # is if the move's unit of measure's rounding does not allow fractional reservation. We chose
        # to convert `taken_quantity` to the move's unit of measure with a down rounding method and
        # then get it back in the quants unit of measure with an half-up rounding_method. This
        # way, we'll never reserve more than allowed. We do not apply this logic if
        # `available_quantity` is brought by a chained move line. In this case, `_prepare_move_line_vals`
        # will take care of changing the UOM to the UOM of the product.
        if not strict and self.product_id.uom_id != self.product_uom:
            taken_quantity_move_uom = self.product_id.uom_id._compute_quantity(taken_quantity, self.product_uom, rounding_method='DOWN')
            taken_quantity = self.product_uom._compute_quantity(taken_quantity_move_uom, self.product_id.uom_id, rounding_method='HALF-UP')

        quants = []
        rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        if self.product_id.tracking == 'serial':
            if float_compare(taken_quantity, int(taken_quantity), precision_digits=rounding) != 0:
                taken_quantity = 0

        try:
            with self.env.cr.savepoint():
                if not float_is_zero(taken_quantity, precision_rounding=self.product_id.uom_id.rounding):
                    quants = self.env['stock.quant']._update_reserved_quantity(
                        self.product_id, location_id, taken_quantity, lot_id=lot_id,
                        package_id=package_id, owner_id=owner_id, strict=strict
                    )
        except UserError:
            taken_quantity = 0

        # Find a candidate move line to update or create a new one.
        for reserved_quant, quantity in quants:
            to_update = self.move_line_ids.filtered(lambda ml: ml._reservation_is_updatable(quantity, reserved_quant))
            if to_update:
                uom_quantity = self.product_id.uom_id._compute_quantity(quantity, to_update[0].product_uom_id, rounding_method='HALF-UP')
                uom_quantity = float_round(uom_quantity, precision_digits=rounding)
                uom_quantity_back_to_product_uom = to_update[0].product_uom_id._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
            if to_update and float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                to_update[0].with_context(bypass_reservation_update=True).product_uom_qty += uom_quantity
            else:
                if self.product_id.tracking == 'serial':
                    for i in range(0, int(quantity)):
                        self.env['stock.move.line'].create(self._prepare_move_line_vals2(quantity=1, reserved_quant=reserved_quant,existing_locations=existing_locations))
                else:
                    self.env['stock.move.line'].create(self._prepare_move_line_vals2(quantity=quantity, reserved_quant=reserved_quant,existing_locations=existing_locations))
        return taken_quantity
    
    def _prepare_move_line_vals2(self, quantity=None, reserved_quant=None,existing_locations=None):
        self.ensure_one()
        # apply putaway
        location_dest_id = self.location_dest_id._get_putaway_strategy2(self.product_id, existing_locations).id or self.location_dest_id.id
        existing_locations.append(location_dest_id)
        vals = {
            'move_id': self.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': location_dest_id,
            'picking_id': self.picking_id.id,
            'company_id': self.company_id.id,
        }
        if quantity:
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom, rounding_method='HALF-UP')
            uom_quantity = float_round(uom_quantity, precision_digits=rounding)
            uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id, rounding_method='HALF-UP')
            if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
                vals = dict(vals, product_uom_qty=uom_quantity)
            else:
                vals = dict(vals, product_uom_qty=quantity, product_uom_id=self.product_id.uom_id.id)
        if reserved_quant:
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                package_id=reserved_quant.package_id.id or False,
                owner_id =reserved_quant.owner_id.id or False,
            )
        return vals
    
class Location(models.Model):
    _inherit = "stock.location"
    
    def exist_location(self,put_way_location, existing_locations):
        existed = False;
        if len(existing_locations) > 0:
            for eloc in existing_locations:
                if eloc == put_way_location.id:
                    existed = True;
                    break;
        return existed

    def _get_putaway_strategy2(self, product,existing_locations):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        current_location = self
        putaway_location = self.env['stock.location']
        quant = self.env['stock.quant']
        product_product = self.env['product.product']

        while current_location and not putaway_location:
            # Looking for a putaway about the product.
            putaway_rules = current_location.putaway_rule_ids.filtered(lambda x: x.product_id == product)
            if putaway_rules:
                putaway_location = putaway_rules[0].location_out_id
                for rule in putaway_rules:
                    records = quant.search([('location_id','=',rule.location_out_id.id),('product_id','=',product.id)])
                    existed  = self.exist_location(rule.location_out_id,existing_locations)
                    if  existed == False and len(records) == 0:                        
                        putaway_location = rule.location_out_id
                        break
                    else:
                        continue
                    
            # If not product putaway found, we're looking with category so.
            else:
                categ = product.categ_id
                while categ:
                    putaway_rules = current_location.putaway_rule_ids.filtered(lambda x: x.category_id == categ)
                    if putaway_rules:
                        putaway_location = putaway_rules[0].location_out_id
                        for rule in putaway_rules:
                            product_records = product_product.search([('categ_id','=',categ.id)])
                            print(product_records)
                            print(product_records.ids)

                            records = quant.search([('location_id','=',rule.location_out_id.id),('product_id','in',product_records.ids)])
                            existed  = self.exist_location(rule.location_out_id,existing_locations)
                            if  existed == False and len(records) == 0:                        
                                putaway_location = rule.location_out_id
                                break
                            else:
                                continue                    
#                     if putaway_rules:
#                         putaway_location = putaway_rules[0].location_out_id
#                         break
                    categ = categ.parent_id
            current_location = current_location.location_id
        return putaway_location

class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_push(self, move,exist_locations):
        """ Apply a push rule on a move.
        If the rule is 'no step added' it will modify the destination location
        on the move.
        If the rule is 'manual operation' it will generate a new move in order
        to complete the section define by the rule.
        Care this function is not call by method run. It is called explicitely
        in stock_move.py inside the method _push_apply
        """
        new_date = fields.Datetime.to_string(move.date + relativedelta(days=self.delay))
        if self.auto == 'transparent':
            old_dest_location = move.location_dest_id
            move.write({'date': new_date, 'location_dest_id': self.location_id.id})
            # make sure the location_dest_id is consistent with the move line location dest
            if move.move_line_ids:
                move.move_line_ids.location_dest_id = move.location_dest_id._get_putaway_strategy2(move.product_id,exist_locations) or move.location_dest_id
                exist_locations.append(move.move_line_ids.location_dest_id)
            # avoid looping if a push rule is not well configured; otherwise call again push_apply to see if a next step is defined
            if self.location_id != old_dest_location:
                # TDE FIXME: should probably be done in the move model IMO
                move._push_apply2()
        else:
            new_move_vals = self._push_prepare_move_copy_values(move, new_date)
            new_move = move.sudo().copy(new_move_vals)
            if new_move._should_bypass_reservation():
                new_move.write({'procure_method': 'make_to_stock'})
            if not new_move.location_id.should_bypass_reservation():
                move.write({'move_dest_ids': [(4, new_move.id)]})
            new_move._action_confirm()


