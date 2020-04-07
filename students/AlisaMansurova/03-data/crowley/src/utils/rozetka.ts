import * as fs from 'fs';
import * as path from 'path';
import { Review } from '../../types';

const dataStoragePath = '../../apify_storage/datasets/default';
const resultFile = 'rozetka.json';

const getReviews = () => {
    const dataStoragePathAbs = path.resolve(__dirname, dataStoragePath);
    const dataFiles = fs.readdirSync(dataStoragePathAbs);

    return dataFiles.map((f) => {
        const fullPath = path.resolve(dataStoragePathAbs, f);
        const reviews = JSON.parse((fs.readFileSync(fullPath) as unknown) as string) as {
            reviews: Review[];
        };
        return reviews;
    });
};

export const mergeReviews = () => {
    const reviews = getReviews();
    const res = reviews.map((review) => review.reviews);

    // @ts-ignore
    const allRes: Review[] = res.flat();

    fs.writeFileSync(path.resolve(__dirname, resultFile), JSON.stringify(allRes, null, 4));
};

// main
mergeReviews();
