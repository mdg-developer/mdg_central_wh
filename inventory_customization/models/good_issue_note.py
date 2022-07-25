from odoo import _, api, fields, models

class GoodIssueNote(models.Model):
    _name = "good.issue.note"
    _description = "Good Issue Note"

    name = fields.Char(String="Name", required=True)
    gin_ref = fields.Char(String="GIN Ref")
    delivery_team = fields.Char(String="Delivery Team")
    requesting_loc = fields.Many2one('stock.location', 'Requesting Location')
    requested_by = fields.Char(String="Requested By")
    issue_date = fields.Date(string='Date for Issie')
    reverse_user = fields.Many2one('res.users', string="Reverse User")
    principle = fields.Char(String="Principle")
    rfi_ref = fields.Char(String="RFI Ref")
    request_warehouse = fields.Many2one('stock.location', 'Request Warehouse')
    branch = fields.Char(String="Branch")
    vehicle_no = fields.Char(String="Vehicle No")
    approved_by = fields.Char(String="Approved By")
    internal_ref = fields.Char(String="Internal Ref")
    issuer = fields.Char(String="Issuer")
    receiver = fields.Char(String="Receiver")
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

    def action_approve(self):
        self.write({'state': 'approve'})

    def action_issue(self):
        self.write({'state': 'issue'})

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
    order_qty = fields.Float(String="Order Qty")
    total_req_qty = fields.Float(String="Total Request Qty")
    qty = fields.Float(String="Qty")
    product_uom_id = fields.Many2one('uom.uom', string="UOM",
                                     domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    batch_no = fields.Char(String="Batch No")
    expiry_date = fields.Date(string='Expiry')
    qty_on_hand = fields.Float(String="Qty on Hand")
    remark = fields.Char(String="Remark")
