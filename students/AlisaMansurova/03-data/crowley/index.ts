import Apify from 'apify';
import { pravdaComUaBaseUrl, pravdaComUaHandle, pravdaComUaPseudoUrls } from './src/handles/pravda';
import { rozetkaPseudoUrls, rozetkaBaseUrl, rozetkaHandle } from './src/handles/rozetka';

const baseUrl = rozetkaBaseUrl;
const pseudoUrls = rozetkaPseudoUrls;
const handle = rozetkaHandle;

Apify.main(async () => {
    const { log } = Apify.utils;

    log.setLevel(log.LEVELS.DEBUG);

    // Open a request queue and add a start URL to it
    const requestQueue = await Apify.openRequestQueue();
    await requestQueue.addRequest({ url: baseUrl });

    // Create a crawler that will use headless Chrome / Puppeteer to extract data
    // from pages and recursively add links to newly-found pages
    const crawler = new Apify.PuppeteerCrawler({
        requestQueue,
        handlePageFunction: async ({ page }) => {
            try {
                const reviews = await handle(page);

                await Apify.pushData({ reviews });
            } catch (e) {
                log.error(e);
                // log.error(`No news article on page '${await page.title()}'`);
            }
            // await Apify.utils.puppeteer.infiniteScroll(page);
            await Apify.utils.enqueueLinks({
                page,
                selector: '.goods-tile__rating a[apprzroute]',
                pseudoUrls,
                requestQueue,
            });
            await Apify.utils.enqueueLinks({
                page,
                selector: '.pagination__link',
                pseudoUrls,
                requestQueue,
            });
        },

        // This function is called for every page the crawler failed to load
        // or for which the handlePageFunction() throws at least "maxRequestRetries"-times
        handleFailedRequestFunction: async ({ request }) => {
            console.log(`Request ${request.url} failed too many times`);
            await Apify.pushData({
                '#debug': Apify.utils.createRequestDebugInfo(request),
            });
        },

        maxRequestRetries: 2,
        maxRequestsPerCrawl: 8000,
        maxConcurrency: 50,
    });

    await crawler.run();
});
