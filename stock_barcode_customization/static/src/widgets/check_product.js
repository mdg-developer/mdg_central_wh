/** @odoo-module **/

import widgetRegistry from 'web.widget_registry';
import Widget from 'web.Widget';

const
ProductCheck = Widget.extend({
    template: 'stock_barcode_customization.CheckBarcodeComponent',
    events: {
        'click .o_digipad_button': '_onCLickButton',

    },
    init: function (parent, data, options) {
        console.log("ProductCheck : init function")
        this._super(...arguments);
        this.parent = parent;
        this.dataPointID = data.id;
        this.viewType = data.viewType;
        this.productField = options.attrs.product_field;
        this.packages = [];
    },

    _onCLickButton: function (ev) {
        ev.preventDefault();
        console.log("Dan Tan Tan Tan")
    },

})

widgetRegistry.add('productcheck', ProductCheck);
export default ProductCheck;
