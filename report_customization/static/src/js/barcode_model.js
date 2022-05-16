/** @odoo-module **/

import BarcodeModel from '@stock_barcode/models/barcode_model';
import LazyBarcodeCache from '@stock_barcode/lazy_barcode_cache';
import BarcodeParser from 'barcodes.BarcodeParser';
import { patch } from 'web.utils';
import Dialog from 'web.Dialog';
import core from 'web.core';
const _t = core._t;
import { useService } from "@web/core/utils/hooks";
import { Mutex } from "@web/core/utils/concurrency";

patch(BarcodeModel.prototype, 'report_customization', {

    setData(data) {
            this._super(...arguments);
            if (this.record.picking_type_code === 'internal'){
                Dialog.alert(self, _t("Destination location must be scanned before validating !"), {
                        title: _t('Internal Transfer'),
                    });

            }
        }


})
