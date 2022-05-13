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
export async function getMedia(sort = null, order = null, offset = 0, limit = null) {
    let url = `${Endpoints.TYPES_URL}?offset=${offset}`;

    if (limit !== null) {
        url += `&limit=${limit}`
    }

    if (type !== null) {
        url += `&type=${type}`
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

/**
 * /api/v1/media/{id}
 * @module getMedium
 * @param {!number} id - Media identifier
 * @return {?Media} - Media item
 */
export async function getMedium(id) {
    const response = await fetch(encodeURI(`${Endpoints.MEDIA_URL}/${id}`), {
        mode: "cors",
        method: "GET",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        const item = await response.json()

        if (item === null) {
            return null;
        }

        return new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at);
    } else {
        throw new Error(response.statusText);
    }
}

/**
 * /api/v1/media
 * @module insertMedium
 * @param {!string} url - URL 
 * @param {!string} type - MIME type
 * @param {!Array<string>} categories - Categories
 * @param {!string} description - Description
 * @param {!string} username - User name
 * @param {!Location} location - Location
 * @return {?Media} - Media item
 */
export async function insertMedium(url, type, categories, description, username, location) {
    const response = await fetch(encodeURI(Endpoints.MEDIA_URL), {
        mode: "cors",
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            url: url,
            type: type,
            categories: categories,
            description: description,
            username: username,
            location: {
                type: "Point",
                coordinates: [location.longitude, location.latitude]
            },
            address: location.address
        })
    });

    if (response.ok) {
        const item = await response.json()

        if (item === null) {
            return null;
        }

        return new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at);
    } else {
        throw new Error(response.statusText);
    }
}

/**
 * /api/v1/media/{id}
 * @module deleteMedium
 * @param {!number} id - Media identifier
 * @return {?Media} - Media item
 */
export async function deleteMedium(id) {
    const response = await fetch(encodeURI(`${Endpoints.MEDIA_URL}/${id}`), {
        mode: "cors",
        method: "DELETE",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    });

    if (response.ok) {
        const item = await response.json()

        if (item === null) {
            return null;
        }

        return new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at);
    } else {
        throw new Error(response.statusText);
    }
}