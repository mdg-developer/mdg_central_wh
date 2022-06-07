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
        console.log("_onDeleteLine")
        let line = ev.detail.line;
        console.log('line :',line)
        const virtualId = line.virtual_id;
        console.log('virtualID :',virtualId)
        await this.env.model.save();
        console.log("line :",line)

        // Updates the line id if it's missing, in order to open the line form view.
        if (!line.id && virtualId) {
            console.log("delete main :")
            console.log("this.env.model.pageLines :",this.env.model.pageLines)
            line = this.env.model.pageLines.find(l => Number(l.dummy_id) === virtualId);
        }
        console.log("line after :",line)
        this.env.model.deletePalletQty(virtualId,line.id);
    }
})

patch(MainComponent.prototype, 'stock_barcode_main_find_id', {
    async _onFineID(ev) {
        console.log("_onFineID")
        let line = ev.detail.line;
        console.log('line :',line)
        const virtualId = line.virtual_id;
        console.log('virtualID :',virtualId)
        await this.env.model.save();
        console.log("line :",line)

        // Updates the line id if it's missing, in order to open the line form view.
        if (!line.id && virtualId) {
            console.log("delete main :")
            console.log("this.env.model.pageLines :",this.env.model.pageLines)
            line = this.env.model.pageLines.find(l => Number(l.dummy_id) === virtualId);
        }
        console.log("line :",line)
        return line.id
    }
})
