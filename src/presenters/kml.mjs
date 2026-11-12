import { kmlGen } from "@tmcw/togeojson";
import { unzip } from "fflate";
import DOMPurify from "dompurify";
import { Endpoints } from "./endpoints.mjs";

const MAX_DOWNLOAD = 25 * 1024 * 1024;
const MAX_XML = 25 * 1024 * 1024;
const MAX_EXPANDED = 50 * 1024 * 1024;
const archiveOrigin = "https://kmz.invalid/";
const imageTypes = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif", webp: "image/webp", svg: "image/svg+xml" };
const styleProperties = [["stroke", "strokeColor"], ["stroke-opacity", "strokeOpacity"], ["stroke-width", "strokeWeight"], ["fill", "fillColor"], ["fill-opacity", "fillOpacity"], ["icon-opacity", "opacity"], ["icon", "icon"]];
const elementName = node => node.namespaceURI === "http://www.google.com/kml/ext/2.2" ? `gx:${node.localName}` : node.localName;
const tick = () => new Promise(resolve => setTimeout(resolve, 0));

export const isKml = type => /^(?:km[lz]|application\/vnd\.google-earth\.(?:kml\+xml|kmz))(?:$|[;/])/i.test(type ?? "");
const tunnelUrl = url => `${Endpoints.TUNNEL_URL}?${new URLSearchParams({ url })}`;

function value(node, name) {
    for (let next = node.firstChild; next; next = next.nextSibling) {
        if (next.nodeType === 1 && next.localName === name) return next.textContent.trim();
    }
}

async function download(url, signal) {
    const response = await fetch(tunnelUrl(url), { signal });
    if (!response.ok) throw new Error(`Could not load KML/KMZ (HTTP ${response.status}).`);
    if (Number(response.headers.get("content-length")) > MAX_DOWNLOAD) throw new Error("KML/KMZ exceeds the 25 MiB download limit.");
    const reader = response.body.getReader();
    const chunks = [];
    let length = 0;
    try {
        while (true) {
            signal.throwIfAborted();
            const { done, value } = await reader.read();
            if (done) break;
            length += value.length;
            if (length > MAX_DOWNLOAD) throw new Error("KML/KMZ exceeds the 25 MiB download limit.");
            chunks.push(value);
        }
    } finally {
        await reader.cancel().catch(() => {});
    }
    const bytes = new Uint8Array(length);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
    return bytes;
}

function expand(bytes, signal) {
    return new Promise((resolve, reject) => {
        let total = 0;
        let count = 0;
        let stop;
        const abort = () => { signal.removeEventListener("abort", abort); stop?.(); reject(signal.reason); };
        // Stored ZIP entries may finish synchronously. Register first so the
        // completion callback can always release this listener and the archive.
        signal.addEventListener("abort", abort, { once: true });
        if (signal.aborted) { abort(); return; }
        try {
            stop = unzip(bytes, {
                filter: file => {
                    total += file.originalSize;
                    if (++count > 256 || total > MAX_EXPANDED) throw new Error("KMZ exceeds the extraction limit (256 files / 50 MiB).");
                    return !file.name.startsWith("__MACOSX/") && /\.(?:kml|png|jpe?g|gif|webp|svg)$/i.test(file.name);
                }
            }, (error, files) => {
                signal.removeEventListener("abort", abort);
                if (error) reject(error);
                else resolve(files);
            });
        } catch (error) {
            signal.removeEventListener("abort", abort);
            reject(error);
        }
    });
}

