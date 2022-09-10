/** @odoo-module **/
console.log("AAAAAAAAAAAAAAAAAAAAAa")
import LazyBarcodeCache from '@stock_barcode/lazy_barcode_cache';

import {patch} from 'web.utils';

patch(LazyBarcodeCache.prototype, 'product_multiple_barcodes/static/src/lazy_barcode_cache.js',{

    _getBarcodeField(model) {
        if (model == 'product.barcode.multi'){
            return 'name';
        }
        if (!this.barcodeFieldByModel.hasOwnProperty(model)) {
            return null;
        }
        return this.barcodeFieldByModel[model];
    }
});
