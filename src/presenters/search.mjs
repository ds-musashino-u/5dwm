import { Endpoints } from "./endpoints.mjs";
import { Media } from "./media.mjs";
import { Location } from "./location.mjs";

/**
 * /api/v1/search
 * @module search
 * @param {!Array<string>} keywords - Keywords
 * @param {!Array<string>} categories - Categories
 * @param {!Array<string>} types - Types
 * @param {?string} imageUrl - Image URL
 * @param {?string} sort - Sort
 * @param {?string} order - Order (asc or desc)
 * @param {!number} offset - Offset
 * @param {?number} limit - Limit
 * @return {Array<Media>} - Array of media items
 */
export async function search(keywords, categories, types, imageUrl = null, sort = null, order = null, offset = 0, limit = null) {
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
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        const media = [];
        const json = await response.json();

        for (const item of json) {
            if (item.location.type === "Point") {
                media.push(new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at));
            }
        }

        return media;
    } else {
        throw new Error(response.statusText);
    }
}