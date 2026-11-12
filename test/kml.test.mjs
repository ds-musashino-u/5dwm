import assert from "node:assert/strict";
import sinon from "sinon";
import { DOMParser } from "@xmldom/xmldom";
import { strToU8, zipSync } from "fflate";
import { isKml, loadKml } from "../src/presenters/kml.mjs";

const wrap = content => `<kml xmlns="http://www.opengis.net/kml/2.2"><Document>${content}</Document></kml>`;
const point = '<Placemark id="same"><name>Tokyo</name><Point><coordinates>139.7,35.6,10</coordinates></Point></Placemark>';
const geometry = wrap(`${point}
  <Style id="normal"><LineStyle><color>ff0000ff</color><width>4</width></LineStyle></Style>
  <Style id="highlight"><LineStyle><color>ffff0000</color></LineStyle></Style>
  <StyleMap id="line"><Pair><key>highlight</key><styleUrl>#highlight</styleUrl></Pair><Pair><key>normal</key><styleUrl>#normal</styleUrl></Pair></StyleMap>
  <Placemark id="same"><styleUrl>#line</styleUrl><LineString><coordinates>139,35 140,36</coordinates></LineString></Placemark>
  <Placemark><Style><PolyStyle><color>8000ff00</color><outline>0</outline></PolyStyle></Style><Polygon>
    <outerBoundaryIs><LinearRing><coordinates>139,35 140,35 140,36 139,36 139,35</coordinates></LinearRing></outerBoundaryIs>
    <innerBoundaryIs><LinearRing><coordinates>139.2,35.2 139.8,35.2 139.8,35.8 139.2,35.2</coordinates></LinearRing></innerBoundaryIs>
  </Polygon></Placemark>`);

function positions(geometry) {
    if (geometry.type === "GeometryCollection") return geometry.geometries.flatMap(positions);
    const flatten = coords => typeof coords[0] === "number" ? [{ lng: coords[0], lat: coords[1] }] : coords.flatMap(flatten);
    return flatten(geometry.coordinates);
}

