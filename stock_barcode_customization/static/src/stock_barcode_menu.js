/** @odoo-module **/

import MainMenu from "@stock_barcode/stock_barcode_menu";
import Session from 'web.session';
var core = require('web.core');
var _t = core._t;


MainMenu.include({
    events: Object.assign({}, MainMenu.prototype.events, {
          "click .button_internal_transfer": function () {
            var barcode =  "CWHB-INTERNAL"
            console.log("this:::",this)
            Session.rpc('/stock_barcode/scan_from_main_menu', { barcode }).then(result => {
                if (result.action) {
                    this.do_action(result.action);
                } else if (result.warning) {
                    this.displayNotification({ title: result.warning, type: 'danger' });
                }
            });
        },

        "click .button_delivery": function () {
            var barcode =  "CWHB-DELIVERY"
            Session.rpc('/stock_barcode/scan_from_main_menu', { barcode }).then(result => {
                if (result.action) {
                    this.do_action(result.action);
                } else if (result.warning) {
                    this.displayNotification({ title: result.warning, type: 'danger' });
                }
            });
        },

        "click .button_replenishment": function () {
            this.do_action({
                type: 'ir.actions.act_window',
                name: _t('Replenishment'),
                res_model: 'stock.warehouse.orderpoint',
                views: [[false, 'kanban']],
                view_mode: "kanban",
                target: 'current',
            });
        },


    }),
});
