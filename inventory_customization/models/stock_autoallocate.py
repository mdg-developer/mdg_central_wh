from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from dateutil.relativedelta import relativedelta



class Location(models.Model):
    _inherit = "stock.location"
    def exist_location(self,put_way_location, existing_locations):
        existed = False;
        if len(existing_locations) > 0:
            for eloc in existing_locations:
                if eloc == put_way_location:
                    existed = True;
                    break;
        return existed

    def _get_putaway_strategy(self, product,existing_locations):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        current_location = self
        putaway_location = self.env['stock.location']
        quant = self.env['stock.quant']
        while current_location and not putaway_location:
            # Looking for a putaway about the product.
            putaway_rules = current_location.putaway_rule_ids.filtered(lambda x: x.product_id == product)
            if putaway_rules:
                putaway_location = putaway_rules[0].location_out_id
                for rule in putaway_rules:
                    records = quant.search([('location_id','=',rule.location_out_id),('product_id','=',product)])
                    existed  = self.exist_location(records.location_out_id,existing_locations)
                    if  existed:
                        continue
                    else:
                        putaway_location = rule.location_out_id
                        break
            # If not product putaway found, we're looking with category so.
            else:
                categ = product.categ_id
                while categ:
                    putaway_rules = current_location.putaway_rule_ids.filtered(lambda x: x.category_id == categ)
                    if putaway_rules:
                        putaway_location = putaway_rules[0].location_out_id
                        break
                    categ = categ.parent_id
            current_location = current_location.location_id
        return putaway_location
    
    def _push_apply(self):
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
                rules = self.env['procurement.group']._search_rule(move.route_ids, move.product_id, warehouse_id, domain)
            else:
                rules = self.sudo().env['procurement.group']._search_rule(move.route_ids, move.product_id, warehouse_id,
                                                                          domain)
            # Make sure it is not returning the return
            if rules and (
                    not move.origin_returned_move_id or move.origin_returned_move_id.location_dest_id.id != rules.location_id.id):
                rules._run_push(move,exist_locations)


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
                move.move_line_ids.location_dest_id = move.location_dest_id._get_putaway_strategy(move.product_id,exist_locations) or move.location_dest_id
                exist_locations.append(move.move_line_ids.location_dest_id)
            # avoid looping if a push rule is not well configured; otherwise call again push_apply to see if a next step is defined
            if self.location_id != old_dest_location:
                # TDE FIXME: should probably be done in the move model IMO
                move._push_apply()
        else:
            new_move_vals = self._push_prepare_move_copy_values(move, new_date)
            new_move = move.sudo().copy(new_move_vals)
            if new_move._should_bypass_reservation():
                new_move.write({'procure_method': 'make_to_stock'})
            if not new_move.location_id.should_bypass_reservation():
                move.write({'move_dest_ids': [(4, new_move.id)]})
            new_move._action_confirm()