describe("KML/KMZ via GeoJSON and Google Maps Data", function () {
    let fetchStub;
    let layers;
    let windows;
    beforeEach(() => {
        layers = [];
        windows = [];
        sinon.define(globalThis, "DOMParser", DOMParser);
        sinon.define(globalThis, "Image", class {
            naturalWidth = 32;
            naturalHeight = 32;
            set src(value) { if (value) queueMicrotask(() => this.onload?.()); }
        });
        sinon.define(globalThis, "google", { maps: {
            Data: class {
                features = [];
                setMap = sinon.spy();
                listener = { remove: sinon.spy() };
                constructor() { layers.push(this); }
                setStyle(style) { this.style = style; }
                addListener(event, callback) { this.click = callback; return this.listener; }
                addGeoJson(collection) {
                    const features = collection.features.map(feature => ({
                        ...feature,
                        getProperty: key => feature.properties[key],
                        getGeometry: () => ({ forEachLatLng: callback => positions(feature.geometry).forEach(callback) })
                    }));
                    this.features.push(...features);
                    return features;
                }
            },
            LatLngBounds: class {
                points = [];
                extend(point) { this.points.push(point); return this; }
                isEmpty() { return this.points.length === 0; }
            },
            Size: class { constructor(width, height) { this.width = width; this.height = height; } },
            Point: class { constructor(x, y) { this.x = x; this.y = y; } },
            InfoWindow: class {
                close = sinon.spy();
                constructor() { windows.push(this); }
            }
        } });
        fetchStub = sinon.stub(globalThis, "fetch").callsFake(async () => new Response(geometry));
    });
    afterEach(() => sinon.restore());

    it("recognizes legacy types and standard MIME types", () => {
        for (const type of ["kml", "kmz", "kml/xml", "application/vnd.google-earth.kml+xml", "application/vnd.google-earth.kmz; charset=binary"]) {
            assert.equal(isKml(type), true, type);
        }
        for (const type of ["image/png", "application/zip", undefined]) assert.equal(isKml(type), false);
    });

    it("converts points, lines and polygons with holes, and uses the normal StyleMap style", async () => {
        const layer = await loadKml("https://example.com/map.kml");
        const data = layers[0];
        assert.equal(data.features.length, 3);
        assert.equal(data.features[0].geometry.type, "Point");
        assert.equal(data.features[2].geometry.coordinates.length, 2);
        assert.equal(new Set(data.features.map(feature => feature.id)).size, 3);
        assert.equal(data.features[0].properties.kmlId, "same");
        assert.equal(data.style(data.features[1]).strokeColor, "#ff0000");
        assert.equal(data.style(data.features[1]).strokeWeight, 4);
        assert.equal(data.style(data.features[2]).fillColor, "#00ff00");
        assert.equal(data.style(data.features[2]).fillOpacity, 128 / 255);
        assert.equal(data.style(data.features[2]).strokeOpacity, 0);
        assert.equal(data.setMap.callCount, 0, "loading must not attach the layer");
        assert.equal(layer.bounds.isEmpty(), false);
        layer.dispose();
    });

    it("supports MultiGeometry and keeps zero width and opacity", async () => {
        fetchStub.resolves(new Response(wrap('<Placemark><Style><LineStyle><color>000000ff</color><width>0</width></LineStyle></Style><MultiGeometry><Point><coordinates>139,35</coordinates></Point><LineString><coordinates>139,35 140,36</coordinates></LineString></MultiGeometry></Placemark>')));
        const layer = await loadKml("https://example.com/map.kml");
        assert.equal(layers[0].features[0].geometry.type, "GeometryCollection");
        assert.equal(layers[0].style(layers[0].features[0]).strokeOpacity, 0);
        assert.equal(layers[0].style(layers[0].features[0]).strokeWeight, 0);
        layer.dispose();
    });

    it("preserves URL query parameters, fragments and Unicode", async () => {
        const url = "https://example.com/地図.kml?a=1&b=2#area";
        const layer = await loadKml(url);
        assert.equal(new URL(fetchStub.firstCall.args[0]).searchParams.get("url"), url);
        layer.dispose();
    });

    it("reuses the same layer for on/off and keeps files isolated", async () => {
        const first = await loadKml("https://example.com/one.kml");
        const second = await loadKml("https://example.com/two.kml");
        const map = {};
        first.setMap(map);
        second.setMap(map);
        first.setMap(null);
        assert.equal(layers[0].setMap.lastCall.args[0], null);
        assert.equal(layers[1].setMap.lastCall.args[0], map);
        first.setMap(map);
        assert.equal(fetchStub.callCount, 2);
        assert.equal(layers[0].features.length, 3);
        first.dispose();
        first.dispose();
        assert.equal(layers[0].listener.remove.callCount, 1);
        const calls = layers[0].setMap.callCount;
        first.setMap(map);
        assert.equal(layers[0].setMap.callCount, calls, "disposed layers cannot reappear");
        second.dispose();
    });

    it("opens KMZ doc.kml and resolves an encoded relative icon", async () => {
        fetchStub.resolves(new Response(zipSync({
            "extra.kml": strToU8(wrap("")),
            "doc.kml": strToU8(wrap('<Placemark><Style><IconStyle><scale>2</scale><Icon><href>images/icon%20one.png</href></Icon></IconStyle></Style><Point><coordinates>139,35</coordinates></Point></Placemark>')),
            "images/icon one.png": new Uint8Array([1, 2, 3])
        })));
        const revoke = sinon.spy(URL, "revokeObjectURL");
        const layer = await loadKml("https://example.com/map.kmz");
        const icon = layers[0].style(layers[0].features[0]).icon;
        assert.match(icon.url, /^blob:/);
        assert.equal(icon.scaledSize.width, 64);
        layer.setMap({});
        layer.setMap(null);
        assert.equal(revoke.callCount, 0, "hidden layers retain resources for reuse");
        layer.dispose();
        layer.dispose();
        assert.equal(revoke.callCount, 1);
    });

    it("accepts one nested KML and resolves icons relative to it", async () => {
        fetchStub.resolves(new Response(zipSync({
            "folder/main.kml": strToU8(wrap('<Placemark><Style><IconStyle><Icon><href>../images/icon.png</href></Icon></IconStyle></Style><Point><coordinates>139,35</coordinates></Point></Placemark>')),
            "images/icon.png": new Uint8Array([1])
        })));
        const layer = await loadKml("https://example.com/map.kmz");
        assert.match(layers[0].features[0].properties.icon.url, /^blob:/);
        layer.dispose();
    });

    it("resolves external icons relative to the original KML URL", async () => {
        fetchStub.resolves(new Response(wrap('<Placemark><Style><IconStyle><Icon><href>../icon.png?a=1&amp;b=2</href></Icon></IconStyle></Style><Point><coordinates>139,35</coordinates></Point></Placemark>')));
        const layer = await loadKml("https://example.com/folder/map.kml");
        const icon = layers[0].features[0].properties.icon;
        assert.equal(new URL(icon.url).searchParams.get("url"), "https://example.com/icon.png?a=1&b=2");
        layer.dispose();
    });

    it("falls back to a default marker for missing or unsafe icons", async () => {
        fetchStub.resolves(new Response(wrap('<Placemark><Style><IconStyle><Icon><href>javascript:alert(1)</href></Icon></IconStyle></Style><Point><coordinates>139,35</coordinates></Point></Placemark>')));
        const layer = await loadKml("https://example.com/map.kml");
        assert.equal(layers[0].features[0].properties.icon, undefined);
        assert.match(layer.warnings.join(" "), /resource URL/);
        layer.dispose();
    });

    it("inherits Document/Folder visibility and excludes hidden geometry from bounds", async () => {
        fetchStub.resolves(new Response(wrap(`<Folder><visibility>0</visibility>${point}</Folder>${point}`)));
        const layer = await loadKml("https://example.com/map.kml");
        assert.equal(layers[0].style(layers[0].features[0]).visible, false);
        assert.equal(layers[0].style(layers[0].features[1]).visible, true);
        assert.equal(layer.bounds.points.length, 1);
        layer.dispose();
        fetchStub.resolves(new Response(wrap(`<visibility>0</visibility>${point}`)));
        const hidden = await loadKml("https://example.com/map.kml");
        assert.equal(hidden.bounds.isEmpty(), true);
        hidden.dispose();
    });

    it("keeps nested and sibling visibility independent when reusing ancestor results", async () => {
        fetchStub.resolves(new Response(wrap(`<visibility>1</visibility>
            <Folder><visibility>0</visibility>${point}<Folder><visibility>1</visibility>${point}</Folder></Folder>
            <Folder><visibility>1</visibility>${point}<Folder><visibility>0</visibility>${point}</Folder></Folder>
            <Placemark><visibility>0</visibility><Point><coordinates>139,35</coordinates></Point></Placemark>`)));
        const layer = await loadKml("https://example.com/nested.kml");
        assert.deepEqual(layers[0].features.map(feature => layers[0].style(feature).visible), [false, false, true, false, false]);
        assert.equal(layer.bounds.points.length, 1);
        layer.dispose();
    });

    it("produces the same geometry, attributes and styles for normal and prefixed KML", async () => {
        const xml = geometry.replace("<name>Tokyo</name>", '<name>Tokyo</name><ExtendedData><Data name="test"><value>value</value></Data></ExtendedData>');
        const prefixed = xml.replace(/(<\/?)([A-Za-z][\w.-]*)(?=[\s/>])/g, "$1k:$2").replace("xmlns=", "xmlns:k=");
        const results = [];
        for (const source of [xml, prefixed]) {
            fetchStub.resolves(new Response(source));
            const layer = await loadKml("https://example.com/map.kml");
            results.push(layers.at(-1).features.map(({ id, geometry, properties }) => ({ id, geometry, properties })));
            layer.dispose();
        }
        assert.deepEqual(results[1], results[0]);
    });

    it("preserves gx tracks with canonical and alternate namespace prefixes", async () => {
        const results = [];
        for (const prefix of ["gx", "track"]) {
            const xml = `<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:${prefix}="http://www.google.com/kml/ext/2.2"><Placemark><${prefix}:Track>
                <when>2026-11-12T00:00:00Z</when><when>2026-11-12T00:01:00Z</when>
                <${prefix}:coord>139 35 0</${prefix}:coord><${prefix}:coord>140 36 10</${prefix}:coord>
                </${prefix}:Track></Placemark></kml>`;
            fetchStub.resolves(new Response(xml));
            const layer = await loadKml("https://example.com/track.kml");
            results.push(layers.at(-1).features[0]);
            layer.dispose();
        }
        assert.deepEqual(results[0].geometry.coordinates, [[139, 35, 0], [140, 36, 10]]);
        assert.deepEqual(results[1].geometry, results[0].geometry);
        assert.deepEqual(results[1].properties, results[0].properties);
    });

    it("reuses an embedded image after its raw archive entry has been released", async () => {
        const feature = '<Placemark><Style><IconStyle><Icon><href>images/shared.png</href></Icon></IconStyle></Style><Point><coordinates>139,35</coordinates></Point></Placemark>';
        fetchStub.resolves(new Response(zipSync({
            "doc.kml": strToU8(wrap(feature + feature)),
            "unused.kml": strToU8(wrap(point)),
            "images/shared.png": new Uint8Array([1])
        })));
        const create = sinon.spy(URL, "createObjectURL");
        const layer = await loadKml("https://example.com/shared.kmz");
        const [first, second] = layers[0].features;
        assert.equal(first.properties.icon.url, second.properties.icon.url);
        assert.equal(create.callCount, 1);
        layer.setMap({});
        layer.setMap(null);
        layer.setMap({});
        assert.equal(first.properties.icon.url, second.properties.icon.url);
        layer.dispose();
    });

    it("separates ExtendedData from style and visibility metadata", async () => {
        fetchStub.resolves(new Response(wrap(`<Placemark><ExtendedData><Data name="icon"><value>javascript:bad()</value></Data><Data name="visibility"><value>false</value></Data></ExtendedData><Point><coordinates>139,35</coordinates></Point></Placemark>`)));
        const layer = await loadKml("https://example.com/map.kml");
        const feature = layers[0].features[0];
        assert.equal(feature.properties.icon, undefined);
        assert.equal(feature.properties.visibility, true);
        assert.equal(feature.properties.attributes.icon, "javascript:bad()");
        layer.dispose();
    });

    it("normalizes CDATA HTML descriptions for the sanitized info window", async () => {
        fetchStub.resolves(new Response(wrap('<Placemark><description><![CDATA[<b>Safe text</b><script>bad()</script>]]></description><Point><coordinates>139,35</coordinates></Point></Placemark>')));
        const layer = await loadKml("https://example.com/map.kml");
        assert.equal(layers[0].features[0].properties.description, "<b>Safe text</b><script>bad()</script>");
        layer.dispose();
    });

    it("parses namespace-prefixed KML and UTF-16 XML", async () => {
        const xml = '<k:kml xmlns:k="http://www.opengis.net/kml/2.2"><k:Placemark><k:name>地図</k:name><k:Point><k:coordinates>139,35</k:coordinates></k:Point></k:Placemark></k:kml>';
        fetchStub.resolves(new Response(Buffer.concat([Buffer.from([0xff, 0xfe]), Buffer.from(xml, "utf16le")])));
        const layer = await loadKml("https://example.com/map.kml");
        assert.equal(layers[0].features[0].properties.name, "地図");
        layer.dispose();
    });

    it("omits overlays and NetworkLinks instead of drawing them as polygons", async () => {
        fetchStub.resolves(new Response(wrap(`${point}<GroundOverlay><Icon><href>overlay.png</href></Icon><LatLonBox><north>36</north><south>35</south><east>140</east><west>139</west></LatLonBox></GroundOverlay><NetworkLink><Link><href>remote.kml</href></Link></NetworkLink>`)));
        const layer = await loadKml("https://example.com/map.kml");
        assert.equal(layers[0].features.length, 1);
        assert.equal(fetchStub.callCount, 1);
        assert.match(layer.warnings.join(" "), /GroundOverlay/);
        assert.match(layer.warnings.join(" "), /NetworkLink/);
        layer.dispose();
    });

    for (const [name, payload, message] of [
        ["HTTP failure", () => new Response("missing", { status: 404 }), /HTTP 404/],
        ["non-KML XML", () => new Response("<html>error</html>"), /not valid KML/],
        ["missing geometry", () => new Response(wrap("<Placemark/>")), /No supported/],
        ["invalid coordinates", () => new Response(wrap('<Placemark><Point><coordinates>200,100</coordinates></Point></Placemark>')), /No supported/],
        ["KMZ without KML", () => new Response(zipSync({ "icon.png": new Uint8Array([1]) })), /unambiguous/],
        ["ambiguous KMZ", () => new Response(zipSync({ "one.kml": strToU8(geometry), "two.kml": strToU8(geometry) })), /unambiguous/],
        ["oversized response", () => new Response(geometry, { headers: { "content-length": String(26 * 1024 * 1024) } }), /download limit/]
    ]) {
        it(`rejects ${name} and allows retry`, async () => {
            fetchStub.onFirstCall().resolves(payload());
            await assert.rejects(loadKml("https://example.com/map"), message);
            const layer = await loadKml("https://example.com/map");
            assert.equal(layers.at(-1).features.length, 3);
            layer.dispose();
        });
    }

    it("accepts uncompressed KML above the previous download and XML limits", async function () {
        this.timeout(10000);
        fetchStub.resolves(new Response(wrap(`<name>${"x".repeat(21 * 1024 * 1024)}</name>${point}`)));
        const layer = await loadKml("https://example.com/large.kml");
        assert.equal(layers[0].features.length, 1);
        assert.equal(layers[0].features[0].properties.name, "Tokyo");
        layer.dispose();
    });

    it("handles an already cancelled request", async () => {
        const controller = new AbortController();
        controller.abort();
        await assert.rejects(loadKml("https://example.com/map.kml", { signal: controller.signal }), { name: "AbortError" });
        assert.equal(layers.length, 0);
    });

    it("cancels between conversion and attachment without leaving a late layer", async () => {
        const controller = new AbortController();
        const pending = loadKml("https://example.com/map.kml", { signal: controller.signal });
        setTimeout(() => controller.abort(), 0);
        await assert.rejects(pending, { name: "AbortError" });
        for (const data of layers) assert.equal(data.setMap.lastCall.args[0], null);
    });
});
