/** @odoo-module **/
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(BarcodeModel.prototype, 'stock_barcode_customization', {

    async _findLinePackage(barcodeData) {

        let foundLine = false;
        const {lot, lotName, product} = barcodeData;
        const quantPackage = barcodeData.package;
        const dataLotName = lotName || (lot && lot.name) || false;
        const currentPage = this.pages[this.pageIndex];
        let foundPage = false;

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
                    foundPage = this.pages[pageLines["index"]];

                    break;
                }
                // The line matches, but there could be a better candidate, so keep searching.
                foundLine = foundLine || line;

            }

        }
//        foundLine['currentPage']= currentPage.index;
//        foundLine['foundPage'] = foundPage.index

        if(currentPage && foundPage && currentPage.index != foundPage.index){
            await this._changePage(foundPage.index);
        }
        return foundLine;
    }

})
//Test
patch(BarcodeModel.prototype, 'stock_barcode_getDisplayIncrementBtn', {
    getDisplayIncrementBtn(line) {
        if (this.getQtyDone(line) == 0 && line.picking_code == 'incoming'){
            return true
        }
    }

})

patch(BarcodeModel.prototype, 'stock_barcode_getDisplayIncrementBtnPick', {
    getDisplayIncrementBtnPick(line) {
        if ((this.getQtyDone(line) < this.getQtyDemand(line)) && line.picking_code == 'internal'){
            return true
        }
    }

})

patch(BarcodeModel.prototype, 'stock_barcode_getDisplayIncrementBtnDelivery', {
    getDisplayIncrementBtnDelivery(line) {
        if (line.picking_code == 'outgoing' && (this.getQtyDone(line) < this.getQtyDemand(line))){
            return true
        }
    }

})



patch(BarcodeModel.prototype, 'stock_barcode_getDisplayIncrementPalletBtn', {
    getDisplayIncrementPalletBtn(line) {
        if (this.getQtyDone(line) != 0 && line.picking_code == 'incoming'){
            return true
        }
    }
})

patch(BarcodeModel.prototype, 'stock_barcode_getRecord', {
    getRecord() {
        return this.record
    }
})
