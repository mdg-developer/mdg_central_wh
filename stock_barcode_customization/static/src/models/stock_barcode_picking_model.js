/** @odoo-module **/
import BarcodePickingModel from '@stock_barcode/models/barcode_picking_model';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(BarcodePickingModel.prototype, 'stock_barcode_customization', {
    async changeDestinationLocation(id, moveScannedLineOnly) {
        console.log("In Barcode Picking Model : in line 36")
        console.log("id",id)
        console.log("moveScannedLineOnly",moveScannedLineOnly)
        console.log("previousScannedLines",this.previousScannedLines)
        this.currentDestLocationId = id;
        if (moveScannedLineOnly && this.previousScannedLines.length) {
            this.currentDestLocationId = id;
            for (const line of this.previousScannedLines) {
                line.location_dest_id = id;
                this._markLineAsDirty(line);
            }
        } else {
            // If the button was used to change the location, if will change the
            // destination location of all the page's move lines.
            for (const line of this.pageLines) {
                line.location_dest_id = id;
                this._markLineAsDirty(line);
            }
        }
        // Forget what lines have been scanned.
        this.scannedLinesVirtualId = [];
        this.lastScannedPackage = false;

        await this.save();
        this._groupLinesByPage(this.currentState);
        for (let i = 0; i < this.pages.length; i++) {
            const page = this.pages[i];
            if (page.sourceLocationId === this.currentLocationId &&
                page.destinationLocationId === this.currentDestLocationId) {
                this.pageIndex = i;
                break;
            }
        }
        this.selectedLineVirtualId = false;
    }


})