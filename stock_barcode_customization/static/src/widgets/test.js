/** @odoo-module **/

export default class CheckBarcodeComponent extends owl.Component {
    get displayIncrementBtn() {
        return this.env.model.getDisplayIncrementBtn(this.line);
    }
}
CheckBarcodeComponent.template = 'stock_barcode_customization.CheckBarcodeComponent';