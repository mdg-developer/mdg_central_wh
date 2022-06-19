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

            if (line.picking_code == 'internal' && line.has_scanned_loc == false){

                line.has_scanned_loc = true
                this._markLineAsDirty(line);
            }

        }

        this.selectedLineVirtualId = false;


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
        var rpc = require('web.rpc');
        var session = require('web.session');
        console.log("session :",session)
        var stop =false
        for (const pageLines of this.pages){

            for (const line of this.pages[pageLines["index"]].lines) {


                if (line.has_scanned_loc == false && line.picking_code == 'internal') {

                    stop = true
                    break;
                }
                if (!line.id){

                    stop = true
                    break;
                }


            }
        }

//        In the Picking ( PICK  / PICKCA / PICKL ) and Delivery order , checking product scan is mandatory
        console.log("this :",this)
        console.log("this.record :", this.record)
        if (['PICK','PICKL', 'OUT'].includes(this.record.picking_type_sequence_code)){
            for (const pageLines of this.pages){
                for (const line of this.pages[pageLines["index"]].lines) {
                    if (line.product_check_flag != 'True' ){
                        Dialog.alert(self, _t("Check Product Barcode !"), {
                        title: _t('ALERT'),
                        });
                        return
                    }
                }
            }
        }

        if (this.record.picking_type_sequence_code == 'PICKCA' && !this.record.picking_type_entire_packs){
            for (const pageLines of this.pages){
                for (const line of this.pages[pageLines["index"]].lines) {
                    if (line.product_check_flag != 'True' ){
                        Dialog.alert(self, _t("Check Product Barcode !"), {
                        title: _t('ALERT'),
                        });
                        return
                    }
                }
            }
        }



        console.log("In validate this :",this)
        console.log("this.recordIds :",this)
        console.log("PackageLines :",this.recordIds)
        if ((this.record.picking_type_code == 'internal' && this.record.location_dest_id == 11) || (this.record.picking_type_code == 'outgoing') || (this.packageLines.length != 0)) {
              console.log ("First If")
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
            for (const pageLines of this.pages){
                for (const line of this.pages[pageLines["index"]].lines) {
                    console.log("inside first for loop")
                    await rpc.query({
                        model: 'stock.move.line',
                        method: 'write',
                        args: [[line.id], {validated_by: session.partner_id}],
                    });


                }
            }

            return options.on_close();
        }

        if (stop == true){
            console.log("Inside stop true")

            Dialog.alert(self, _t("Destination location must be scanned before validating !"), {
                title: _t('Internal Transfer'),
            });

        }
        else{
        console.log("Inside else")
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
        for (const pageLines of this.pages){
            for (const line of this.pages[pageLines["index"]].lines) {
//                 console.log("Inside Update Loop")
//                 await this.updateLine(line, {validated_by: session.uid});
                console.log("inside first for loop")
                await rpc.query({
                        model: 'stock.move.line',
                        method: 'write',
                        args: [[line.id], {validated_by: session.partner_id}],
                    });


            }
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

        var rpc = require('web.rpc');
        await rpc.query({
            model: 'stock.move.line',
            method: 'unlink',
            args: [lineId],
        })
        this.trigger('refresh')
    }

})

patch(BarcodePickingModel.prototype, 'stock_barcode_isInternalTransfer', {
  get isInternalTransfer() {
        return ['internal'].includes(this.record.picking_type_code);
    }
})

