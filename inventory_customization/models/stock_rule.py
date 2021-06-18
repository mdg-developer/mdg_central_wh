from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from collections import defaultdict, namedtuple
from odoo.tools import float_compare, float_is_zero, html_escape
from odoo import SUPERUSER_ID, _, api, fields, models, registry
import math

class ProcurementException(Exception):
    """An exception raised by ProcurementGroup `run` containing all the faulty
    procurements.
    """
    def __init__(self, procurement_exceptions):
        """:param procurement_exceptions: a list of tuples containing the faulty
        procurement and their error messages
        :type procurement_exceptions: list
        """
        self.procurement_exceptions = procurement_exceptions

class StockRule(models.Model):
    """ A rule describe what a procurement should do; produce, buy, move, ... """
    _inherit = 'stock.rule'
    
    def splitting_stock_move(self,procurement, rule, moves_values_by_company,procure_method):
#         move_values=[]
#         new_procurements = []
        product = self.env['product.product'].search([('id', '=', procurement.product_id.id)])
       
        pallet_size = product.product_tmpl_id.pallet_quantity
        pick_face_qty = pallet_qty = 0
        if pallet_size>0:
            #divisor =  math.ceil(procurement.product_qty / pallet_quantity)
            if procurement.product_qty<pallet_size:
                pick_face_qty = procurement.product_qty
            elif procurement.product_qty> pallet_size:
                pick_face_qty = procurement.product_qty % pallet_size
                pallet_qty = procurement.product_qty / pallet_size
        else:
            pick_face_qty = procurement.product_qty
        
        #only pickface qty exist  like orignal
        if pallet_qty==0 and pick_face_qty>0:
#             procurement.product_qty = pick_face_qty
            move_values = rule._get_stock_move_values(procurement.product_id, pick_face_qty, procurement.product_uom,procurement.location_id,procurement.name, procurement.origin, procurement.company_id, procurement.values)
        #pickface, pallet
        elif pallet_qty>0 and pick_face_qty>0:
            #pallet generation
            #warehouse_stock_location
            procurement_warehouse = procurement.values.get('warehouse_id').id                                
            stock_location = self.env['stock.location'].search([('warehouse_id', '=', procurement_warehouse),('name', 'ilike', 'SHIPTO')], order='id', limit=1)
#             procurement.append({'location_id' : stock_location})
#             procurement.product_qty = pallet_qty*pallet_size
            quantity = pallet_qty*pallet_size
