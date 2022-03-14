/** @odoo-module **/
import MainComponent from '@stock_barcode/components/main';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(MainComponent.prototype, 'stock_barcode_customization', {

      get sourceLocationsLength() {
            console.log("Inside sourceLocationsLength",this.env.model.locationList.length)
            if(this.env.model.locationList.length>5){
                return true
            }
            else{
                return false
            }

      }
})