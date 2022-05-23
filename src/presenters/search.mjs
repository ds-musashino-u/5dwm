import { Endpoints } from "./endpoints.mjs";
import { Media } from "./media.mjs";
import { Location } from "./location.mjs";

/**
 * @classdesc ResultItem
 */
 export class ResultItem {
    /**
     * @param {?number} score - Score
     * @param {!Media} media - Media
     */
    constructor(score, media) {
        this.score = score;
        this.media = media;
    }

    get hasScore() {
        return this.score !== null;
    }
}

/**
 * /api/v1/search
 * @module search
 * @param {!string} token - ID token
 * @param {!Array<string>} keywords - Keywords
 * @param {!Array<string>} categories - Categories
 * @param {!Array<string>} types - Types
 * @param {!Array<string>} usernames - Usernames
 * @param {?string} image - Data URL of Image
 * @param {?string} sort - Sort
 * @param {?string} order - Order (asc or desc)
 * @param {!number} offset - Offset
 * @param {?number} limit - Limit
 * @return {Array<ResultItem>} - Array of result items
 */
export async function search(token, keywords, categories, types, usernames, image = null, sort = null, order = null, offset = 0, limit = null) {
    const data = {
        keywords: keywords,
        categories: categories,
        types: types,
        usernames: usernames,
        offset: offset,
        limit: limit
    };

    if (image !== null) {
        data["image"] = image;
    }

    if (sort !== null) {
        data["sort"] = sort;
    }

    if (order !== null) {
        data["order"] = order;
    }

    const response = await fetch(Endpoints.SEARCH_URL, {
        mode: "cors",
        method: "POST",
        headers: {
            "X-Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        const resultItems = [];
        const json = await response.json();

        for (const item of json.items) {
            // Fallback
            if(!/^https?:\/\//.test(item.url)) {
                item.url = `https://www.5dwm.mydns.jp/5dtest/upload/images/${item.url}`;
            }

            if (item.location !== null && item.location.type === "Point" && typeof(item.location.coordinates[0]) === "number" && typeof(item.location.coordinates[1]) === "number") {
                resultItems.push(new ResultItem(item.score, new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at)));
            } else {
                resultItems.push(new ResultItem(item.score, new Media(item.id, item.url, item.type, item.categories, item.description, item.username, null, item.created_at)));
            }
        }

        return [resultItems, json.count];
    } else {
        throw new Error(response.statusText);
    }
}