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


        if (this.qtyDemand){
            return false
        }
        return true



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

        this.trigger('delete-line', { line: this.line });
    }

})

patch(LineComponent.prototype, 'stock_barcode_line_showLoc', {
     async showLocation(prodID){
        var rpc = require('web.rpc');
        var flag;
        console.log("**** look :", prodID)
        const domain = [['pick_face', '=', true],['product_id','=',prodID.id]];
        const fields = ['complete_name','pick_face'];

        var data =await rpc.query({
            args: [domain, fields],
            method: 'search_read',
            model: 'stock.location',
        })

        return data;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_pickFaceLocationName', {
    get pickFaceLocationName() {
        var result_temp;

        var result;
        var loc_name;
        console.log("this.line :",this.line)
        var prodID = this.line.product_id
        console.log("this.line line.product_id :",prodID)
        if (this.line.picking_code == 'incoming'){
            return
        }

        else{
             result_temp = this.showLocation(prodID);
             result_temp.then(function (result) {
                    console.log("result :",result)
                    if (result.length !=0){
                        console.log("result[0].pick_face :",result[0].pick_face)
                        document.getElementById("pickFaceLocation").textContent = ' ' + result[0].complete_name;
                        document.getElementById("pickFaceLabel").textContent = 'PickFace Location :';
                    }
//                    else{
//                        document.getElementById("pickFaceLocation").textContent = ' No Pickface Location Defined for this Product';
//                    }

                });
             return "Loading..."
        }



    }

})

patch(LineComponent.prototype, 'stock_barcode_line_showPickfaceLocation', {
    showPickfaceLocation(){
        console.log("************** Show Pickface Loc")
        console.log(this.env.model.isInternalTransfer())
        this.env.model.isInternalTransfer();
    }
})

