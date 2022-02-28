/** @odoo-module **/
console.log("Inherit load");
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { patch } from 'web.utils';
import Dialog from 'web.Dialog';
import core from 'web.core';
const _t = core._t;

patch(BarcodeModel.prototype, 'report_customization', {

    async changeSourceLocation(id, applyChangeToPageLines = false) {
        console.log("In barcode_model js in changeSourceLocation function")
        if (this.record.picking_type_code === 'internal'){
            Dialog.alert(self, _t("Destination location must be scanned before validating !"), {
                    title: _t('Internal Transfer'),
                });

        }
        this.scannedLinesVirtualId = [];
        // For the pickings, changes the location will change the source
        // location of all the page's move lines.
        if (applyChangeToPageLines) {
            const moveLines = this.pageLines;
            for (const moveLine of moveLines) {
                moveLine.location_id = id;
                this._markLineAsDirty(moveLine);
            }
            this._groupLinesByPage(this.currentState);
        }
        this.currentLocationId = id;
        let pageFound = false;
        let emptyPage = false;
        const currentPage = this.pages[this.pageIndex];
        // We take either the current dest. location (if we move barcode line),
        // either the default dest. location (if we just want to create/change
        // page without move lines) to use while searching for an existing page.
        const refDestLocationId = applyChangeToPageLines ? this.currentDestLocationId : this._defaultDestLocationId();
        // If the scanned location is the current want, keep it.
        if (currentPage && this.currentLocationId === currentPage.sourceLocationId) {
            pageFound = currentPage;
        } else { // Otherwise, searches for a page with these src./dest. locations.
            for (let i = 0; i < this.pages.length; i++) {
                const page = this.pages[i];
                if (page.sourceLocationId === this.currentLocationId &&
                    page.destinationLocationId === refDestLocationId) {
                    this.pageIndex = i;
                    pageFound = page;
                    break;
                }
                if (page.lines.length === 0) {
                    emptyPage = page;
                }
            }
        }
        // Resets highlighting.
        this.selectedLineVirtualId = false;
        this.highlightDestinationLocation = false;
        await this.save();
        if (pageFound) {
            await this._changePage(pageFound.index);
        } else {
            if (emptyPage) {
                // If no matching page was found but an empty page was, reuses it.
                emptyPage.sourceLocationId = this.currentLocationId;
                emptyPage.destinationLocationId = this._defaultDestLocationId();
                pageFound = emptyPage;
            } else {
                // Otherwise, creates a new one.
                pageFound = {
                    index: this.pages.length,
                    lines: [],
                    sourceLocationId: this.currentLocationId,
                    destinationLocationId: this._defaultDestLocationId(),
                };
                this.pages.push(pageFound);
            }
            await this._changePage(pageFound.index);
        }
    }

})
