import { encodeGeohash } from "./geohash.mjs"

/**
 * @classdesc Location
 */
export class Location {
    /**
     * @param {!number} longitude - Longitude
     * @param {!number} latitude - Latitude
     * @param {?string} address - Address
     */
    constructor(longitude, latitude, address = null, geohashPrecision=9) {
        this.longitude = longitude;
        this.latitude = latitude;
        this.address = address;
        this.geohash = encodeGeohash(latitude, longitude, geohashPrecision);
    }

    get hasAddress() {
        return this.address !== null && this.address.length > 0;
    }
}