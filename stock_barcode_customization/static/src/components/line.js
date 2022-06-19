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

patch(LineComponent.prototype, 'stock_barcode_line_color_customization_pick', {
    get isPicking() {
        if (this.line.picking_sequence_code == 'PICK' && this.line.qty_done && this.line.product_check_flag == 'True'){
            console.log("Inside thisss")
            return true;

        }
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_color_customization_delivery_order', {
    get isDeliveryOrder() {
        console.log("this :",this)
        console.log("this.line :",this.line)
        console.log("this.line.picking_sequence_code :",this.line.picking_sequence_code)
        console.log("this.line.qty_done :",this.line.qty_done)
        console.log("this.line.product_check_flag :",this.line.product_check_flag)
        if (this.line.picking_code == 'outgoing' && this.line.qty_done && this.line.product_check_flag == 'True'){
            console.log("Inside thisss")
            return true;

        }
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_color_customization_pickCA', {
    get isPickCA() {
       if (this.line.picking_sequence_code == 'PICKCA'){
            if(this.line.is_shipto_location == true){
                if(this.line.qty_done && this.line.product_check_flag == 'True'){
                    return true
                }
            }
            else{
                if(this.line.qty_done && this.line.product_check_flag == 'True'){
                    return true
                }
            }
       }
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_color_customization_pickL', {
    get isPickL() {
        if (this.line.picking_sequence_code == 'PICKL'){
            if(this.line.is_shipto_location == true){
                if(this.line.qty_done && this.line.product_check_flag == 'True'){
                    return true
                }
            }
            else{
                if(this.line.qty_done && this.line.has_scanned_loc == true && this.line.product_check_flag == 'True'){
                    return true
                }
            }

        }
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
        if (this.line.has_scanned_loc == true && this.line.picking_sequence_code == 'INT'){
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
        var prodID = this.line.product_id
        if (this.line.picking_code == 'incoming' || this.line.picking_code == 'outgoing' || this.line.picking_sequence_code == 'PICK'
                || this.line.picking_sequence_code == 'PICKCA' || this.line.picking_sequence_code == 'PICKL'){
            return
        }

        else{
             result_temp = this.showLocation(prodID);
             result_temp.then(function (result) {
                    if (result.length !=0){
                        document.getElementById("pickFaceLocation").textContent = ' ' + result[0].complete_name;
                        document.getElementById("pickFaceLabel").textContent = 'PickFace :';
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
        console.log("**P*******")
        console.log("this :",this)
        console.log("this.line :", this.line)
        this.env.model.isInternalTransfer();
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_incrementQtyPick', {
 get incrementQtyPick() {
        return this.qtyDemand;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_incrementQtyDelivery', {
 get incrementQtyDelivery() {
        return this.qtyDemand;
    }
})


patch(LineComponent.prototype, 'stock_barcode_line_displayIncrementBtnPick', {
get displayIncrementBtnPick() {
        return this.env.model.getDisplayIncrementBtnPick(this.line);
    }

})


patch(LineComponent.prototype, 'stock_barcode_line_displayIncrementBtnDelivery', {
get displayIncrementBtnDelivery() {
        return this.env.model.getDisplayIncrementBtnDelivery(this.line);
    }

})

patch(LineComponent.prototype, 'stock_barcode_line_showExpDate', {
    showExpDate(){
//        this.env.model.isInternalTransfer();
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_exp_date', {
 get expDate() {
        console.log("*********")
        console.log("this :",this)
        console.log("this.line :",this.line)
        if(this.line.lot_id){
            console.log("this.line.lot_id.expiration_date :",this.line.lot_id.expiration_date)
            var expiry  = this.line.lot_id.expiration_date
            var parts =expiry.split('-');
            console.log("parts :",parts)
            var exp_date = parts[2] +"/" +parts[1]+"/"+parts[0]
//            document.getElementById("expLabel").textContent = 'Exp : ';
            return "Exp: "+exp_date

        }


    }
})


patch(LineComponent.prototype, 'stock_barcode_line_caseQuantity', {
 get caseQuantity() {
        console.log("*********Case Quantity")
        console.log(this.line.product_purchase_uom_id_factor)
        console.log(this.qtyDone)
        var factor =this.line.product_purchase_uom_id_factor
        var result = this.qtyDone / factor
        console.log("result :",result)
        console.log("result :",result.toFixed(2))
        return result.toFixed(2)


    }
})

patch(LineComponent.prototype, 'stock_barcode_line_showCaseQty', {
    showCaseQty(){
        console.log("*******Show Case Qty")
        console.log("this :",this)
        if (this.line.picking_code == 'outgoing'){
            return true
        }
        else{
             return false
        }

    }
})