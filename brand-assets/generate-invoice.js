const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const os = require('os');

(async () => {
    // Generate output directory on Desktop for brand assets
    const desktopDir = path.join(os.homedir(), 'Desktop', 'Prompt_AI_Print_Assets');
    if (!fs.existsSync(desktopDir)) {
        fs.mkdirSync(desktopDir, { recursive: true });
    }

    // Generate output directory for Downloads
    const downloadsDir = path.join(os.homedir(), 'Downloads');

    console.log('Launching browser to render High-Res PDFs...');
    const browser = await puppeteer.launch();

    async function renderPDF(htmlFilename, outputDir, pdfFilename) {
        console.log(`Rendering ${pdfFilename}...`);
        const page = await browser.newPage();
        const fp = 'file://' + path.join(__dirname, htmlFilename);
        await page.goto(fp, { waitUntil: 'networkidle0' });

        await page.evaluateHandle('document.fonts.ready');

        await page.pdf({
            path: path.join(outputDir, pdfFilename),
            printBackground: true,
            preferCSSPageSize: true
        });
        await page.close();
    }

    // Invoice -> Downloads
    await renderPDF('invoice.html', downloadsDir, 'Prompt_AI_Solutions_Invoice_ResolvePT.pdf');

    await browser.close();
    console.log(`Success! Invoice saved to Downloads.`);
})();
