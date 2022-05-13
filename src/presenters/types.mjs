import { Endpoints } from "./endpoints.mjs";

/**
 * /api/v1/types
 * @module getTypes
 * @param {?string} sort - Sort
 * @param {?string} order - Order (asc or desc)
 * @param {!number} offset - Offset
 * @param {?number} limit - Limit
 * @return {Array<string>} - Array of type
 */
export async function getTypes(sort = null, order = null, offset = 0, limit = null) {
    let url = `${Endpoints.TYPES_URL}?offset=${offset}`;

    if (limit !== null) {
        url += `&limit=${limit}`
    }

    if (sort !== null) {
        url += `&sort=${sort}`
    }

    if (order !== null) {
        url += `&order=${order}`
    }

    const response = await fetch(encodeURI(url), {
        mode: "cors",
        method: "GET",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        const types = [];

        for (const type of await response.json()) {
            types.push(type);
        }

        return types;
    } else {
        throw new Error(response.statusText);
    }
}