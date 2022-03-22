/**
 * @classdesc Media
 */
 export class Media {
    /**
     * @param {!string} url - Media URL
     * @param {!string} type - MIME type of Media
     * @param {?string} preview_image_url - Preview image URL
     */
    constructor(url, type, preview_image_url = null) {
        this.url = url;
        this.type = type;
        this.preview_image_url = preview_image_url;
    }
}