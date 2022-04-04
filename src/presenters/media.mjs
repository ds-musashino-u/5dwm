import { Location } from "./location.mjs";

/**
 * @classdesc Media
 */
export class Media {
    /**
     * @param {!integer} id - Media Identifier
     * @param {!string} url - Media URL
     * @param {!string} type - MIME type of Media
     * @param {!Array<string>} categories - Categories
     * @param {!string} description - Description
     * @param {!string} username - User name
     * @param {!Location} location - Location
     * @param {!string} createdAt - Updated date time (ISO 8601)
     * @param {?string} previewImageUrl - Preview image URL
     */
    constructor(id, url, type, categories, description, username, location, createdAt, previewImageUrl = null) {
        this.id = id;
        this.url = url;
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