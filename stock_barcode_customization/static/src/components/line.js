/** @odoo-module **/
import LineComponent from '@stock_barcode/components/line';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(LineComponent.prototype, 'stock_barcode_line_color_customization', {
    get isFaulty() {
        console.log("##Line.xml :isFaulty()")
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_color_customization_1', {
    get isResultPackageId() {
        console.log("##Line.xml :isResultPackageId()")
        console.log("##Inside ResultPackageId ")
        console.log("##this.line : ",this.line)
        if (this.line.result_package_id && this.line.picking_code == 'incoming'){
            return true;

        }
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_isNotResultPackageId', {
    get isNotResultPackageId() {
        console.log("##Line.xml :isResultPackageId()")
        console.log("##Inside ResultPackageId ")
        console.log("##this.line : ",this.line)
        if (!this.line.result_package_id && this.line.picking_code == 'incoming'){
            return true;

        }
        return false;
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_displayIncrementPalletBtn', {
    get displayIncrementPalletBtn() {
            return this.env.model.getDisplayIncrementPalletBtn(this.line);
        }
})

patch(LineComponent.prototype, 'stock_barcode_line_incrementQty', {
    get incrementQty() {
          console.log("**** IncrementQty")
          console.log("this.line.tixhi * this.line.dummy",this.line.tixhi * this.line.dummy)
          console.log("this.line.tixhi :",this.line.tixhi)
          console.log("this.line.dummy :",this.line.dummy)
          return (this.line.tixhi * this.line.dummy)
    }
})

patch(LineComponent.prototype, 'stock_barcode_line_addPallet', {
    addPallet(quantity, ev) {
        quantity = this.line.tixhi * this.line.dummy
        this.env.model.updateLinePalletQty(this.line.virtual_id, quantity);
    }
})