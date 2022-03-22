/**
 * @classdesc SearchItem
 */
 export class SearchItem {
    /**
     * @param {!number} id - Identifier
     * @param {!string} name - Category name
     * @param {!string} createdAt - Updated date time (ISO 8601)
     */
    constructor(id, name, location, createdAt) {
        this.id = id;
        this.name = name;
        this.updatedAt = new Date(updatedAt);
    }
}