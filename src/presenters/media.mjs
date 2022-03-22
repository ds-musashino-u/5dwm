/**
 * @classdesc Media
 */
export class Media {
    /**
     * @param {!string} url - Media URL
     * @param {!string} type - MIME type of Media
     * @param {?string} previewImageUrl - Preview image URL
     */
    constructor(url, type, previewImageUrl = null) {
        this.url = url;
        this.type = type;
        this.previewImageUrl = previewImageUrl;
    }

    get hasPreviewImageUrl() {
        return this.hasPreviewImageUrl !== null;
    }
}