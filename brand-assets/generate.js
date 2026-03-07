const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const os = require('os');

(async () => {
    // Generate output directory on Desktop
    const desktopDir = path.join(os.homedir(), 'Desktop', 'Prompt_AI_Print_Assets');
    if (!fs.existsSync(desktopDir)) {
        fs.mkdirSync(desktopDir, { recursive: true });
    }

    console.log('Launching browser to render High-Res PDFs...');
    const browser = await puppeteer.launch();

    async function renderPDF(htmlFilename, pdfFilename) {
        console.log(`Rendering ${pdfFilename}...`);
        const page = await browser.newPage();
        const fp = 'file://' + path.join(__dirname, htmlFilename);
        await page.goto(fp, { waitUntil: 'networkidle0' });

        await page.evaluateHandle('document.fonts.ready');

        await page.pdf({
            path: path.join(desktopDir, pdfFilename),
            printBackground: true,
            preferCSSPageSize: true
        });
        await page.close();
    }

    // Original Brand Assets
    await renderPDF('business-cards.html', 'Prompt_AI_Business_Cards_Print_Ready.pdf');
    await renderPDF('letterhead.html', 'Prompt_AI_Letterhead_Print_Ready.pdf');

    // Teaching Brand Assets
    await renderPDF('business-cards-teaching.html', 'Andy_McAteer_Teaching_Business_Cards_Print_Ready.pdf');
    await renderPDF('letterhead-teaching.html', 'Andy_McAteer_Teaching_Letterhead_Print_Ready.pdf');

    await browser.close();
    console.log(`Success! Print-ready files saved to: ${desktopDir}`);
})();
