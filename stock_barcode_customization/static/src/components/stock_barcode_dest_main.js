/** @odoo-module **/
console.log("Inherit load:stock_Barcode_dest_main.js");
import MainComponent from '@stock_barcode/components/main';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(MainComponent.prototype, 'stock_barcode_customization_1', {

      get destinationLocationsLength() {
            if(this.env.model.destLocationList.length>5){
                return true
            }
            else{
                return false
            }

      }

      })