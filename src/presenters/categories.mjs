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
 * @param {!number} offset - Offset
 * @param {?number} limit - Limit
 * @return {!Array<Category>} - Array of category
 */
export async function getCategories(offset = 0, limit = null) {
    let url = `${Endpoints.CATEGORIES_URL}?offset=${offset}`;

    if (limit !== null) {
        url += `&limit=${limit}`
    }

    const response = await fetch(encodeURI(url), {
        mode: "cors",
        method: "GET",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        const categories = [];

        for (const category of await response.json()) {
            categories.push(new Category(category.id, category.name, category.updated_at));
        }

        return categories;
    } else {
        throw new Error(response.statusText);
    }
}

/**
 * /api/v1/categories/{id}
 * @module getCategory
 * @param {!number} id - Category identifier
 * @return {?Category} - Category item
 */
export async function getCategory(id) {
    const response = await fetch(encodeURI(`${Endpoints.CATEGORIES_URL}/${id}`), {
        mode: "cors",
        method: "GET",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        const category = await response.json()

        if (category === null) {
            return null;
        }

        return new Category(category.id, category.name, category.updated_at);
    } else {
        throw new Error(response.statusText);
    }
}

/**
 * /api/v1/categories
 * @module addCategory
 * @param {!number} name - Category identifier
 * @return {?Category} - Category item
 */
export async function addCategory(name) {
    const response = await fetch(encodeURI(Endpoints.CATEGORIES_URL), {
        mode: "cors",
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: name })
    });

    if (response.ok) {
        const category = await response.json()

        if (category === null) {
            return null;
        }

        return new Category(category.id, category.name, category.updated_at);
    } else {
        throw new Error(response.statusText);
    }
}

/**
 * /api/v1/categories/{id}
 * @module removeCategory
 * @param {!number} id - Category identifier
 * @return {?Category} - Category item
 */
export async function removeCategory(id) {
    const response = await fetch(encodeURI(`${Endpoints.CATEGORIES_URL}/${id}`), {
        mode: "cors",
        method: "DELETE",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        const category = await response.json()

        if (category === null) {
            return null;
        }

        return new Category(category.id, category.name, category.updated_at);
    } else {
        throw new Error(response.statusText);
    }
}