from odoo import _, api, fields, models
import datetime

class GoodIssueNote(models.Model):
    _name = "good.issue.note"
    _description = "Good Issue Note"

    name = fields.Char(string="Name", required=True, default=lambda self: self.env['ir.sequence'].next_by_code('stock.gin'), readonly=True)
    gin_ref = fields.Char(string="GIN Ref")
    delivery_team = fields.Char(string="Delivery Team")
    requesting_loc = fields.Many2one('stock.location', 'Requesting Location')
    requested_by = fields.Char(string="Requested By")
    issue_date = fields.Date(string='Date for Issie')
    reverse_user = fields.Many2one('res.users', string="Reverse User")
    principle = fields.Char(string="Principle")
    rfi_ref = fields.Char(string="RFI Ref")
    request_warehouse = fields.Char(string='Request Warehouse')
    branch = fields.Char(string="Branch")
    vehicle_no = fields.Char(string="Vehicle No")
    approved_by = fields.Char(string="Approved By")
    internal_ref = fields.Char(string="Internal Ref")
    issuer = fields.Char(string="Issuer")
    receiver = fields.Char(string="Receiver")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('issue', 'Issue'),
        ('cancel', 'Cancel'),
        ('reversed', 'Reverse'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    gin_line = fields.One2many('good.issue.note.line', 'gin_id', string='Good Issue Note Lines',
                                 states={'cancel': [('readonly', True)], 'issue': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('stock.gin') or _('New')
    #     res = super(GoodIssueNote, self).create(vals)
    #     return res

    def action_approve(self):
        user = self.env['res.users'].browse(self.env.uid)
        customer_location = self.env['stock.location'].search(
            [('name', '=', 'Customers')], limit=1)
        pick_out = self.env['stock.picking.type'].search(
            [('warehouse_id', '=', 1), ('code', '=', 'outgoing')],
            limit=1,
        )
        picking = self.env['stock.picking'].create({
            # 'partner_id': self.subcontractor_partner.id,
            'location_id': self.requesting_loc.id,
            'location_dest_id': customer_location.id,
            'picking_type_id': pick_out.id,
            'origin': self.gin_ref,
        })
        for line in self.gin_line:
            if line.product_uom_id.id == line.product_id.uom_id.id:
                move_vals = {
                    'name': 'GIN-Issue',
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'product_uom_qty': line.total_req_qty,
                    'picking_id': picking.id,
                    'location_id': self.requesting_loc.id,
                    'location_dest_id': customer_location.id,
                    'origin': self.name,

                }
            else:
                to_base_qty = line.total_req_qty * line.product_uom_id.factor_inv
                move_vals = {
                    'name': 'GIN-Issue',
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uom_qty': to_base_qty,
                    'picking_id': picking.id,
                    'location_id': self.requesting_loc.id,
                    'location_dest_id': customer_location.id,
                    'origin': self.name,

                }

            self.env['stock.move'].create(move_vals)
        picking.action_confirm()
        picking.action_assign()
        self.write({'state': 'approve', 'approved_by': user.name})

    def action_issue(self):
        current_date = fields.Date.today()
        user = self.env['res.users'].browse(self.env.uid)
        self.write({'state': 'issue', 'issuer': user.name, 'issue_date':current_date})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reverse(self):
        self.write({'state': 'reversed'})


class GoodIssueNoteLine(models.Model):
    _name = "good.issue.note.line"
    _description = "Good Issue Note Line"

    gin_id = fields.Many2one('good.issue.note', string='GIN Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    product_id = fields.Many2one("product.product", string="Product")
    order_qty = fields.Float(string="Order Qty")
    total_req_qty = fields.Float(string="Total Request Qty")
    qty = fields.Float(string="Qty")
    product_uom_id = fields.Many2one('uom.uom', string="UOM",
                                     domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    batch_no = fields.Char(string="Batch No")
    expiry_date = fields.Date(string='Expiry')
    qty_on_hand = fields.Float(string="Qty on Hand")
    remark = fields.Char(string="Remark")
