import * as fs from 'fs';
import * as path from 'path';
import { Article } from '../../types';

const dataStoragePath = '../../apify_storage/datasets/default';
const resultFile = 'pravda.com.ua.json';
const datesFile = 'pravda.com.ua-dates.json';

const getArticles = () => {
    const dataStoragePathAbs = path.resolve(__dirname, dataStoragePath);
    const dataFiles = fs.readdirSync(dataStoragePathAbs);
    return dataFiles.map((f) => {
        const fullPath = path.resolve(dataStoragePathAbs, f);
        const article = JSON.parse((fs.readFileSync(fullPath) as unknown) as string) as Article;
        return article;
    });
};

export const merge = () => {
    const articles = getArticles();
    fs.writeFileSync(path.resolve(__dirname, resultFile), JSON.stringify(articles, null, 4));
};

const findDateRange = () => {
    const monthMap: { [key: string]: string } = {
        січня: '01',
        лютого: '02',
        березня: '03',
        квітня: '04',
        травня: '05',
        червня: '06',
        липня: '07',
        серпня: '08',
        вересня: '09',
        жовтня: '10',
        листопада: '11',
        грудня: '12',
    };

    const articles = getArticles();
    const years: { [key: string]: number } = {};
    const res = articles
        .map((article) => {
            const date = article.date as string;
            const dayDate = date.split(',')[1].trimLeft().split(' ');
            const day = dayDate[0].length === 1 ? `0${dayDate[0]}` : dayDate[0];
            const month = monthMap[dayDate[1].toLowerCase()];
            const year = dayDate[2];
            if (year in years) {
                years[year] += 1;
            } else {
                years[year] = 1;
            }
            return `${year}/${month}/${day}`;
        })
        .sort();
    const disp = Object.keys(years).map((y) => {
        const perc = Number(years[y]) / articles.length;
        return { [y]: perc.toFixed(4) };
    });
    console.log(disp);
    fs.writeFileSync(path.resolve(__dirname, datesFile), JSON.stringify(res, null, 4));
};

// main
// merge()
// findDateRange();