function parseXml(bytes) {
    if (bytes.length > MAX_XML) throw new Error("KML exceeds the 25 MiB XML limit.");
    const prefix = new TextDecoder().decode(bytes.subarray(0, 200));
    const encoding = bytes[0] === 0xff && bytes[1] === 0xfe ? "utf-16le"
        : bytes[0] === 0xfe && bytes[1] === 0xff ? "utf-16be"
        : prefix.match(/<\?xml[^>]*encoding=["']([^"']+)/i)?.[1] ?? "utf-8";
    const document = new DOMParser().parseFromString(new TextDecoder(encoding, { fatal: true }).decode(bytes), "application/xml");
    if (document.documentElement?.localName !== "kml" || document.doctype || document.getElementsByTagName("parsererror").length) {
        throw new Error("The document is not valid KML.");
    }
    const elements = document.getElementsByTagName("*");
    let needsCopy = false;
    for (let index = 0; index < elements.length; index++) {
        if (elements[index].nodeName !== elementName(elements[index])) { needsCopy = true; break; }
    }
    if (!needsCopy) return document;
    // togeojson expects unprefixed KML tags; keep gx extensions under their
    // canonical prefix, even when the source uses a different namespace prefix.
    const normalized = document.implementation.createDocument(null, "", null);
    function copy(node, parent) {
        if (node.nodeType !== 1) { parent.appendChild(normalized.importNode(node, true)); return; }
        const element = normalized.createElementNS(node.namespaceURI, elementName(node));
        for (const attr of Array.from(node.attributes)) element.setAttribute(attr.name, attr.value);
        parent.appendChild(element);
        for (const next of Array.from(node.childNodes)) copy(next, element);
    }
    copy(document.documentElement, normalized);
    return normalized;
}

function validGeometry(geometry, count) {
    const point = position => {
        if (++count.vertices > 200000) throw new Error("KML exceeds the 200,000 vertex limit.");
        return Array.isArray(position) && position.length >= 2 && position.every(Number.isFinite)
            && Math.abs(position[0]) <= 180 && Math.abs(position[1]) <= 90;
    };
    const line = (positions, minimum = 2) => Array.isArray(positions) && positions.length >= minimum && positions.every(point);
    const polygon = rings => Array.isArray(rings) && rings.length > 0 && rings.every(ring => line(ring, 4)
        && ring[0][0] === ring.at(-1)[0] && ring[0][1] === ring.at(-1)[1]);
    switch (geometry?.type) {
        case "Point": return point(geometry.coordinates);
        case "MultiPoint": return line(geometry.coordinates, 1);
        case "LineString": return line(geometry.coordinates);
        case "MultiLineString": return geometry.coordinates.length > 0 && geometry.coordinates.every(positions => line(positions));
        case "Polygon": return polygon(geometry.coordinates);
        case "MultiPolygon": return geometry.coordinates.length > 0 && geometry.coordinates.every(polygon);
        case "GeometryCollection": return geometry.geometries.length > 0 && geometry.geometries.every(geometry => validGeometry(geometry, count));
        default: return false;
    }
}

function convert(document, warnings) {
    for (const tag of ["GroundOverlay", "ScreenOverlay", "NetworkLink", "Model"]) {
        if (document.getElementsByTagName(tag).length) warnings.add(`Unsupported KML element omitted: ${tag}.`);
    }
    // Resolve StyleMap's normal style independently of Pair ordering.
    for (const styleMap of Array.from(document.getElementsByTagName("StyleMap"))) {
        const pairs = Array.from(styleMap.childNodes).filter(node => node.nodeType === 1 && node.localName === "Pair");
        const normal = pairs.find(pair => value(pair, "key") === "normal");
        if (normal) for (const pair of pairs) if (pair !== normal) styleMap.removeChild(pair);
    }
    const placemarks = Array.from(document.getElementsByTagName("Placemark"));
    if (placemarks.length > 20000) throw new Error("KML exceeds the 20,000 feature limit.");
    // Keep ExtendedData separate so an attribute named 'icon' or 'visibility'
    // cannot overwrite rendering metadata emitted by the converter.
    const attributes = placemarks.map(placemark => Object.fromEntries([
        ...Array.from(placemark.getElementsByTagName("Data")).map(node => [node.getAttribute("name"), value(node, "value") ?? ""]),
        ...Array.from(placemark.getElementsByTagName("SimpleData")).map(node => [node.getAttribute("name"), node.textContent])
    ]));
    for (const node of Array.from(document.getElementsByTagName("ExtendedData"))) node.parentNode.removeChild(node);
    const count = { vertices: 0 };
    const features = [];
    const visibility = new WeakMap();
    const isVisible = node => {
        const ancestors = [];
        while (node?.nodeType === 1 && !visibility.has(node)) {
            ancestors.push(node);
            node = node.parentNode;
        }
        let visible = visibility.get(node) ?? true;
        for (let index = ancestors.length - 1; index >= 0; index--) {
            visible = visible && value(ancestors[index], "visibility") !== "0";
            visibility.set(ancestors[index], visible);
        }
        return visible;
    };
    let index = 0;
    for (const feature of kmlGen(document)) {
        if (feature.properties["@geometry-type"]) continue;
        const source = placemarks[index];
        // CDATA descriptions are represented as {@type: 'html', value} by
        // togeojson, while ordinary descriptions are strings.
        if (feature.properties.description?.["@type"] === "html") {
            feature.properties.description = feature.properties.description.value;
        }
        feature.properties.attributes = attributes[index];
        feature.properties.kmlId = feature.id ?? null;
        feature.id = `kml-${index++}`;
        if (!validGeometry(feature.geometry, count)) { warnings.add("Some placemarks have invalid or missing geometry and were omitted."); continue; }
        feature.properties.visibility = isVisible(source);
        if (feature.properties.styleUrl && !feature.properties.styleUrl.startsWith("#")) warnings.add("External styles are not supported.");
        features.push(feature);
    }
    if (!features.length) throw new Error("No supported point, line or polygon geometry was found.");
    return features;
}

function featureStyle(feature) {
    const style = { visible: feature.getProperty("visibility") !== false, title: feature.getProperty("name") };
    for (const [property, option] of styleProperties) {
        const value = feature.getProperty(property);
        if (value !== undefined) style[option] = value;
    }
    return style;
}

function imageSize(url, signal) {
    return new Promise((resolve, reject) => {
        const image = new Image();
        const finish = (error) => {
            clearTimeout(timeout);
            signal.removeEventListener("abort", abort);
            image.onload = image.onerror = null;
            if (error) { image.src = ""; reject(error); }
            else resolve({ width: image.naturalWidth, height: image.naturalHeight });
        };
        const abort = () => finish(signal.reason);
        const timeout = setTimeout(() => finish(new Error("An icon could not be loaded.")), 10000);
        image.onload = () => finish();
        image.onerror = () => finish(new Error("An icon could not be loaded."));
        signal.addEventListener("abort", abort, { once: true });
        if (signal.aborted) abort();
        else image.src = url;
    });
}

/** Load a detached layer. setMap(null) hides it; dispose() releases its resources. */
export async function loadKml(url, { signal } = {}) {
    const controller = new AbortController();
    const abort = () => controller.abort(signal.reason);
    signal?.addEventListener("abort", abort, { once: true });
    if (signal?.aborted) abort();
    const timeout = setTimeout(() => controller.abort(new DOMException("KML/KMZ download timed out.", "TimeoutError")), 30000);
    const objectUrls = new Map();
    const warnings = new Set();
    let files = null;
    let data = null;
    let infoWindow = null;
    let listener = null;
    let map = null;
    let disposed = false;
    const dispose = () => {
        if (disposed) return;
        disposed = true;
        map = null;
        data?.setMap(null);
        infoWindow?.close();
        listener?.remove();
        for (const blobUrl of objectUrls.values()) URL.revokeObjectURL(blobUrl);
        objectUrls.clear();
        files = null;
    };
    try {
        let bytes = await download(url, controller.signal);
        clearTimeout(timeout);
        let mainPath = null;
        if (bytes[0] === 0x50 && bytes[1] === 0x4b) {
            files = await expand(bytes, controller.signal);
            const names = Object.keys(files).filter(name => /\.kml$/i.test(name));
            mainPath = names.find(name => name.toLowerCase() === "doc.kml") ?? (names.length === 1 ? names[0] : null);
            if (mainPath === null) throw new Error("KMZ must contain doc.kml or one unambiguous KML document.");
            if (Object.values(files).reduce((total, bytes) => total + bytes.length, 0) > MAX_EXPANDED) throw new Error("KMZ exceeds the 50 MiB extraction limit.");
            bytes = files[mainPath];
        }
        controller.signal.throwIfAborted();
        const features = convert(parseXml(bytes), warnings);
        bytes = null;
        if (files) {
            for (const path of Object.keys(files)) if (/\.kml$/i.test(path)) delete files[path];
        }
        function resourceUrl(href) {
            if (files && !/^[a-z][a-z\d+.-]*:|^\/\//i.test(href)) {
                const path = decodeURIComponent(new URL(href, new URL(mainPath, archiveOrigin)).pathname.slice(1));
                if (objectUrls.has(path)) return objectUrls.get(path);
                if (!Object.hasOwn(files, path)) throw new Error(`Missing KMZ image: ${path}`);
                const type = imageTypes[path.split(".").pop().toLowerCase()];
                if (!type) throw new Error("Unsupported KMZ image type.");
                objectUrls.set(path, URL.createObjectURL(new Blob([files[path]], { type })));
                delete files[path];
                return objectUrls.get(path);
            }
            const resolved = new URL(href, url);
            if (!/^https?:$/.test(resolved.protocol)) throw new Error("Unsupported resource URL.");
            return tunnelUrl(resolved.href);
        }
        const sizes = new Map();
        const prepareIcon = async feature => {
            const properties = feature.properties;
            if (properties.icon) {
                try {
                    const icon = { url: resourceUrl(properties.icon) };
                    if (!sizes.has(icon.url)) sizes.set(icon.url, imageSize(icon.url, controller.signal));
                    const { width, height } = await sizes.get(icon.url);
                    const scale = Number.isFinite(properties["icon-scale"]) ? Math.max(0, properties["icon-scale"]) : 1;
                    icon.scaledSize = new google.maps.Size(width * scale, height * scale);
                    const offset = properties["icon-offset"];
                    const units = properties["icon-offset-units"];
                    if (offset && units) {
                        const pixels = (value, units, length) => units === "fraction" ? value * length : units === "insetPixels" ? length - value : value;
                        icon.anchor = new google.maps.Point(pixels(offset[0], units[0], width) * scale, (height - pixels(offset[1], units[1], height)) * scale);
                    }
                    properties.icon = icon;
                } catch (error) { delete properties.icon; warnings.add(error.message); }
            }
        };
        const icons = features.filter(feature => feature.properties.icon);
        for (let index = 0; index < icons.length; index += 16) {
            controller.signal.throwIfAborted();
            await Promise.all(icons.slice(index, index + 16).map(prepareIcon));
        }
        sizes.clear();
        await tick();
        controller.signal.throwIfAborted();
        data = new google.maps.Data();
        data.setStyle(featureStyle);
        const bounds = new google.maps.LatLngBounds();
        for (let index = 0; index < features.length; index += 250) {
            controller.signal.throwIfAborted();
            const added = data.addGeoJson({ type: "FeatureCollection", features: features.slice(index, index + 250) });
            for (const feature of added) {
                if (feature.getProperty("visibility") !== false) feature.getGeometry().forEachLatLng(position => bounds.extend(position));
            }
            await tick();
        }
        controller.signal.throwIfAborted();
        infoWindow = new google.maps.InfoWindow();
        listener = data.addListener("click", event => {
            const content = document.createElement("div");
            const name = document.createElement("strong");
            name.textContent = event.feature.getProperty("name") ?? "";
            const description = document.createElement("div");
            description.innerHTML = DOMPurify.sanitize(event.feature.getProperty("description") ?? "", {
                ALLOWED_TAGS: ["p", "br", "b", "strong", "i", "em", "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td", "a", "img"],
                ALLOWED_ATTR: ["href", "src", "alt", "title", "colspan", "rowspan"]
            });
            for (const image of description.querySelectorAll("img[src]")) {
                try { image.setAttribute("src", resourceUrl(image.getAttribute("src"))); }
                catch { image.removeAttribute("src"); }
            }
            for (const link of description.querySelectorAll("a[href]")) {
                try {
                    const resolved = new URL(link.getAttribute("href"), url);
                    if (!/^https?:$/.test(resolved.protocol)) throw new Error();
                    link.href = resolved.href;
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                } catch { link.removeAttribute("href"); }
            }
            content.append(name, description);
            const attributes = document.createElement("dl");
            for (const [key, value] of Object.entries(event.feature.getProperty("attributes") ?? {})) {
                const term = document.createElement("dt");
                const detail = document.createElement("dd");
                term.textContent = key;
                detail.textContent = String(value);
                attributes.append(term, detail);
            }
            content.append(attributes);
            infoWindow.setContent(content);
            infoWindow.setPosition(event.latLng);
            infoWindow.open({ map });
        });
        return {
            bounds,
            warnings: [...warnings],
            setMap(nextMap) {
                if (disposed) return;
                map = nextMap;
                data.setMap(nextMap);
                if (nextMap === null) infoWindow.close();
            },
            dispose
        };
    } catch (error) {
        dispose();
        throw controller.signal.aborted ? controller.signal.reason : error;
    } finally {
        clearTimeout(timeout);
        signal?.removeEventListener("abort", abort);
    }
}
