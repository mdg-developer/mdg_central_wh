/** @odoo-module **/
import BarcodePickingModel from '@stock_barcode/models/barcode_picking_model';
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;
import Dialog from 'web.Dialog';
import { Mutex } from "@web/core/utils/concurrency";
import LazyBarcodeCache from '@stock_barcode/lazy_barcode_cache';
import BarcodeParser from 'barcodes.BarcodeParser';
import { useService } from "@web/core/utils/hooks";
import { sprintf } from '@web/core/utils/strings';

patch(BarcodePickingModel.prototype, 'stock_barcode_customization', {
    async changeDestinationLocation(id, moveScannedLineOnly) {
        this.currentDestLocationId = id;
        if (moveScannedLineOnly && this.previousScannedLines.length) {
            this.currentDestLocationId = id;
            if (this.previousScannedLines.length != 1){
                this.lastScannedLine.location_dest_id = id;
                this._markLineAsDirty(this.lastScannedLine);
            }
            else{
                for (const line of this.previousScannedLines) {
                    line.location_dest_id = id;
                    this._markLineAsDirty(line);
                }

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

patch(BarcodeModel.prototype, 'stock_barcode_show_alert_validate',{
    async validate() {
        console.log ("Inside Button Validate ")
        console.log ("Before if statement : this.scanDestinationLocation Value :", this.scanDestinationLocation)
        console.log("this.record.picking_type_code ###:",this.record.picking_type_code)
        if (this.scanDestinationLocation == false && this.record.picking_type_code == 'internal'){
            console.log ("Inside true true")
            Dialog.alert(self, _t("Destination location must be scanned before validating !"), {
                title: _t('Internal Transfer'),
            });

        }
        else{
            await this.save();
            const action = await this.orm.call(
                this.params.model,
                this.validateMethod,
                [this.recordIds]
            );
            const options = {
                on_close: ev => {
                    if (ev === undefined) {
                        // If all is OK, displays a notification and goes back to the previous page.
                        this.notification.add(this.validateMessage, { type: 'success' });
                        this.trigger('history-back');
                    }
                },
            };
            if (action && action.res_model) {
                return this.trigger('do-action', { action, options });
            }
            return options.on_close();
        }
    }

})

patch(BarcodeModel.prototype, 'stock_barcode_process_location',{
    async _processLocation(barcodeData) {
        if (barcodeData.location) {
            await this._processLocationSource(barcodeData);
            this.trigger('update');
        }
        this.scanDestinationLocation = true;
        console.log("processLocation function: this.scanDestinationLocation",this.scanDestinationLocation)
    }
})

patch(BarcodeModel.prototype, 'stock_barcode_setup',{
    setData(data) {
            this._super(...arguments);
            this.scanDestinationLocation = false;
            if (this.record.picking_type_code === 'internal'){
                Dialog.alert(self, _t("Destination location must be scanned before validating !"), {
                        title: _t('Internal Transfer'),
                    });

            }

        }
})