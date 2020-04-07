import { Page } from 'puppeteer';
import { Review } from '../../types';

export const rozetkaHandle = async (page: Page): Promise<Review[]> => {
    const getShowMoreBtn = async () => {
        const showMoreBtn = await page.$(
            'button[class*="button button_size_medium product-comments__show-more"]'
        );
        if (showMoreBtn) {
            await showMoreBtn.click();
            await page.waitFor(1000);
            await getShowMoreBtn();
        }
    };
    await getShowMoreBtn();

    const comments = await page.$$(`product-comment`);
    return Promise.all(
        comments.map(async (c) => {
            const body = await c.$(`[class='product-comment__body']`);
            const content = await body!.evaluate((x) => x.textContent);
            const ratingString = await (await c.$(`[class='rating-stars']`))?.evaluate((x) =>
                x.getAttribute('aria-label')
            );

            const contentParts = content?.split(/(?=Достоинства:)/);
            const text = contentParts?.[0];

            const pros = content?.match(/(?<=Достоинства: ).*(?= Недостатки)/)?.[0];
            const cons = content?.match(/(?<=Недостатки: ).*/)?.[0];
            const ratingMatch = ratingString?.match(/([\d\.]+)/)?.[0];
            const rating = ratingMatch ? Number(ratingMatch) : null;

            return {
                rating,
                text,
                pros,
                cons,
            };
        })
    );
};
