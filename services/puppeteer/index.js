const express = require('express');
const bodyParser = require('body-parser');
const puppeteer = require('puppeteer');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

app.post('/scrape', async (req, res) => {
  const { url } = req.body;

  if (!url) {
    return res.status(400).json({ error: 'URL is required' });
  }

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
      ],
    });

    const page = await browser.newPage();

    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 180000
    });

    const hasIframe = await page.$('iframe#innerWrap');

    if (hasIframe) {
      const iframeSrc = await page.evaluate(() => {
        const iframe = document.querySelector('iframe#innerWrap');
        return iframe ? iframe.src : null;
      });

      if (iframeSrc) {
        await page.goto(iframeSrc, {
          waitUntil: 'networkidle2',
          timeout: 180000
        });
      }
    }

    await page.evaluate(async () => {
      let prev = 0, sameCount = 0, totalHeight = 0;
      while (true) {
        window.scrollBy(0, 300);
        await new Promise(r => setTimeout(r, 200));
        let sh = document.body.scrollHeight;
        totalHeight += 300;
        if (sh === prev) {
          sameCount++;
        } else {
          sameCount = 0;
          prev = sh;
        }
        if (sameCount >= 5) break;
        if (totalHeight > 1000000) break;
      }
      await new Promise(r => setTimeout(r, 2000));
    });

    const selectors = ['.synap-page', '.page', '.document-page'];
    let texts = [];

    for (const selector of selectors) {
      const nodes = await page.$$eval(selector, nodes =>
        nodes.map(n => n.innerText.trim()).filter(Boolean)
      ).catch(() => []);

      if (nodes.length > 0) {
        texts = nodes;
        break;
      }
    }

    if (texts.length === 0) {
      const bodyText = await page.evaluate(() => document.body.innerText);
      texts = [bodyText];
    }

    const finalText = texts.join('\n\n');

    const sanitizedText = finalText.replace(/<[^>]*>/g, '');

    await browser.close();

    res.json({
      text: sanitizedText,
      metadata: {
        url,
        extractedAt: new Date().toISOString(),
        chunkCount: texts.length,
        textLength: sanitizedText.length
      }
    });

  } catch (error) {
    if (browser) {
      await browser.close();
    }

    console.error('Scraping error:', error);
    res.status(500).json({
      error: 'Scraping failed',
      message: error.message
    });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'puppeteer-scraper' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Puppeteer scraper service listening on port ${PORT}`);
});
