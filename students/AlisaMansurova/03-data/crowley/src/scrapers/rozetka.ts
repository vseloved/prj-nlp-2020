import Apify from 'apify';
import { rozetkaHandle } from '../handles/rozetka';
import { failedRequestHandler } from './common';

const baseUrl = 'https://rozetka.com.ua/ua/tv-photo-video/c80258/page=15/';
const pseudoUrls = [new Apify.PseudoUrl(`[.*]`)];
const handle = rozetkaHandle;

Apify.main(async () => {
    const { log } = Apify.utils;
    log.setLevel(log.LEVELS.DEBUG);

    const requestQueue = await Apify.openRequestQueue();
    await requestQueue.addRequest({ url: baseUrl });

    const crawler = new Apify.PuppeteerCrawler({
        requestQueue,
        handlePageFunction: async ({ page }) => {
            try {
                const reviews = await handle(page);
                await Apify.pushData({ reviews });
            } catch (e) {
                log.error(e);
            }
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
        handleFailedRequestFunction: failedRequestHandler,
        maxRequestRetries: 2,
        maxRequestsPerCrawl: 10000,
        maxConcurrency: 50,
    });

    await crawler.run();
});
