import Apify from 'apify';
import { pravdaComUaHandle } from '../../src/handles/pravda';
import { failedRequestHandler } from './common';

const baseUrl = 'https://www.pravda.com.ua/news';
const pseudoUrls = [new Apify.PseudoUrl(`${baseUrl}/[.*]`)];

Apify.main(async () => {
    const { log } = Apify.utils;
    log.setLevel(log.LEVELS.DEBUG);

    const requestQueue = await Apify.openRequestQueue();
    await requestQueue.addRequest({ url: baseUrl });

    const crawler = new Apify.PuppeteerCrawler({
        requestQueue,
        handlePageFunction: async ({ page }) => {
            try {
                const { date, title, content, tags } = await pravdaComUaHandle(page);
                await Apify.pushData({
                    date,
                    title,
                    content,
                    tags,
                });
            } catch {
                log.error(`No news article on page '${await page.title()}'`);
            }

            await Apify.utils.enqueueLinks({ page, selector: 'a', pseudoUrls, requestQueue });
        },
        handleFailedRequestFunction: failedRequestHandler,
        maxRequestRetries: 2,
        maxRequestsPerCrawl: 10,
        maxConcurrency: 10,
    });

    await crawler.run();
});
