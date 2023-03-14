import { Endpoints } from "./endpoints.mjs";
import { Location } from "./location.mjs";

/**
 * @classdesc Media
 */
export class Media {
    /**
     * @param {!integer} id - Identifier
     * @param {!string} url - Media URL
     * @param {!string} type - MIME type of Media
     * @param {!Array<string>} categories - Categories
     * @param {!string} description - Description
     * @param {!string} username - User name
     * @param {?Location} location - Location
     * @param {!string} createdAt - Updated date time (ISO 8601)
     * @param {?string} previewImageUrl - Preview image URL
     */
    constructor(id, url, type, categories, description, username, location, createdAt, previewImageUrl = null) {
        this.id = id;
        this.url = url.replace(/^http:\/\//, "https://");
        this.type = type;
        this.categories = categories;
        this.description = description;
        this.username = username;
        this.location = location;
        this.createdAt = new Date(createdAt);
        this.previewImageUrl = previewImageUrl;
    }

    get hasPreviewImageUrl() {
        return this.hasPreviewImageUrl !== null;
    }
}

/**
 * /api/v1/media
 * @module getMedia
 * @param {?string} type - MIME type
 * @param {?string} sort - Sort
 * @param {?string} order - Order (asc or desc)
 * @param {!number} offset - Offset
 * @param {?number} limit - Limit
 * @return {Array<Media>} - Array of media
 */
export async function getMedia(type = null, sort = null, order = null, offset = 0, limit = null) {
    let url = `${Endpoints.MEDIA_URL}?offset=${offset}`;

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
        const media = [];

        for (const item of await response.json()) {
            if (item.location.type === "Point") {
                media.push(new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at));
            }
        }

        return media;
    } else {
        throw new Error(response.statusText);
    }
}

/**
 * /api/v1/media/{id}
 * @module getMedium
 * @param {!number} id - Identifier
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
 * @param {!string} token - Access token
 * @param {!string} url - URL 
 * @param {!string} type - MIME type
 * @param {!Array<string>} categories - Categories
 * @param {!string} description - Description
 * @param {!string} username - User name
 * @param {!Location} location - Location
 * @param {?Date} createdAt - Created date time
 * @return {?Media} - Media item
 */
export async function insertMedium(token, url, type, categories, description, username, location, createdAt=null) {
    const data = {
        url: url,
        type: type,
        categories: categories,
        description: description,
        username: username,
        location: {
            type: "Point",
            coordinates: [location.longitude, location.latitude]
        }
    };

    if (location.hasAddress) {
        data["address"] = location.address;
    }

    if (createdAt !== null) {
        data["created_at"] = createdAt.toISOString()
    }

    const response = await fetch(encodeURI(Endpoints.MEDIA_URL), {
        mode: "cors",
        method: "POST",
        headers: {
            "X-Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
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
 * @param {!string} token - Access token
 * @param {!number} id - Identifier
 * @param {!string} url - URL 
 * @param {!string} type - MIME type
 * @param {!Array<string>} categories - Categories
 * @param {!string} description - Description
 * @param {!string} username - User name
 * @param {!Location} location - Location
 * @param {?Date} createdAt - Created date time
 * @return {?Media} - Media item
 */
export async function updateMedium(token, id, url, type, categories, description, username, location, createdAt=null) {
    const data = {
        id: id,
        url: url,
        type: type,
        categories: categories,
        description: description,
        username: username,
        location: {
            type: "Point",
            coordinates: [location.longitude, location.latitude]
        }
    };

    if (location.hasAddress) {
        data["address"] = location.address;
    }

    if (createdAt !== null) {
        data["created_at"] = createdAt.toISOString()
    }

    const response = await fetch(encodeURI(Endpoints.MEDIA_URL), {
        mode: "cors",
        method: "PUT",
        headers: {
            "X-Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
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
 * @param {!string} token - Access token
 * @param {!number} id - Media identifier
 * @return {?Media} - Media item
 */
export async function deleteMedium(token, id) {
    const response = await fetch(encodeURI(`${Endpoints.MEDIA_URL}/${id}`), {
        mode: "cors",
        method: "DELETE",
        headers: {
            "X-Authorization": `Bearer ${token}`,
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