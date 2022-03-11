/** @odoo-module **/
console.log("Inherit load:stock_barcode_model.js");
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(BarcodeModel.prototype, 'stock_barcode_customization', {

      async updateLine(line, args) {
        let {lot_id, owner_id, package_id} = args;
        if (!line) {
            throw new Error('No line found');
        }
        if (!line.product_id && args.product_id) {
            line.product_id = args.product_id;
            line.product_uom_id = this.cache.getRecord('uom.uom', args.product_id.uom_id);
           //added
            line.product_purchase_uom_id = this.cache.getRecord('uom.uom', args.product_id.uom_po_id);
        }
        if (lot_id) {
            if (typeof lot_id === 'number') {
                lot_id = this.cache.getRecord('stock.production.lot', args.lot_id);
            }
            line.lot_id = lot_id;
        }
        if (owner_id) {
            if (typeof owner_id === 'number') {
                owner_id = this.cache.getRecord('res.partner', args.owner_id);
            }
            line.owner_id = owner_id;
        }
        if (package_id) {
            if (typeof package_id === 'number') {
                package_id = this.cache.getRecord('stock.quant.package', args.package_id);
            }
            line.package_id = package_id;
        }
        if (args.lot_name) {
            await this.updateLotName(line, args.lot_name);
        }
        this._updateLineQty(line, args);
        this._markLineAsDirty(line);
    }
})