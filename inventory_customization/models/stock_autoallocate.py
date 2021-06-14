from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from dateutil.relativedelta import relativedelta

class Location(models.Model):
    _inherit = "stock.location"
    
    def _get_putaway_strategy(self, product):
        ''' Returns the location where the product has to be put, if any compliant putaway strategy is found. Otherwise returns None.'''
        current_location = self
        putaway_location = self.env['stock.location']
        while current_location and not putaway_location:
            # Looking for a putaway about the product.
            putaway_rules = current_location.putaway_rule_ids.filtered(lambda x: x.product_id == product)
            if putaway_rules:
                putaway_location = putaway_rules[0].location_out_id
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
    
class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_push(self, move):
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
    