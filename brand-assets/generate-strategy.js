const puppeteer = require('puppeteer');
const path = require('path');

async function generateReport() {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();

    const reportPath = path.join(__dirname, 'joes-growth-strategy.html');
    await page.goto(`file:${reportPath}`, { waitUntil: 'networkidle0' });

    // Export path in Downloads
    const downloadDir = path.join(require('os').homedir(), 'Downloads');
    const pdfPath = path.join(downloadDir, 'Joes_Salmon_Lodge_Growth_Strategy.pdf');

    await page.pdf({
        path: pdfPath,
        format: 'Letter',
        printBackground: true,
    });

    console.log(`Generated strategy document at: ${pdfPath}`);

    await browser.close();
}

generateReport().catch(console.error);