#             new_procurements.append(self.env['procurement.group'].Procurement(
#                 procurement.product_id, quantity, procurement.product_uom,
#                 stock_location,
#                 procurement.name, procurement.origin, procurement.company_id, procurement.values))
            move_values = rule._get_stock_move_values(procurement.product_id, quantity, procurement.product_uom,stock_location,procurement.name, procurement.origin, procurement.company_id, procurement.values)
            move_values['procure_method'] = procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)
            
            for company_id, moves_values in moves_values_by_company.items():
                # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
                moves = self.env['stock.move'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(moves_values)
                # Since action_confirm launch following procurement_group we should activate it.
                moves._action_confirm()              
            #pickface generation, original
#             procurement.product_qty = pick_face_qty
            move_values = rule._get_stock_move_values(procurement.product_id, pick_face_qty, procurement.product_uom,stock_location,procurement.name, procurement.origin, procurement.company_id, procurement.values)
            
#             move_values.append(pallet_move_values)
#             move_values.append(pick_face_move_values)
        
        elif pallet_qty>0 and pick_face_qty==0:
            #pallet generation
            #warehouse_stock_location
            procurement_warehouse = procurement.values.get('warehouse_id').id                                
            stock_location = self.env['stock.location'].search([('warehouse_id', '=', procurement_warehouse),('name', 'ilike', 'Stock')], order='id', limit=1)
            procurement.location_id =stock_location
            procurement.product_qty = pallet_qty*pallet_size
            pallet_face_move_values = rule._get_stock_move_values(*procurement)
            move_values = pallet_face_move_values        
        return move_values
            
    @api.model
    def _run_pull(self, procurements):
        moves_values_by_company = defaultdict(list)
        mtso_products_by_locations = defaultdict(list)

        # To handle the `mts_else_mto` procure method, we do a preliminary loop to
        # isolate the products we would need to read the forecasted quantity,
        # in order to to batch the read. We also make a sanitary check on the
        # `location_src_id` field.
        for procurement, rule in procurements:
            if not rule.location_src_id:
                msg = _('No source location defined on stock rule: %s!') % (rule.name, )
                raise ProcurementException([(procurement, msg)])

            if rule.procure_method == 'mts_else_mto':
                mtso_products_by_locations[rule.location_src_id].append(procurement.product_id.id)

        # Get the forecasted quantity for the `mts_else_mto` procurement.
        forecasted_qties_by_loc = {}
        for location, product_ids in mtso_products_by_locations.items():
            products = self.env['product.product'].browse(product_ids).with_context(location=location.id)
            forecasted_qties_by_loc[location] = {product.id: product.free_qty for product in products}

        # Prepare the move values, adapt the `procure_method` if needed.
        for procurement, rule in procurements:
            is_shipto_location = False
            procure_method = rule.procure_method
            if rule.procure_method == 'mts_else_mto':
                qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
                qty_available = forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id]
                if float_compare(qty_needed, qty_available, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:
                    procure_method = 'make_to_stock'
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
                else:
                    procure_method = 'make_to_order'
            
            #warehouse spitting
            if not procurement.values.get('sale_line_id'):
                location = self.env['stock.location'].search([('id', '=', procurement.location_id.id)])
                if location and location.name.lower() == 'shipto':
                    is_shipto_location = True
                if is_shipto_location == True:
                    move_values = self.splitting_stock_move(procurement,rule,moves_values_by_company,procure_method)
                else:
                    move_values = rule._get_stock_move_values(*procurement)
            else:
                move_values = rule._get_stock_move_values(*procurement)
            move_values['procure_method'] = procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)

        for company_id, moves_values in moves_values_by_company.items():
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            moves = self.env['stock.move'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(moves_values)
            # Since action_confirm launch following procurement_group we should activate it.
            moves._action_confirm()
        return True
    
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'pull' or 'pull_push') set on it.

        :param procurement: browse record
        :rtype: dictionary
        '''
        group_id = False
        if self.group_propagation_option == 'propagate':
            group_id = values.get('group_id', False) and values['group_id'].id
        elif self.group_propagation_option == 'fixed':
            group_id = self.group_id.id

        date_scheduled = fields.Datetime.to_string(
            fields.Datetime.from_string(values['date_planned']) - relativedelta(days=self.delay or 0)
        )
        date_deadline = values.get('date_deadline') and (fields.Datetime.to_datetime(values['date_deadline']) - relativedelta(days=self.delay or 0)) or False
        partner = self.partner_address_id or (values.get('group_id', False) and values['group_id'].partner_id)
        if partner:
            product_id = product_id.with_context(lang=partner.lang or self.env.user.lang)
        picking_description = product_id._get_description(self.picking_type_id)
        if values.get('product_description_variants'):
            picking_description += values['product_description_variants']
        # it is possible that we've already got some move done, so check for the done qty and create
        # a new move with the correct qty
        qty_left = product_qty

        move_dest_ids = []
        if not self.location_id.should_bypass_reservation():
            move_dest_ids = values.get('move_dest_ids', False) and [(4, x.id) for x in values['move_dest_ids']] or []

        move_values = {
            'name': name[:2000],
            'company_id': self.company_id.id or self.location_src_id.company_id.id or self.location_id.company_id.id or company_id.id,
            'product_id': product_id.id,
            'product_uom': product_uom.id,
            'product_uom_qty': qty_left,
            'partner_id': partner.id if partner else False,
            'location_id': self.location_src_id.id,
            'location_dest_id': location_id.id,
            'move_dest_ids': move_dest_ids,
            'rule_id': self.id,
            'procure_method': self.procure_method,
            'origin': origin,
            'picking_type_id': self.picking_type_id.id,
            'group_id': group_id,
            'route_ids': [(4, route.id) for route in values.get('route_ids', [])],
            'warehouse_id': self.propagate_warehouse_id.id or self.warehouse_id.id,
            'date': date_scheduled,
            'date_deadline': False if self.group_propagation_option == 'fixed' else date_deadline,
            'propagate_cancel': self.propagate_cancel,
            'description_picking': picking_description,
            'priority': values.get('priority', "0"),
            'orderpoint_id': values.get('orderpoint_id') and values['orderpoint_id'].id,
        }
        for field in self._get_custom_move_fields():
            if field in values:
                move_values[field] = values.get(field)
        return move_values
    