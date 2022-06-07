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

patch(LineComponent.prototype, 'stock_barcode_line_displayDeleteButton', {
    get displayDeleteButton(){

        console.log("############ Now this")
        console.log("this :",this)
        console.log("this.line :",this.line)
        if (this.qtyDemand){
            return false
        }
        else if (this.line.picking_code == 'incoming' && !this.line.qtyDemand){
            console.log("inside if condition")
            return true
        }else{
            return false
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

patch(LineComponent.prototype, 'stock_barcode_line_delete', {
    delete() {
        console.log("line.js > delete this.line :",this.line)
        this.trigger('delete-line', { line: this.line });
    }

})