/** @odoo-module **/
import MainComponent from '@stock_barcode/components/main';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(MainComponent.prototype, 'stock_barcode_main_mounted', {
    mounted(){
        this._super(...arguments);
        this.el.addEventListener('delete-line', this._onDeleteLine.bind(this));
        this.el.addEventListener('find-id', this._onFineID.bind(this));
    }
})


patch(MainComponent.prototype, 'stock_barcode_main_delete', {
    async _onDeleteLine(ev) {
        let line = ev.detail.line;
        const virtualId = line.virtual_id;
        await this.env.model.save();

        // Updates the line id if it's missing, in order to open the line form view.
        if (!line.id && virtualId) {
            line = this.env.model.pageLines.find(l => Number(l.dummy_id) === virtualId);
        }
        this.env.model.deletePalletQty(virtualId,line.id);
    }
})

patch(MainComponent.prototype, 'stock_barcode_main_find_id', {
    async _onFineID(ev) {
        let line = ev.detail.line;
        const virtualId = line.virtual_id;
        await this.env.model.save();

        // Updates the line id if it's missing, in order to open the line form view.
        if (!line.id && virtualId) {
            line = this.env.model.pageLines.find(l => Number(l.dummy_id) === virtualId);
        }
        return line.id
    }
})

patch(MainComponent.prototype, 'stock_barcode_main_showAddProduct', {
get displayAddProduct() {
        console.log("pick_type_code :",this.env.model.name)
        var pick_type_code = this.env.model.name
        if(pick_type_code.includes('PICK') || pick_type_code.includes('OUT')){
            console.log("inside if")
            return false
        }
        console.log("outside if")
        return true
    }
})