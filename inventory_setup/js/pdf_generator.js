const pdfGenerator = {
    generate: async function (products) {
        const { PDFDocument, rgb, StandardFonts } = PDFLib;

        // Create a new PDFDocument
        const pdfDoc = await PDFDocument.create();
        const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
        const fontBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

        // --- 1. Embed Database (JSON) ---
        const cleanProducts = products.map(p => ({
            id: p.id,
            barcode: p.barcode,
            name: p.name,
            price: p.price,
            qty: p.qty,
            image_filename: p.image ? `img_${p.barcode}.jpg` : null
        }));

        const jsonContent = JSON.stringify(cleanProducts, null, 2);
        // Explicitly encode to UTF-8 bytes to avoid encoding issues
        const encoder = new TextEncoder();
        const jsonBytes = encoder.encode(jsonContent);

        await pdfDoc.attach(jsonBytes, 'inventory_db.json', {
            mimeType: 'application/json',
            description: 'Database of products',
            creationDate: new Date(),
            modificationDate: new Date(),
        });

        // --- 2. Embed Images ---
        for (const p of products) {
            if (p.image) {
                const base64Data = p.image.split(',')[1];
                const imageBytes = Uint8Array.from(atob(base64Data), c => c.charCodeAt(0));

                await pdfDoc.attach(imageBytes, `img_${p.barcode}.jpg`, {
                    mimeType: 'image/jpeg',
                    description: `Photo of ${p.name}`,
                    creationDate: new Date(),
                    modificationDate: new Date(),
                });
            }
        }

        // --- 3. Generate Labels ---
        const PAGE_WIDTH = 612;
        const PAGE_HEIGHT = 792;

        // Grid Config (4 cols x 10 rows)
        const MARGIN_X = 15;
        const MARGIN_Y = 36;
        const COLS = 4;
        const ROWS = 10;
        const COL_WIDTH = (PAGE_WIDTH - (2 * MARGIN_X)) / COLS;
        const ROW_HEIGHT = (PAGE_HEIGHT - (2 * MARGIN_Y)) / ROWS;

        let page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
        let col = 0;
        let row = 0;

        // Flatten list based on quantity
        const labelsToPrint = [];
        products.forEach(p => {
            for (let i = 0; i < p.qty; i++) {
                labelsToPrint.push(p);
            }
        });

        const barcodeCache = {};

        for (const p of labelsToPrint) {
            // Check page overflow
            if (row >= ROWS) {
                page = pdfDoc.addPage([PAGE_WIDTH, PAGE_HEIGHT]);
                row = 0;
                col = 0;
            }

            const x = MARGIN_X + (col * COL_WIDTH);
            const y = PAGE_HEIGHT - MARGIN_Y - ((row + 1) * ROW_HEIGHT);

            // Draw Dotted Border for Cutting
            page.drawRectangle({
                x: x,
                y: y,
                width: COL_WIDTH,
                height: ROW_HEIGHT,
                borderWidth: 1,
                borderColor: rgb(0.6, 0.6, 0.6),
                borderDashArray: [4, 4], // Dotted/Dashed pattern
            });

            // Draw Label Content

            // 0. Legend "YAELI'S"
            const legendText = "YAELI'S";
            const legendFontSize = 6;
            const legendWidth = fontBold.widthOfTextAtSize(legendText, legendFontSize);
            page.drawText(legendText, {
                x: x + (COL_WIDTH - legendWidth) / 2,
                y: y + ROW_HEIGHT - 8,
                size: legendFontSize,
                font: fontBold,
                color: rgb(0, 0, 0),
            });

            // 1. Name (Truncated if too long)
            const fontSize = 8;
            let text = p.name.toUpperCase();
            text = text.length > 20 ? text.substring(0, 20) + '...' : text;

            const textWidthName = fontBold.widthOfTextAtSize(text, fontSize);
            const nameX = x + (COL_WIDTH - textWidthName) / 2;

            page.drawText(text, {
                x: nameX,
                y: y + ROW_HEIGHT - 18, // Moved down slightly
                size: fontSize,
                font: fontBold,
                color: rgb(0, 0, 0),
            });

            // 2. Barcode
            let barcodeImage = barcodeCache[p.barcode];
            if (!barcodeImage) {
                barcodeImage = await this.generateBarcodeImage(p.barcode, pdfDoc);
                barcodeCache[p.barcode] = barcodeImage;
            }

            if (barcodeImage) {
                const bcDims = barcodeImage.scale(0.4);
                const bcX = x + (COL_WIDTH - bcDims.width) / 2;
                page.drawImage(barcodeImage, {
                    x: bcX,
                    y: y + 20, // Moved up to make room for price
                    width: bcDims.width,
                    height: bcDims.height,
                });
            }

            // 3. Barcode Text (Human Readable)
            const codeText = p.barcode;
            const textWidth = font.widthOfTextAtSize(codeText, 7);
            page.drawText(codeText, {
                x: x + (COL_WIDTH - textWidth) / 2,
                y: y + 11,
                size: 7,
                font: font,
                color: rgb(0, 0, 0),
            });

            // 4. Price
            const priceVal = parseFloat(p.price) || 0;
            const priceText = `$${priceVal.toFixed(2)}`;
            const priceWidth = fontBold.widthOfTextAtSize(priceText, 9);
            page.drawText(priceText, {
                x: x + (COL_WIDTH - priceWidth) / 2,
                y: y + 2,
                size: 9,
                font: fontBold,
                color: rgb(0, 0, 0),
            });

            // Advance Grid
            col++;
            if (col >= COLS) {
                col = 0;
                row++;
            }
        }

        // --- 4. Save and Download ---
        const pdfBytes = await pdfDoc.save();
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);

        // Download
        const link = document.createElement('a');
        link.href = url;
        link.download = 'etiquetas_inventario.pdf';
        link.click();

        // Auto-open (Attempt)
        setTimeout(() => {
            window.open(url, '_blank');
        }, 500);
    },

    generateBarcodeImage: async function (text, pdfDoc) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            try {
                bwipjs.toCanvas(canvas, {
                    bcid: 'code128',       // Barcode type
                    text: text,            // Text to encode
                    scale: 3,               // 3x scaling factor
                    height: 10,              // Bar height, in millimeters
                    includetext: false,            // Show human-readable text
                    textxalign: 'center',        // Always good to set this
                });

                const dataUrl = canvas.toDataURL('image/png');
                const base64Data = dataUrl.split(',')[1];
                const imageBytes = Uint8Array.from(atob(base64Data), c => c.charCodeAt(0));

                pdfDoc.embedPng(imageBytes).then(resolve);

            } catch (e) {
                console.error("Error generating barcode:", e);
                resolve(null);
            }
        });
    }
};
