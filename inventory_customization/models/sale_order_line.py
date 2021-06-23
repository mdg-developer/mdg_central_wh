from odoo import api, fields, models, SUPERUSER_ID, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    loose = fields.Boolean('Loose', default=False)

    @api.onchange('loose')
    def _loose(self):
        for line in self:
            if line.loose:
                pick_face_route = self.env['stock.location.route'].search(
                    [('pickface_pcs_route', '=', True)],limit=1)
                if pick_face_route:
                    line.route_id =pick_face_route.id
            else:
                line.route_id =None