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
        var rpc = require('web.rpc');
        console.log("Change location customized :")
        console.log("this.pageLines before :",this.pageLines)
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



        for (const line of this.pageLines) {
            console.log("Inside main loop")
            console.log ("line :", line)
            if (line.picking_code == 'internal' && line.has_scanned_loc == false){
                console.log('inside main confition')
                line.has_scanned_loc = true
                this._markLineAsDirty(line);
            }
            console.log ("write done :", line)
        }

        this.selectedLineVirtualId = false;
        console.log("this.pageLines after :",this.pageLines)

    }

})

patch(BarcodePickingModel.prototype, 'stock_barcode_destination_location_occupied', {
    async _processLocationDestination(barcodeData) {

        if (this.record.picking_type_code === 'internal' || this.record.picking_type_code === 'incoming'){

            var rpc = require('web.rpc');
            var fields = [];
            var result =[];
            var result_length;
            result = await rpc.query({
                model: 'stock.quant',
                method: 'search_read',
                domain: [['location_id', '=', barcodeData.destLocation.id]],
            }).then(function (data) {

                result = data
                result_length = result.length

            });
             if (result_length >= 1){
                    Dialog.alert(self, _t("Your cannot transfer to this location !"), {
                                title: _t('Internal Transfer'),
                    });
             }
             else{

                this.highlightDestinationLocation = true;
                await this.changeDestinationLocation(barcodeData.destLocation.id, true);
                this.trigger('update');
                barcodeData.stopped = true;
             }
        }
        else{

            this._super(...arguments);
        }

    }
})


patch(BarcodeModel.prototype, 'stock_barcode_show_alert_validate',{
    async validate() {
        console.log("Inside Validate")
        var stop =false

        console.log("Start")
        for (const pageLines of this.pages){

            for (const line of this.pages[pageLines["index"]].lines) {
                console.log("line :",line)
                if (line.has_scanned_loc == false && line.picking_code == 'internal') {
                    console.log("iniside if condition")
                    stop = true
                    break;
                }
                if (!line.id){
                    console.log("Inside if condition 1")
                    stop = true
                    break;
                }

            }
        }
        console.log("Stop")
        console.log("stop :",stop)
        if (stop == true){

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

        const flag = this.pageLines.find(l => l.virtual_id === virtualId);
        const product = this.cache.getRecord('product.product', flag.product_id.id);
        const fieldsParams = this._convertDataToFieldsParams({
            product,
            qty: qty,
            lot_id :'',
        });

        var newLine = await this._createNewLine({fieldsParams});
        this.trigger('update')
    }

})

patch(BarcodePickingModel.prototype, 'stock_barcode_deletePalletQty', {
    async deletePalletQty(virtualId,lineId) {
        console.log("Inside deletePalletQty Function")
        var rpc = require('web.rpc');
        await rpc.query({
            model: 'stock.move.line',
            method: 'unlink',
            args: [lineId],
        })
        this.trigger('refresh')
    }

})

