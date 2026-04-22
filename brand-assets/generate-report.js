const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function generateReport() {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();

    const reportPath = path.join(__dirname, 'joes-report.html');
    await page.goto(`file:${reportPath}`, { waitUntil: 'networkidle0' });

    // Export path in Downloads
    const downloadDir = path.join(require('os').homedir(), 'Downloads');
    const pdfPath = path.join(downloadDir, 'Joes_Salmon_Lodge_Modernization_Report.pdf');

    await page.pdf({
        path: pdfPath,
        format: 'Letter',
        printBackground: true,
    });

    console.log(`Generated report at: ${pdfPath}`);

    await browser.close();
}

generateReport().catch(console.error);
