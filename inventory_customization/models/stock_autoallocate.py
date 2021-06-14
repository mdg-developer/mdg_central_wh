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
        quant = self.env['stock.quant']
        while current_location and not putaway_location:
            # Looking for a putaway about the product.

            putaway_rules = current_location.putaway_rule_ids.filtered(lambda x: x.product_id == product)
            if putaway_rules:
                putaway_location = putaway_rules[0].location_out_id
                for rule in putaway_rules:
                    records = quant.search([('location_id','=',rule.location_out_id),('product_id','=',product)])
                    if len(records) == 0 or not records:
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