export interface Article {
    title: string | null;
    date: string | null;
    content: string | null;
    tags?: (string | null)[];
}

export interface Review {
    rating: number | null;
    text?: string;
    pros?: string;
    cons?: string;
}
