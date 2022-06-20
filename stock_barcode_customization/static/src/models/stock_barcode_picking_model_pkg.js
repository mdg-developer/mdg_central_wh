/** @odoo-module **/
import BarcodePickingModel from '@stock_barcode/models/barcode_picking_model';
import { patch } from 'web.utils';
import core from 'web.core';
const _t = core._t;

patch(BarcodePickingModel.prototype, 'stock_barcode_customization_package', {

    async _processPackage(barcodeData) {
        console.log("Inside _processPackage")

        const { packageName } = barcodeData;
        const recPackage = barcodeData.package;
        var rpc = require('web.rpc');
        var result;
        console.log("barcodeData.packageType :",barcodeData.packageType)
        console.log("recPackage :",recPackage)
        console.log("packageName :",packageName)
        console.log("this :",this)
        console.log("this.record :",this.record)
        this.lastScannedPackage = false;
        if (barcodeData.packageType && !recPackage) {
            console.log("Inside first if")
            // Scanned a package type and no existing package: make a put in pack (forced package type).
            barcodeData.stopped = true;
            return await this._processPackageType(barcodeData);
        } else if (packageName && !recPackage) {
            console.log("Inside first else if")
            // Scanned a non-existing package: make a put in pack.
            barcodeData.stopped = true;
            return await this._putInPack({ default_name: packageName });
        } else if (!recPackage || (
            recPackage.location_id && recPackage.location_id != this.currentLocationId
        )) {
            console.log("Inside last else if")
            if(this.record.picking_type_sequence_code != 'PICK'){
                return; // No package, package's type or package's name => Nothing to do.
            }

        }
        // Scanned a package: fetches package's quant and creates a line for
        // each of them, except if the package is already scanned.
        // TODO: can check if quants already in cache to avoid to make a RPC if
        // there is all in it (or make the RPC only on missing quants).
        const res = await this.orm.call(
            'stock.quant',
            'get_stock_barcode_data_records',
            [recPackage.quant_ids]
        );
        const quants = res.records['stock.quant'];
        console.log("quants :",quants)
        if (!quants.length) { // Empty package => Assigns it to the last scanned line.

            const currentLine = this.selectedLine || this.lastScannedLine;
            if (currentLine && !currentLine.package_id && !currentLine.result_package_id) {

                const fieldsParams = this._convertDataToFieldsParams({
                    resultPackage: recPackage,
                });
                await this.updateLine(currentLine, fieldsParams);

                barcodeData.stopped = true;
                this.selectedLineVirtualId = false;
                this.lastScannedPackage = recPackage.id;

                this.trigger('update');
            }
            return;
        }
        this.cache.setCache(res.records);

        // Checks if the package is already scanned.
        let alreadyExisting = 0;
        for (const line of this.pages[this.pageIndex].lines) {

            if (line.package_id && line.package_id.id === recPackage.id &&
                this.getQtyDone(line) > 0) {
                alreadyExisting++;
            }
        }

        if (alreadyExisting === quants.length) {
            barcodeData.error = _t("This package is already scanned.");
            return;
        }
        // For each quants, creates or increments a barcode line.
        for (const quant of quants) {
            console.log("inside loop quant :")
            const product = this.cache.getRecord('product.product', quant.product_id);

            const searchLineParams = Object.assign({}, barcodeData, { product });

//            const currentLine = this._findLine(searchLineParams);
            const currentLine = await this._findLinePackage(searchLineParams);
            console.log("currentLine :",currentLine)
            if (currentLine) { // Updates an existing line.

                const fieldsParams = this._convertDataToFieldsParams({
                    qty: quant.quantity,
                    lotName: barcodeData.lotName,
                    lot: barcodeData.lot,
                    package: recPackage,
                    owner: barcodeData.owner,
                });

                await this.updateLine(currentLine, fieldsParams);
            } else { // Creates a new line.

                const fieldsParams = this._convertDataToFieldsParams({
                    product,
                    qty: quant.quantity,
                    lot: quant.lot_id,
                    package: quant.package_id,
                    resultPackage: quant.package_id,
                    owner: quant.owner_id,

                });
                var new_line = await this._createNewLine({ fieldsParams });

                if (this.isInternalTransfer && this.destLocation.display_name == 'CWHB/Stock'){

                    result = await rpc.query({
                         model: 'stock.location',
                        method: 'search',
                        args: [[['pick_face', '=', true],['product_id', '=',product.id]]],
                    });

                    new_line.location_dest_id = result[0];
                    this._markLineAsDirty(new_line);

                }
            }
        }

        barcodeData.stopped = true;
        this.selectedLineVirtualId = false;
        this.lastScannedPackage = recPackage.id;

        this.trigger('update');



    }



})