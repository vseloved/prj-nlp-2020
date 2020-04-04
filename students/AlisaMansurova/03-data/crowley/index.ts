import Apify from 'apify';
import { pravdaComUaBaseUrl, pravdaComUaHandle } from './src/handles/pravda';

Apify.main(async () => {
    const { log } = Apify.utils;

    log.setLevel(log.LEVELS.DEBUG);

    // Open a request queue and add a start URL to it
    const requestQueue = await Apify.openRequestQueue();
    await requestQueue.addRequest({ url: pravdaComUaBaseUrl });

    // Define a pattern of URLs that the crawler should visit
    const pseudoUrls = [new Apify.PseudoUrl(`${pravdaComUaBaseUrl}/[.*]`)];

    // Create a crawler that will use headless Chrome / Puppeteer to extract data
    // from pages and recursively add links to newly-found pages
    const crawler = new Apify.PuppeteerCrawler({
        requestQueue,
        handlePageFunction: async ({ page }) => {
            try {
                const { date, title, content, tags } = await pravdaComUaHandle(page);
                await Apify.pushData({
                    date,
                    title,
                    content,
                    tags
                });
            } catch {
                log.error(`No news article on page '${await page.title()}'`);
            }

            await Apify.utils.enqueueLinks({ page, selector: 'a', pseudoUrls, requestQueue });
        },

        // This function is called for every page the crawler failed to load
        // or for which the handlePageFunction() throws at least "maxRequestRetries"-times
        handleFailedRequestFunction: async ({ request }) => {
            console.log(`Request ${request.url} failed too many times`);
            await Apify.pushData({
                '#debug': Apify.utils.createRequestDebugInfo(request)
            });
        },

        maxRequestRetries: 2,
        maxRequestsPerCrawl: 10,
        maxConcurrency: 10
    });

    await crawler.run();
});
