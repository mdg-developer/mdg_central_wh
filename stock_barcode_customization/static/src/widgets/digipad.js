/** @odoo-module **/

import widgetRegistry from 'web.widget_registry';
import Widget from 'web.Widget';

const
Digipad = Widget.extend({
    template: 'stock_barcode.DigipadTemplate',
    events: {
        'click .o_digipad_button': '_onCLickButton',
        'click .o_packaging_button': '_onCLickButtonPackage',
    },
    buttons: [
        '7', '8', '9',
        '4', '5', '6',
        '1', '2', '3',
        '.', '0', 'erase',
    ],

    /**
     * @override
     */
    init: function (parent, data, options) {
        this._super(...arguments);
        this.parent = parent;
        this.dataPointID = data.id;
        this.viewType = data.viewType;
        this.quantityField = options.attrs.quantity_field;
        this.packages = [];
    },

    /**
     * @override
     */
    willStart: function () {
        return Promise.all([
            this._super(...arguments),
            this._setSpecialButtons(),
            this._defineDisplayUOM(),
        ]);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Copies the input value if digipad value is not set yet, or overrides it if there is a
     * difference between the two values (in case user has manualy edited the input value).
     * @private
     */
    _checkInputValue: function () {
        const quantityField = document.querySelector(`input[name="${this.quantityField}"]`);
        const inputValue = quantityField.value;
        if (Number(this.value) != Number(inputValue)) {
            this.value = inputValue;
        }
    },

     _checkInputValuePackage: function () {
        const quantityField = document.querySelector(`input[name="${this.quantityField}"]`);
        const inputValue = quantityField.value;
        if (Number(this.value) != Number(inputValue)) {
            this.value = inputValue;

        }
        const productField = document.querySelector("span[name='dummy_product_pallet']");
        const resultValue = productField.innerHTML;
//        resultValue =await this._rpc({
//                        model: 'product.product',
//                        method: 'search_read',
//                        domain: [
//                            ['name', '=', productName],
//                        ],
//                        fields: ['ti_x_hi'],
//                        limit: 1,
//                    }).then(function (result) {
//                        console.log("result :",result[0].ti_x_hi)
//                        resultValue = result[0].ti_x_hi;
//                        console.log("resultValue ##:",resultValue)
//                        return resolve(resultValue);
//                    })

        return resultValue


    },

    /**
     * Defines if the UoM must be displayed in the buttons.
     *
     * @private
     * @returns {Promise}
     */
    _defineDisplayUOM: async function () {
        this.display_uom = await this.getSession().user_has_group('uom.group_uom');
    },

    /**
     * Increments the field value by the interval amount (1 by default).
     *
     * @private
     * @param {integer} [interval=1]
     */
    _increment: function (interval=1) {
        console.log("Inside increment function")
        const numberValue = Number(this.value || 0);
        console.log("numberValue :",numberValue)
        console.log("interval :",interval)
        this.value = String(numberValue + interval);
        console.log("this.value :",this.value)
    },

    /**
     * Notifies changes on the field to mark the record as dirty.
     *
     * @private
     */
    _notifyChanges: function () {
        const { dataPointID, viewType } = this;
        const changes = { [this.quantityField]: Number(this.value.replace(',', '.')) };
        this.trigger_up('field_changed', { dataPointID, changes, viewType });
    },

    /**
     * Defines the special buttons (+1, -1 and + packagings' quantity if relevant).
     *
     * @returns {Promise}
     */
    _setSpecialButtons: function () {
         console.log("Shittttt 2#")
        this.specialButtons = ['increase', 'decrease'];
        const record = this.parent.state.data;
        const demandQty = record.product_uom_qty;
        console.log("demandQty :",demandQty)
        const domain = [['product_id', '=', record.product_id.res_id]];
        if (demandQty) { // Doesn't fetch packaging with a too high quantity.
            domain.push(['qty', '<=', demandQty]);
        }
        return this._rpc({
            model: 'product.packaging',
            method: 'search_read',
            kwargs: {
                domain,
                fields: ['name', 'product_uom_id', 'qty'],
                limit: 3,
            },
        }).then(res => {
            console.log("...res :", ...res)
            this.specialButtons.push(...res);
            console.log("this.specialButtons :",this.specialButtonsdisplay_uom)
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Handles the click on one of the digipad's button and updates the value by
     * calling the method according to the pressed button.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onCLickButton: function (ev) {
        ev.preventDefault();
        this._checkInputValue();
        const buttonValue = ev.currentTarget.dataset.button;
        if (buttonValue === 'erase') {
            this.value = this.value.substr(0, this.value.length - 1);
        } else if (buttonValue === 'increase') {
            this._increment();
        } else if (buttonValue === 'decrease') {
            this._increment(-1);
        } else {
            if (buttonValue === '.' && this.value.indexOf('.') != -1) {
                // Avoids to add a decimal separator multiple time.
                return;
            }
            this.value += buttonValue;
        }
        this._notifyChanges();
    },

    /**
     * Handles the click on product's packaging buttons and increases the
     * quantity by this product packaging quantity.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onCLickButtonPackage: async function (ev) {
        var result;
        result = this._checkInputValuePackage();
        console.log("this.result ## :",result);
        this._increment(Number(result));
        this._notifyChanges();
//        ev.preventDefault();
//        this._checkInputValue();
//        console.log("Number(ev.currentTarget.dataset.qty) :",Number(ev.currentTarget.dataset.qty))
//        this._increment(Number(ev.currentTarget.dataset.qty));
//        this._increment(Number(result));
//        this._notifyChanges();
    },
});

widgetRegistry.add('digipad', Digipad);
export default Digipad;
