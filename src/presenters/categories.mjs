import { Endpoints } from "./endpoints.mjs";

/**
 * @classdesc Category
 */
export class Category {
    /**
     * @param {!number} id - Identifier
     * @param {!string} name - Category name
     * @param {!string} updated - Updated date time (ISO 8601)
     */
    constructor(id, name, updatedAt) {
        this.id = id;
        this.name = name;
        this.updatedAt = new Date(updatedAt);
    }
}

/**
 * /api/v1/categories
 * @module getCategories
 * @param {number} offset - Offset
 * @param {number} limit - Limit
 * @return {Array<Category>} - Array of category
 */
export async function getCategories(offset = 0, limit = null) {
    const categories = [];
    let url = `${Endpoints.CATEGORIES_URL}?offset=${offset}`;

    if (limit !== null) {
        url += `&limit=${limit}`
    }

    try {
        const response = await fetch(encodeURI(url), {
            mode: "cors",
            method: "GET",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        });

        if (response.ok) {
            for (const category of await response.json()) {
                categories.push(new Category(category.id, category.name, category.updated_at));
            }
        } else {
            throw new Error(response.statusText);
        }
    } catch (error) {
        console.error(error);
    }

    return categories;
}