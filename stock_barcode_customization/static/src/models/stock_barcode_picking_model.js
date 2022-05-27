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
        console.log("#BarcodePicking : changeDestinationLocation")
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

patch(BarcodePickingModel.prototype, 'stock_barcode_destination_location_occupied', {
    async _processLocationDestination(barcodeData) {
        console.log("######## Inherited process location destination")
        console.log("this.record.picking_type_code :",this.record.picking_type_code)
        if (this.record.picking_type_code === 'internal' || this.record.picking_type_code === 'incoming'){
            console.log("##### Inside if")
            var rpc = require('web.rpc');
            var fields = [];
            var result =[];
            var result_length;
            result = await rpc.query({
                model: 'stock.quant',
                method: 'search_read',
                domain: [['location_id', '=', barcodeData.destLocation.id]],
            }).then(function (data) {
                console.log(data);
                result = data
                result_length = result.length
                console.log("result :",result)
                console.log("result_length :",result_length)
            });
             if (result_length >= 1){
                    Dialog.alert(self, _t("Your cannot transfer to this location !"), {
                                title: _t('Internal Transfer'),
                    });
             }
             else{
                console.log("#Barocode picking:_processLocationDestination")
                this.highlightDestinationLocation = true;
                await this.changeDestinationLocation(barcodeData.destLocation.id, true);
                this.trigger('update');
                barcodeData.stopped = true;
             }
        }
        else{
            console.log("##### Inside else")
            this._super(...arguments);
        }

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
        console.log("# barcode_model:_processLocation")
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
        }
})

patch(BarcodePickingModel.prototype, 'stock_barcode_updateLinePalletQty', {
    async updateLinePalletQty(virtualId, qty = 1) {
        console.log("####Inside updateLinePalletQty")
        const flag = this.pageLines.find(l => l.virtual_id === virtualId);
        const product = this.cache.getRecord('product.product', flag.product_id.id);
        console.log("flag :",flag)
        console.log("product :",product)
        const fieldsParams = this._convertDataToFieldsParams({
            product,
            qty: qty,
            lot_id :'',
        });

        await this._createNewLine({fieldsParams});
    }

})