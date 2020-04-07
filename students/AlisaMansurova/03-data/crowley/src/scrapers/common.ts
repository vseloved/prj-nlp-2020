import Apify from 'apify';

// This function is called for every page the crawler failed to load
// or for which the handlePageFunction() throws at least "maxRequestRetries"-times
export const failedRequestHandler = async ({ request }: { request: Apify.Request }) => {
    console.log(`Request ${request.url} failed too many times`);
    await Apify.pushData({
        '#debug': Apify.utils.createRequestDebugInfo(request),
    });
};
