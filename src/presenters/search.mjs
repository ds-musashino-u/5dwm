import { Endpoints } from "./endpoints.mjs";
import { Media } from "./media.mjs";
import { Location } from "./location.mjs";

/**
 * /api/v1/categories
 * @module search
 * @param {!Array<string>} - Keywords
 * @param {!number} offset - Offset
 * @param {?number} limit - Limit
 * @return {Array<SearchItem>} - Array of search items
 */
export async function search(keywords, categories, types, imageUrl = null, offset = 0, limit = null) {
    const data = {
        keywords: keywords,
        categories: categories,
        types: types,
        offset: offset,
        limit: limit
    };

    if (imageUrl !== null) {
        data["image_url"] = imageUrl;
    }

    const response = await fetch(Endpoints.SEARCH_URL, {
        mode: "cors",
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (response.ok) {
        const media = [];
        const json = await response.json();

        for (const item of json) {
            media.push(new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.longitude, item.latitude, item.address), item.created_at));
        }

        return media;
    } else {
        throw new Error(response.statusText);
    }
}