/**
 * @classdesc Location
 */
export class Location {
    /**
     * @param {!number} longitude - Longitude
     * @param {!number} latitude - Latitude
     * @param {?string} address - Address
     */
    constructor(longitude, latitude, address = null) {
        this.longitude = longitude;
        this.latitude = latitude;
        this.address = address;
    }

    get hasAddress() {
        return this.address !== null && this.address.length > 0;
    }
}