# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import Counter

from odoo import _, api, fields, tools, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    bigger_uom_qty_done = fields.Float('Bigger UOM Done', digits='Product Unit of Measure', copy=False)
    basic_uom_qty_done = fields.Float('Basic UOM Done', digits='Product Unit of Measure', copy=False)
    bigger_uom_id = fields.Many2one('uom.uom', 'Unit of Measure',related='product_id.uom_po_id',domain="[('id', '=', product_purchase_category_id)]")
    demand_bigger_qty = fields.Float('Demand Case', default=0.0, digits='Product Unit of Measure',
                                     compute='_bigger_quantity_done_compute', store=True)
    bigger_category_id = fields.Many2one(related='product_id.uom_po_id')

    basic_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', related='product_id.uom_id',
                                    domain="[('id', '=', product_purchase_category_id)]")
    basic_category_id = fields.Many2one(related='product_id.uom_id')
    dummy_product_pallet = fields.Float(related='product_id.product_tmpl_id.pallet_quantity', store=True)
    dummy = fields.Float(related='product_id.uom_po_id.factor_inv', store=True)
    ti = fields.Integer(related="product_id.product_tmpl_id.ti", store=True)
    hi = fields.Integer(related="product_id.product_tmpl_id.hi", store=True)
    tixhi = fields.Integer('TI X HI', compute='_compute_ti_hi')
    dummy_result_package_id = fields.Char("Destination Package")
    has_scanned_loc = fields.Boolean('Scanned Destination Location?', default=False)
    product_check = fields.Char("Product Check" )
    product_check_flag = fields.Char('Product Check',default='False')
    check_product_msg = fields.Char('Wrong Product Message', default='Verify the Product First!', readonly=True)
    picking_sequence_code = fields.Char(related='picking_id.picking_type_id.sequence_code')

    product_purchase_uom_id_factor = fields.Float(related='product_id.uom_po_id.factor_inv')
    product_purchase_uom_id_name = fields.Char(related='product_id.uom_po_id.name')
    is_shipto_location = fields.Boolean('Is Ship To Location?', compute='_compute_is_shipto_location')

    @api.depends('product_id')
    def _bigger_quantity_done_compute(self):
        for record in self:
            record.demand_bigger_qty = record.product_uom_qty / record.bigger_uom_id.factor_inv

    @api.onchange('qty_done')
    def onchange_qty_done(self):
        if self.qty_done and self.picking_id.picking_type_id.sequence_code in ('PICK', 'PICKCA', 'PICKL', 'OUT'):
            if self.qty_done > self.product_uom_qty:
                demand_amt = self.product_uom_qty
                self.update({
                    'qty_done': demand_amt,
                })
                self.env.cr.commit()
                raise UserError(_('Cannot Issue More than the Demanded Quantity!'))
    @api.depends('is_shipto_location', 'location_dest_id')
    def _compute_is_shipto_location(self):
        for record in self:
            loc_record = self.env['stock.location'].search([('id','=',record.location_dest_id.id)])
            record.is_shipto_location = loc_record.ship_to

    @api.onchange('expiration_date')
    def onchange_expiration_date(self):
        if self.expiration_date and self.picking_id.picking_type_id.sequence_code == 'IN':
            inbound_shelf_life = self.product_id.inbound_shelf_life
            if inbound_shelf_life != 0.0:
                today = fields.Date.today()
                last_date = today+timedelta(days=self.product_id.inbound_shelf_life)
                if self.expiration_date < last_date:
                    raise UserError(_('Check Inbound Shelf Life of the Product!'))
            batch = self.expiration_date.strftime("%d%m%Y")
            self.update({
                'lot_name': batch
            })
    @api.onchange('product_check')
    def onchange_product_check(self):
        if self.product_check:
            product = self.product_id
            barcode_names = []
            if product.barcode_ids:
                barcode_names = product.mapped('barcode_ids.name')
            if product.barcode:
                barcode_names.append(product.barcode)

            # if self.product_id.barcode != self.product_check:
            if self.product_check not in barcode_names:
                self.update({
                    'product_check_flag': 'False',
                })

                raise ValidationError(_('Wrong Product !'))
            else:
                self.update({
                    'product_check_flag': 'True'
                })
                if self.picking_id.picking_type_id.code in ('incoming','outgoing') or self.picking_id.picking_type_id.sequence_code == 'PICK':
                    same_prod = self.env['stock.move.line'].search([('picking_id', '=', self.picking_id.id), ('product_id', '=', self.product_id.id)])
                    for record in same_prod:
                        record.update({
                            'product_check_flag': 'True'
                        })



        else:
            self.update({
                'product_check_flag': 'False'
            })

        if self.picking_id.picking_type_id.code == 'incoming':
            same_prod = self.env['stock.move.line'].search([('picking_id', '=', self.picking_id.id), ('product_id', '=', self.product_id.id)])


    @api.onchange('dummy_result_package_id')
    def onchange_dummy_result_package_id(self):
        if self.dummy_result_package_id:
            package_id = self.env['stock.quant.package'].create({'name': self.dummy_result_package_id})
            if package_id:
                self.update({
                    'result_package_id':package_id.id
                })
            else:
                self.dummy_result_package_id = False


    @api.depends('ti', 'hi', 'product_id')
    def _compute_ti_hi(self):
        for record in self:
            record.tixhi = record.ti * record.hi

    @api.onchange('product_id', 'bigger_uom_qty_done','basic_uom_qty_done','bigger_uom_id')
    def _onchange_product_id_uom(self):
        if self.product_id.uom_id:
            self.basic_uom_id = self.product_id.uom_id.id
        if self.product_id.uom_po_id:
            self.bigger_uom_id = self.product_id.uom_po_id.id
        if self.product_id and self.bigger_uom_id:
            other_uom_qty = 0.0
            if self.bigger_uom_id.uom_type == 'bigger':
                other_uom_qty = self.bigger_uom_qty_done * self.bigger_uom_id.factor_inv
            self.qty_done = other_uom_qty + self.basic_uom_qty_done
        if not self.product_id:
            self.basic_uom_id = False
            self.bigger_uom_qty_done =False
            self.basic_uom_qty_done = False
            self.qty_done = False
            self.bigger_uom_id = False

    @api.onchange('bigger_uom_qty_done')
    def _onchange_bigger_uom_qty_done(self):
        if self.bigger_uom_qty_done < 0:
            self.bigger_uom_qty_done = 0

    @api.onchange('basic_uom_qty_done')
    def _onchange_basic_uom_qty_done(self):
        if self.basic_uom_qty_done < 0:
            self.basic_uom_qty_done = 0

    @api.onchange('qty_done')
    def _onchange_qty_done(self):
        if self.qty_done < 0:
            self.qty_done = 0

    @api.model_create_multi
    def create(self, vals_list):
        # if recs and recs.picking_id.picking_type_id.sequence_code == 'INT' and recs.location_dest_id.id != 8:
        #     recs.update({'location_dest_id': 8})


        for vals in vals_list:
            if vals.get('move_id'):
                vals['company_id'] = self.env['stock.move'].browse(vals['move_id']).company_id.id
            elif vals.get('picking_id'):
                vals['company_id'] = self.env['stock.picking'].browse(vals['picking_id']).company_id.id

            # if vals.get('picking_id') and vals.get('location_dest_id'):
            #     check_int = self.env['stock.picking'].browse(vals['picking_id']).picking_type_id.sequence_code
            #     check_dest_loc = self.env['stock.location'].browse(vals['location_dest_id']).id
            #     check_stock_loc = self.env['stock.location'].search([('name','=','Stock')])
            #     if check_int == 'INT' and check_stock_loc and check_dest_loc !=check_stock_loc.id:
            #         vals['location_dest_id'] = check_stock_loc.id


        mls = super().create(vals_list)

        def create_move(move_line):
            new_move = self.env['stock.move'].create({
                'name': _('New Move:') + move_line.product_id.display_name,
                'product_id': move_line.product_id.id,
                'product_uom_qty': 0 if move_line.picking_id and move_line.picking_id.state != 'done' else move_line.qty_done,
                'product_uom': move_line.product_uom_id.id,
                'description_picking': move_line.description_picking,
                'location_id': move_line.picking_id.location_id.id,
                'location_dest_id': move_line.picking_id.location_dest_id.id,
                'picking_id': move_line.picking_id.id,
                'state': move_line.picking_id.state,
                'picking_type_id': move_line.picking_id.picking_type_id.id,
                'restrict_partner_id': move_line.picking_id.owner_id.id,
                'company_id': move_line.picking_id.company_id.id,
            })
            move_line.move_id = new_move.id

        # If the move line is directly create on the picking view.
        # If this picking is already done we should generate an
        # associated done move.
        for move_line in mls:
            if move_line.move_id or not move_line.picking_id:
                continue
            if move_line.picking_id.state != 'done':
                moves = move_line.picking_id.move_lines.filtered(lambda x: x.product_id == move_line.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    move_line.move_id = moves[0].id
                else:
                    create_move(move_line)
            else:
                create_move(move_line)

        for ml, vals in zip(mls, vals_list):
            if ml.move_id and \
                    ml.move_id.picking_id and \
                    ml.move_id.picking_id.immediate_transfer and \
                    ml.move_id.state != 'done' and \
                    'qty_done' in vals:
                ml.move_id.product_uom_qty = ml.move_id.quantity_done
            if ml.state == 'done':
                if 'qty_done' in vals:
                    ml.move_id.product_uom_qty = ml.move_id.quantity_done
                if ml.product_id.type == 'product':
                    Quant = self.env['stock.quant']
                    quantity = ml.product_uom_id._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id,
                                                                   rounding_method='HALF-UP')
                    in_date = None
                    available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity,
                                                                              lot_id=ml.lot_id,
                                                                              package_id=ml.package_id,
                                                                              owner_id=ml.owner_id)
                    if available_qty < 0 and ml.lot_id:
                        # see if we can compensate the negative quants with some untracked quants
                        untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False,
                                                                      package_id=ml.package_id, owner_id=ml.owner_id,
                                                                      strict=True)
                        if untracked_qty:
                            taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                            Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty,
                                                             lot_id=False, package_id=ml.package_id,
                                                             owner_id=ml.owner_id)
                            Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty,
                                                             lot_id=ml.lot_id, package_id=ml.package_id,
                                                             owner_id=ml.owner_id)
                    Quant._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id,
                                                     package_id=ml.result_package_id, owner_id=ml.owner_id,
                                                     in_date=in_date)
                next_moves = ml.move_id.move_dest_ids.filtered(lambda move: move.state not in ('done', 'cancel'))
                next_moves._do_unreserve()
                next_moves._action_assign()
        return mls

    @api.onchange('location_dest_id')
    def _onchange_location_dest_id(self):
        if self.picking_code == 'internal':
            records = self.env['stock.quant'].search([('location_id','=',self.location_dest_id.id)])
            if records and records.location_id.pick_face == False:
                self.location_dest_id = False
                return {'warning': {
                    'title': _("Transfer Warning"),
                    'message': _(
                        "You cannot transfer to this location !! "
                    ),
                }}
            if self.location_dest_id.hold:
                self.location_dest_id = False
                return {'warning': {
                    'title': _("Transfer Warning"),
                    'message': _(
                        "You cannot transfer to the HOLD location ! "
                    ),
                }}

    def _get_fields_stock_barcode(self):
        fields = super()._get_fields_stock_barcode()
        fields.append('picking_code')
        fields.append('tixhi')
        fields.append('dummy')
        fields.append('has_scanned_loc')
        fields.append('id')
        fields.append('expiration_date')
        fields.append('picking_sequence_code')
        fields.append('product_purchase_uom_id_factor')
        fields.append('product_purchase_uom_id_name')
        fields.append('product_check_flag')
        fields.append('is_shipto_location')
        return fields

    # def check_product(self):
    #     return
