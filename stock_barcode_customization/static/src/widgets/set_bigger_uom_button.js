/** @odoo-module **/

import widgetRegistry from 'web.widget_registry';
import Widget from 'web.Widget';

const SetBiggerUomButton = Widget.extend({
    template: 'stock_barcode_customization.SetBiggerUomTemplate',
    events: { click: '_onClickButton' },

    /**
     * @override
     */
    init: function (parent, data, options) {
        this._super(...arguments);
        this.parent = parent;
        this.dataPointID = data.id;
        this.viewType = data.viewType;
        this.record = this.parent.state.data;
        this.qty = this.record.product_uom_qty;
        const uom = this.record.product_purchase_uom_id;
        this.uom = uom && uom.data.display_name;
    },

    /**
     * @override
     */
    willStart: function () {
        this.display_uom = this.getSession().user_has_group('uom.group_uom');
        return Promise.all([
            this._super(...arguments),
            this.display_uom,
        ]);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    _onClickButton: function (ev) {
        ev.preventDefault();
        const { dataPointID, viewType } = this;
        const changes = { qty_done: this.qty };
        this.trigger_up('field_changed', { dataPointID, changes, viewType });
    },
});

widgetRegistry.add('set_bigger_uom_button', SetBiggerUomButton);
export default SetBiggerUomButton;
