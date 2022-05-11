/** @odoo-module **/
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

    _findLinePackage(barcodeData) {
        console.log("Inside _fineLine ")
        let foundLine = false;
        const {lot, lotName, product} = barcodeData;
        const quantPackage = barcodeData.package;
        const dataLotName = lotName || (lot && lot.name) || false;

        for (const pageLines of this.pages){

            for (const line of this.pages[pageLines["index"]].lines) {

                const lineLotName = line.lot_name || (line.lot_id && line.lot_id.name) || false;
                if (line.product_id.id !== product.id) {

                    continue; // Not the same product.
                }
                if (quantPackage && (!line.package_id || line.package_id.id !== quantPackage.id)) {

                    continue; // Not the expected package.
                }
                if (dataLotName && lineLotName && dataLotName !== lineLotName && !this._canOverrideTrackingNumber(line)) {

                    continue; // Not the same lot.
                }
                if (line.product_id.tracking === 'serial') {

                    if (this.getQtyDone(line) >= 1 && lineLotName) {
                        continue; // Line tracked by serial numbers with quantity & SN.
                    } else if (dataLotName && this.getQtyDone(line) > 1) {
                        continue; // Can't add a SN on a line where multiple qty. was previously added.
                    }
                }
                if ((
                        !dataLotName || !lineLotName || dataLotName !== lineLotName
                    ) && (
                        line.qty_done && line.qty_done > line.product_uom_qty &&
                        line.virtual_id != this.selectedLine.virtual_id
                )) {

                    continue;
                }
                if (foundLine && this.getQtyDemand(line) && this.getQtyDone(line) <= this.getQtyDemand(line)) {

                    continue; // Don't take a complete line if already find another one.
                }
                if (this._lineIsNotComplete(line)) {
                    // Found a uncompleted compatible line, stop searching.

                    foundLine = line;
                    break;
                }
                // The line matches, but there could be a better candidate, so keep searching.
                foundLine = foundLine || line;
            }

        }

        return foundLine;
    }
})