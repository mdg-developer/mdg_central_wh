/** @odoo-module **/
import LineComponent from '@stock_barcode/components/line';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(LineComponent.prototype, 'stock_barcode_line_color_customization', {
    get isFaulty() {
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_color_customization_1', {
    get isResultPackageId() {
        if (this.line.result_package_id && this.line.picking_code == 'incoming'){
            return true;

        }
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_isNotResultPackageId', {
    get isNotResultPackageId() {
        if (!this.line.result_package_id && this.line.picking_code == 'incoming'){
            return true;

        }
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_hasScannedDestinationLocation', {
    get hasScannedDestinationLocation() {
        if (this.line.has_scanned_loc == true && this.line.picking_code == 'internal'){
            return true;

        }
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_displayIncrementPalletBtn', {
    get displayIncrementPalletBtn() {
//        console.log("this.qtyDemand :",this.qtyDemand)
//        console.log("this.qtyDone :",this.qtyDone)
//        console.log("this :",this)
//        return this.env.model.getDisplayIncrementPalletBtn(this.line);

        var pallet = this.line.tixhi * this.line.dummy
        if(this.line.picking_code != 'incoming'){
            return false
        }
        if (!this.qtyDemand){
            return false
        }
        else if (this.qtyDone == 0){
            return false
        }
        else{
            return true
        }
        }
})

patch(LineComponent.prototype, 'stock_barcode_line_incrementQty', {
    get incrementQty() {
          return (this.line.tixhi * this.line.dummy)
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_incrementQtyPallet', {
    get incrementQtyPallet() {
          console.log("### incrementQtyPallet")
          console.log("this :",this)
          console.log("this.qtyDemand :",this.qtyDemand)
          console.log("this.qtyDone :",this.qtyDone)
          console.log("this.line.tixhi * this.line.dummy :",this.line.tixhi * this.line.dummy)
          console.log("this.qtyDemand - this.qtyDone :",this.qtyDemand - this.qtyDone)
          if ((this.qtyDemand - this.qtyDone) < (this.line.tixhi * this.line.dummy)){
            return (this.qtyDemand - this.qtyDone)
          }
          else{
            return (this.line.tixhi * this.line.dummy)
          }

    }
})

patch(LineComponent.prototype, 'stock_barcode_line_addPallet', {
    addPallet(quantity, ev) {
//        quantity = this.line.tixhi * this.line.dummy
        this.env.model.updateLinePalletQty(this.line.virtual_id, quantity);
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_deletePallet', {
     deletePallet() {
//        var rpc = require('web.rpc');
        console.log("deletePallet inside line.js")
        console.log("this.line :",this.line)
        console.log("this.line :",this.id)
        console.log("##### :",this.line.id)
//        await rpc.query({
//            model: 'stock.move.line',
//            method: 'unlink',
//            args: [this.line.id],
//        })
//        .then(function () {
//            window.location.reload();
//        });
        this.env.model.deletePalletQty(this.line.virtual_id,this.line.id);


    }
})