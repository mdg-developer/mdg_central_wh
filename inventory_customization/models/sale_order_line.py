from odoo import api, fields, models, SUPERUSER_ID, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    loose = fields.Boolean('Loose', default=False)
    ctn_pickface = fields.Boolean('Ctn', default=False)

    @api.onchange('loose')
    def _loose(self):
        for line in self:
            if line.loose:
                pick_face_route = self.env['stock.location.route'].search(
                    [('pickface_pcs_route', '=', True),('active','=',True)],limit=1)
                if pick_face_route:
                    line.route_id =pick_face_route.id
            else:
                line.route_id =None
                
    @api.onchange('ctn_pickface')
    def _ctn_pickface(self):
        for line in self:
            if line.ctn_pickface:
                pick_face_route = self.env['stock.location.route'].search(
                    [('pickface_ctn_route', '=', True),('active','=',True)],limit=1)
                if pick_face_route:
                    line.route_id =pick_face_route.id
            else:
                line.route_id =None                