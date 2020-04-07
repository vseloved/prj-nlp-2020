import { Page } from 'puppeteer';
import { utils } from 'apify';
import { Article } from '../../types';

export const pravdaComUaHandle = async (page: Page): Promise<Article> => {
    const title = await page.$eval(`[class='post_news__title']`, (e) => e.textContent);
    const date = await page.$eval(`[class='post_news__date']`, (e) => e.textContent);
    const content = utils.htmlToText(
        await page.$eval(`[class='post_news__text']`, (e) => e.innerHTML)
    );
    const tags = await page.evaluate(() =>
        Array.from(
            document.querySelectorAll(`[class='post__tags__item']`),
            (element) => element.textContent
        )
    );

    return {
        title,
        date,
        content,
        tags,
    };
};
