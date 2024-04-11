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
 * @param {!string} token - Access token
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
export async function search(token, keywords, categories, types, usernames, image = null, from = null, to = null, sort = null, order = null, offset = 0, limit = null) {
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

    if (from !== null) {
        data["from"] = from.toISOString();
    }

    if (to !== null) {
        data["to"] = to.toISOString();
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
            let mediaData = null;
            const regex = /^(https:\/\/static.5dworldmap.com\/media\/)(\S+)$/g;
            const thumbnailUrl = regex.test(item.url) ? item.url.replace(regex, "$1thumbnails/$2") : null;

            if (!/^https?:\/\//.test(item.url)) {
                if (item.type.startsWith("kml") || item.type.startsWith("kmz")) {
                    item.url = `https://www.5dwm.mydns.jp/5dtest/upload/kmlkmz/${item.url}`;
                } else {
                    item.url = `https://www.5dwm.mydns.jp/5dtest/upload/images/${item.url}`;
                }
            }

            if ("data" in item) {
                mediaData = [];

                for (const record of item.data) {
                    if ("values" in record) {
                        mediaData.push({ id: record.id, values: record.values, time: new Date(record.time), location: new Location(record.location.coordinates[0], record.location.coordinates[1], "address" in record ? record.address : null) });
                    } else {
                        mediaData.push({ id: record.id, value: record.value, time: new Date(record.time), location: new Location(record.location.coordinates[0], record.location.coordinates[1], "address" in record ? record.address : null) });
                    }
                }
            }

            if (item.location !== null && item.location.type === "Point" && typeof (item.location.coordinates[0]) === "number" && typeof (item.location.coordinates[1]) === "number") {
                resultItems.push(new ResultItem(item.score, new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at, mediaData, thumbnailUrl)));
            } else {
                resultItems.push(new ResultItem(item.score, new Media(item.id, item.url, item.type, item.categories, item.description, item.username, null, item.created_at, mediaData, thumbnailUrl)));
            }
        }

        return [resultItems, json.count, json.timestamp];
    } else {
        throw new Error(response.statusText);
    }
}