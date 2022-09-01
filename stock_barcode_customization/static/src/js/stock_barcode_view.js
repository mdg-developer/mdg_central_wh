console.log("Inside odoo 15.0+e:")

odoo.define('stock_barcode_customization.button_int', function (require) {
"use strict";

var rpc = require('web.rpc');
var session = require('web.session');
var core = require('web.core');
var _t = core._t;
//const { useService } = require("@web/core/utils/hooks");
//const { doAction } = useService("action");
const { createWebClient, doAction } = require('@web/../tests/webclient/helpers');


$(document).on('click', '#button_click', function(){

    console.log("test")
    console.log("this",this)
    console.log("self",self)
    var barcode =  "CWHB-INTERNAL"
    session.rpc('/stock_barcode/scan_from_main_menu', { barcode }).then(result => {
        if (result.action) {
            do_action(result.action);
        } else if (result.warning) {
            this.displayNotification({ title: result.warning, type: 'danger' });
        }
    });
 });
});