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
     * @param {?Array<string>} dataTypes - Data types
     * @param {?object} data - Data
     * @param {?string} previewImageUrl - Preview image URL
     */
    constructor(id, url, type, categories, description, username, location, createdAt, dataTypes = null, data = null, thumbnailUrl = null) {
        this.id = id;
        this.url = url.replace(/^http:\/\//, "https://");
        this.type = type;
        this.categories = categories;
        this.description = description;
        this.username = username;
        this.location = location;
        this.createdAt = new Date(createdAt);
        this.dataTypes = dataTypes;
        this.data = data;
        this.thumbnailUrl = thumbnailUrl;
    }

    get hasDataTypes() {
        return this.dataTypes !== null;
    }

    get hasData() {
        return this.data !== null;
    }

    get hasThumbnailUrl() {
        return this.thumbnailUrl !== null;
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
                let mediaDataTypes = null;
                let mediaData = null;

                if ("data" in item) {
                    mediaDataTypes = item.data.types;
                    mediaData = [];

                    for (const record of item.data.items) {
                        mediaData.push({ id: record.id, values: record.values, time: new Date(record.time), location: new Location(record.location.coordinates[0], record.location.coordinates[1], "address" in record ? record.address : null) });
                    }
                }

                media.push(new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at, mediaDataTypes, mediaData));
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

        let mediaDataTypes = null;
        let mediaData = null;

        if ("data" in item) {
            mediaDataTypes = item.data.types;
            mediaData = [];

            for (const record of item.data.items) {
                mediaData.push({ id: record.id, values: record.values, time: new Date(record.time), location: new Location(record.location.coordinates[0], record.location.coordinates[1], "address" in record ? record.address : null) });
            }
        }

        return new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at, mediaDataTypes, mediaData);
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
 * @param {?Array<string>} dataTypes - Data types
 * @param {?object} data - Data
 * @return {?Media} - Media item
 */
export async function insertMedium(token, url, type, categories, description, username, location, createdAt = null, dataTypes = null, data = null) {
    const content = {
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
        content["address"] = location.address;
    }

    if (createdAt !== null) {
        content["created_at"] = createdAt.toISOString();
    }

    if (data !== null && Array.isArray(data)) {
        const dataItems = [];

        for (const record of data) {
            const dataItem = {
                id: record.id, values: record.values, time: record.time.toISOString(), location: {
                    type: "Point",
                    coordinates: [record.location.longitude, record.location.latitude]
                }
            };

            if ("address" in record.location) {
                dataItem["address"] = record.location.address;
            }

            dataItems.push(dataItem);
        }

        content["data"] = {types: dataTypes === null ? [] : dataTypes, items: dataItems};
    }

    const response = await fetch(encodeURI(Endpoints.MEDIA_URL), {
        mode: "cors",
        method: "POST",
        headers: {
            "X-Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(content)
    });

    if (response.ok) {
        const item = await response.json()

        if (item === null) {
            return null;
        }

        let mediaDataTypes = null;
        let mediaData = null;

        if ("data" in item) {
            mediaDataTypes = item.data.types;
            mediaData = [];

            for (const record of item.data.items) {
                mediaData.push({ id: record.id, values: record.values, time: new Date(record.time), location: new Location(record.location.coordinates[0], record.location.coordinates[1], "address" in record ? record.address : null) });
            }
        }

        return new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at, mediaDataTypes, mediaData);
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
 * @param {?Array<string>} dataTypes - Data types
 * @param {?object} data - Data
 * @return {?Media} - Media item
 */
export async function updateMedium(token, id, url, type, categories, description, username, location, createdAt = null, dataTypes = null, data = null) {
    const content = {
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
        content["address"] = location.address;
    }

    if (createdAt !== null) {
        content["created_at"] = createdAt.toISOString();
    }

    if (data !== null && Array.isArray(data)) {
        const dataItems = [];

        for (const record of data) {
            const dataItem = {
                id: record.id, values: record.values, time: record.time.toISOString(), location: {
                    type: "Point",
                    coordinates: [record.location.longitude, record.location.latitude]
                }
            };

            if ("address" in record.location) {
                dataItem["address"] = record.location.address;
            }

            dataItems.push(dataItem);
        }

        content["data"] = {types: dataTypes === null ? [] : dataTypes, items: dataItems};
    }

    const response = await fetch(encodeURI(`${Endpoints.MEDIA_URL}/${id}`), {
        mode: "cors",
        method: "PUT",
        headers: {
            "X-Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify(content)
    });

    if (response.ok) {
        const item = await response.json()

        if (item === null) {
            return null;
        }

        let mediaDataTypes = null;
        let mediaData = null;

        if ("data" in item) {
            mediaDataTypes = item.data.types;
            mediaData = [];

            for (const record of item.data.items) {
                mediaData.push({ id: record.id, values: record.values, time: new Date(record.time), location: new Location(record.location.coordinates[0], record.location.coordinates[1], "address" in record ? record.address : null) });
            }
        }

        return new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at, mediaDataTypes, mediaData);
    } else {
        throw new Error(response.statusText);
    }
}

/**
 * /api/v1/media/{id}
 * @module deleteMedium
 * @param {!string} token - Access token
 * @param {!number} id - Identifier
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

        let mediaDataTypes = null;
        let mediaData = null;

        if ("data" in item) {
            mediaDataTypes = item.data.types;
            mediaData = [];

            for (const record of item.data.items) {
                mediaData.push({ id: record.id, values: record.values, time: new Date(record.time), location: new Location(record.location.coordinates[0], record.location.coordinates[1], "address" in record ? record.address : null) });
            }
        }

        return new Media(item.id, item.url, item.type, item.categories, item.description, item.username, new Location(item.location.coordinates[0], item.location.coordinates[1], item.address), item.created_at, mediaDataTypes, mediaData);
    } else {
        throw new Error(response.statusText);
    }
}