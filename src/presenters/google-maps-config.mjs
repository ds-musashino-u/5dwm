export class GoogleMapsConfig {
    static API_KEY = "AIzaSyCJfuPZn56-CDI74WPsUPGrQ3bI6hm7H9c";
    static VERSION = "beta"; //"quarterly";
    static MAP_ID = "DEMO_MAP_ID";
    static MAP_OPTIONS = {
        center: { lat: 35.6809591, lng: 139.7673068 },
        zoom: 4,
        mapId: this.MAP_ID,
        mapTypeId: "terrain",
        zoomControl: true,
        mapTypeControl: false,
        scaleControl: true,
        streetViewControl: false,
        rotateControl: true,
        fullscreenControl: false,
    };
}