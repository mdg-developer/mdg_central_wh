/** @odoo-module **/
import GroupedLineComponent from '@stock_barcode/components/grouped_line';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(GroupedLineComponent.prototype, 'stock_barcode_group_displayIncrementPalletBtn', {
    get displayIncrementPalletBtn() {

//        return this.env.model.getDisplayIncrementPalletBtn(this.line);
        if(this.line.picking_code == 'internal' || this.line.picking_code == 'outgoing'){
            return false
        }
        else if ( this.qtyDone >= this.qtyDemand){
            return false
        }
        else{
            return true
        }
    }
})

patch(GroupedLineComponent.prototype, 'stock_barcode_line_incrementQtyGroup', {
    get incrementQtyGroup() {

          if((this.qtyDemand - this.qtyDone) < (this.line.tixhi * this.line.dummy)){
            return (this.qtyDemand - this.qtyDone)
          }
          else{
            return (this.line.tixhi * this.line.dummy)
          }
    }
})

patch(GroupedLineComponent.prototype, 'stock_barcode_line_addPalletGroup', {
    addPalletGroup(quantity, ev) {
//        quantity = this.line.tixhi * this.line.dummy
        this.env.model.updateLinePalletQty(this.line.virtual_id, quantity);
    }
})