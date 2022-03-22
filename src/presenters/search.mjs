import { Endpoints } from "./endpoints.mjs";
import { Media } from "./media.mjs";
import { Location } from "./location.mjs";

/**
 * @classdesc SearchItem
 */
export class SearchItem {
    /**
     * @param {!number} id - Identifier
     * @param {?string} description - Description
     * @param {!Array<string>} categories - Categories
     * @param {!Media} media - Media
     * @param {!Location} location - Location
     * @param {!string} createdAt - Created date time (ISO 8601)
     */
    constructor(id, description, categories, media, location, createdAt) {
        this.id = id;
        this.description = description;
        this.categories = categories;
        this.media = media;
        this.location = location;
        this.createdAt = new Date(createdAt);
    }
}

/**
 * /api/v1/categories
 * @module search
 * @param {!Array<string>} - Keywords
 * @param {!number} offset - Offset
 * @param {?number} limit - Limit
 * @return {Array<SearchItem>} - Array of search items
 */
export async function search(keywords, offset = 0, limit = null) {
    const imageUrl = "";
    const categories = "";
    const kinds = "";
    const databases = "";

    const response = await fetch("https://5dworldmap.com/api/v1/echo", {
        mode: "cors",
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            url: encodeURI(
                `${Endpoints.SEARCH_URL}?imgurl=${imageUrl}&keyword=${keywords.join(",")}&ctg=${categories}&kind=${kinds}&db=${databases}`
            ),
        }),
    });

    if (response.ok) {
        const searchItems = [];
    
        for (const item of await response.json()) {
            if ("id" in item) {
                searchItems.push(new SearchItem(item.id, item.description, [item.category], new Media(item.file_name, item.kind), new Location(item.lng, item.lat, item.place), item.datetaken));
            }
        }

        return searchItems;
    } else {
        throw new Error(response.statusText);
    }
}