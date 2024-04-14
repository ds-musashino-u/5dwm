<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, reactive, onMounted, onUnmounted, onActivated, onDeactivated, watch } from "vue";
import { getAccessToken } from "../presenters/auth.mjs";
import { getCategories } from "../presenters/categories.mjs";
import { getTypes } from "../presenters/types.mjs";
import { Location } from "../presenters/location.mjs";
import { Media, getMedium, insertMedium, updateMedium, deleteMedium } from "../presenters/media.mjs";
import { upload as uploadMedia } from "../presenters/uploader.mjs";
import { GoogleMapsConfig } from "../presenters/google-maps-config.mjs";
import { csv } from "csvtojson";
import { EXIF } from "exif-js";
import ListBox from "./ListBox.vue";

const props = defineProps({
    auth0: Object,
    user: Object,
    text: String,
    isAdmin: Boolean,
    isClosable: { type: Boolean, required: false, default: false },
    isDeletable: { type: Boolean, required: false, default: false },
    media: { type: Object, required: false, default: null },
});
const mapRef = ref(null);
let map = null;
let geocoder = null;
const isInitializedRef = ref(false);
const isDraggingRef = ref(false);
const isFetchingRef = ref(false);
const isLoadingRef = ref(false);
const isLocatingRef = ref(false);
const isUploadingRef = ref(false);
const isUploadedRef = ref(false);
const isDeletingRef = ref(false);
const deleteButtonRef = ref(null);
const deleteConfirmation = reactive({ visible: false, dismiss: false });
const mediaIDRef = ref(null);
const mediaIsCollapsedRef = ref(false);
const mediaFileRef = ref(null);
const mediaPreviewRef = ref(null);
const mediaUrlRef = ref("");
const mediaDataTypesRef = ref(null);
const mediaDataRef = ref(null);
const descriptionRef = ref("");
const latitudeRef = ref("");
const longitudeRef = ref("");
const hasLocationErrorRef = ref(false);
const addressRef = ref("");
const timeRef = ref(new Date());
const timeYearRef = ref(timeRef.value.getFullYear());
const timeMonthRef = ref(timeRef.value.getMonth());
const timeDayRef = ref(timeRef.value.getDate());
const timeHoursRef = ref(timeRef.value.getHours());
const timeMinutesRef = ref(timeRef.value.getMinutes());
const timeSecondsRef = ref(timeRef.value.getSeconds());
const hasTimeErrorRef = ref(false);
const maxCategoriesLength = 100;
const categoriesRef = ref([]);
const categoriesIsCollapsedRef = ref(false);
const categoriesIsContinuousRef = ref(false);
const categoriesItemsRef = ref([]);
const categoriesPageIndexRef = ref(0);
const maxTypesLength = 25;
const typeRef = ref(null);
const typesIsLoadingRef = ref(true);
const typesIsCollapsedRef = ref(false);
const typesIsContinuousRef = ref(false);
const typesItemsRef = ref([]);
const typesPageIndexRef = ref(0);
const progressRef = ref(0);

if (props.media !== null) {
    mediaIDRef.value = props.media.id;
    mediaUrlRef.value = props.media.url;
    descriptionRef.value = props.media.description;
    timeRef.value = props.media.createdAt;
    timeYearRef.value = timeRef.value.getFullYear();
    timeMonthRef.value = timeRef.value.getMonth();
    timeDayRef.value = timeRef.value.getDate();
    timeHoursRef.value = timeRef.value.getHours();
    timeMinutesRef.value = timeRef.value.getMinutes();
    timeSecondsRef.value = timeRef.value.getSeconds();
    longitudeRef.value = String(props.media.location.longitude);
    latitudeRef.value = String(props.media.location.latitude);
    typeRef.value = props.media.type;

    if ("dataTypes" in props.media && props.media.dataTypes !== null) {
        mediaDataTypesRef.value = [];
        
        for (const type of props.media.dataTypes) {
            mediaDataTypesRef.value.push(type);
        }
    }

    if ("data" in props.media && props.media.data !== null) {
        mediaDataRef.value = [];

        for (const mediaDataItem of props.media.data) {
            mediaDataRef.value.push({ id: mediaDataItem.id, value: mediaDataItem.value, time: mediaDataItem.time, location: new Location(mediaDataItem.location.longitude, mediaDataItem.location.latitude, mediaDataItem.location.address !== null && mediaDataItem.location.address.length > 0 ? mediaDataItem.location.address : null) });
        }
    }

    if (props.media.categories !== null) {
        for (const category of props.media.categories) {
            categoriesRef.value.push(category);
        }
    }

    if (props.media.location.address !== null && props.media.location.address.length > 0) {
        addressRef.value = props.media.location.address;
    }
}

const emit = defineEmits(["close", "updated"]);
const resizeImage = async (dataURL, length) => {
    try {
        return await new Promise(async (resolve1, reject1) => {
            const i = new Image();

            i.onload = () => {
                const canvas = document.createElement("canvas");

                if (i.width > i.height) {
                    if (i.width > length) {
                        canvas.width = length * window.devicePixelRatio;
                        canvas.height =
                            Math.floor((length / i.width) * i.height) *
                            window.devicePixelRatio;
                    } else {
                        canvas.width = i.width * window.devicePixelRatio;
                        canvas.height = i.height * window.devicePixelRatio;
                    }
                } else if (i.height > length) {
                    canvas.width =
                        Math.floor((length / i.height) * i.width) * window.devicePixelRatio;
                    canvas.height = length * window.devicePixelRatio;
                } else {
                    canvas.width = i.width * window.devicePixelRatio;
                    canvas.height = i.height * window.devicePixelRatio;
                }

                const ctx = canvas.getContext("2d");

                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = "high";
                ctx.drawImage(i, 0, 0, canvas.width, canvas.height);
                ctx.canvas.toBlob(async (blob) => {
                    try {
                        resolve1(
                            await new Promise(async (resolve2, reject2) => {
                                const reader = new FileReader();

                                reader.onload = () => {
                                    resolve2(reader.result);
                                };
                                reader.onerror = () => {
                                    reject2(reader.error);
                                };
                                reader.readAsDataURL(blob);
                            })
                        );
                    } catch (e) {
                        reject1(e);
                    }

                    ctx.canvas.width = ctx.canvas.height = 0;
                }, "image/jpeg");
            };
            i.onerror = (error) => {
                reject1(error);
            };
            i.crossOrigin = "anonymous";
            i.src = dataURL;
        });
    } catch (e) {
        console.error(e);
    }

    return null;
};
const toFormattedData = (data) => {
    const formattedDataTypes = [];
    const formattedData = [];

    if (data[0].length > 4 && data[0][0] === "Date" && data[0][1] === "Location" && data[0][2] === "Latitude" && data[0][3] === "Longitude") {
        let index = 0;

        for (const row of data) {
            if (index > 0) {
                const date = Date.parse(row[0]);
                const latitude = parseFloat(row[2]);
                const longitude = parseFloat(row[3]);
                const values = [];

                if (date === NaN || latitude === NaN || longitude === NaN) {
                    return null;
                }

                for (let i = 4; i < row.length; i++) {
                    const value = parseFloat(row[i]);

                    if (value === NaN) {
                        return null;
                    }

                    values.push(value);
                }

                formattedData.push({ id: index - 1, values: values, time: new Date(date), location: new Location(longitude, latitude, row[1]) });
            } else {
                for (let i = 4; i < row.length; i++) {
                    formattedDataTypes.push(row[i]);
                }
            }

            index++;
        }
    } else {
        for (const row of data) {
            if (row.length === 6) {
                const id = parseInt(row[0]);
                const value = parseFloat(row[1]);
                const date = Date.parse(row[2]);
                const latitude = parseFloat(row[4]);
                const longitude = parseFloat(row[5]);

                if (id === NaN || value === NaN || date === NaN || latitude === NaN || longitude === NaN) {
                    return null;
                }

                formattedData.push({ id: id, values: [value], time: new Date(date), location: new Location(longitude, latitude, row[3]) });
            } else {
                return null;
            }
        }
    }

    return [formattedDataTypes, formattedData];
};
const close = (event) => {
    emit("close");
};
const dragover = (event) => {
    isDraggingRef.value = true;
    event.dataTransfer.dropEffect = "copy";
};
const drop = async (event) => {
    isDraggingRef.value = false;

    for (const file of event.dataTransfer.files) {
        isLoadingRef.value = true;

        try {
            mediaUrlRef.value = "";
            mediaFileRef.value = {
                filename: file.name,
                type: file.type,
                dataURL: await new Promise(function (resolve, reject) {
                    const reader = new FileReader();

                    reader.addEventListener("load", (e) => {
                        if (file.type === "image/jpeg") {
                            const image = new Image();

                            image.onload = () => {
                                EXIF.getData(image, async () => {
                                    const tags = EXIF.getAllTags(image);

                                    if ("DateTimeOriginal" in tags) {
                                        timeRef.value = new Date(tags["DateTimeOriginal"].replace(/^(\d{4}):(\d{2}):(\d{2})\s(\d{2}):(\d{2}):(\d{2})$/g, "$1/$2/$3 $4:$5:$6"));
                                        timeYearRef.value = timeRef.value.getFullYear();
                                        timeMonthRef.value = timeRef.value.getMonth();
                                        timeDayRef.value = timeRef.value.getDate();
                                        timeHoursRef.value = timeRef.value.getHours();
                                        timeMinutesRef.value = timeRef.value.getMinutes();
                                        timeSecondsRef.value = timeRef.value.getSeconds();
                                    }

                                    if ("GPSLatitude" in tags && "GPSLatitudeRef" in tags && "GPSLongitude" in tags && "GPSLongitudeRef" in tags) {
                                        let latitude = tags["GPSLatitude"][0] / 1.0 + tags["GPSLatitude"][1] / 60.0 + tags["GPSLatitude"][2] / 3600.0;
                                        let longitude = tags["GPSLongitude"][0] / 1.0 + tags["GPSLongitude"][1] / 60.0 + tags["GPSLongitude"][2] / 3600.0;

                                        if ("S" === tags["GPSLatitudeRef"]) {
                                            latitude *= -1
                                        }

                                        if ("W" === tags["GPSLongitudeRef"]) {
                                            longitude *= -1
                                        }

                                        map.panTo(new google.maps.LatLng(latitude, longitude));

                                        latitudeRef.value = latitude.toFixed(5);
                                        longitudeRef.value = longitude.toFixed(5);

                                        try {
                                            const response = await geocoder.geocode({
                                                location: {
                                                    lat: latitude,
                                                    lng: longitude,
                                                },
                                                language: "en"
                                            });

                                            if (response.results.length > 0) {
                                                addressRef.value = response.results[0].formatted_address;
                                            }
                                        } catch (error) {
                                            console.error(error);
                                        }
                                    }
                                });
                            };
                            image.src = reader.result;
                        }

                        resolve(reader.result);
                    });
                    reader.addEventListener("error", (e) => {
                        reject(reader.error);
                    });
                    reader.readAsDataURL(file);
                }),
            };
            mediaDataTypesRef.value = null;
            mediaDataRef.value = null;

            if (mediaFileRef.value.type.startsWith('image/')) {
                mediaPreviewRef.value = await resizeImage(mediaFileRef.value.dataURL, 512);
            } else {
                if (mediaFileRef.value.type === "text/csv") {
                    const result = toFormattedData(await new Promise(function (resolve, reject) {
                        const reader = new FileReader();

                        reader.addEventListener("load", async (e) => {
                            resolve(await csv({ output: "csv", noheader: true }).fromString(reader.result));
                        });
                        reader.addEventListener("error", (e) => {
                            reject(reader.error);
                        });
                        reader.readAsText(file);
                    }));

                    if (result !== null) {
                        mediaDataTypesRef.value = result[0];
                        mediaDataRef.value = result[1];
                    }
                }

                mediaPreviewRef.value = null;
            }

            let type;

            if (mediaFileRef.value.type === "text/csv") {
                type = "csv";
            } else {
                type = mediaFileRef.value.type;
            }

            for (const item of typesItemsRef.value) {
                if (type.startsWith(item.name)) {
                    item.checked = true;
                    typeRef.value = item.name;
                } else {
                    item.checked = false;
                }
            }

            mediaUrlRef.value = "";
        } catch (error) {
            console.error(error);
        }

        isLoadingRef.value = false;

        return;
    }
};
const browse = async (event) => {
    for (const file of event.currentTarget.files) {
        isLoadingRef.value = true;

        try {
            mediaUrlRef.value = "";
            mediaFileRef.value = {
                filename: file.name,
                type: file.type,
                dataURL: await new Promise(function (resolve, reject) {
                    const reader = new FileReader();

                    reader.onload = () => {
                        if (file.type === "image/jpeg") {
                            const image = new Image();

                            image.onload = () => {
                                EXIF.getData(image, async () => {
                                    const tags = EXIF.getAllTags(image);

                                    if ("DateTimeOriginal" in tags) {
                                        timeRef.value = new Date(tags["DateTimeOriginal"].replace(/^(\d{4}):(\d{2}):(\d{2})\s(\d{2}):(\d{2}):(\d{2})$/g, "$1/$2/$3 $4:$5:$6"));
                                        timeYearRef.value = timeRef.value.getFullYear();
                                        timeMonthRef.value = timeRef.value.getMonth();
                                        timeDayRef.value = timeRef.value.getDate();
                                        timeHoursRef.value = timeRef.value.getHours();
                                        timeMinutesRef.value = timeRef.value.getMinutes();
                                        timeSecondsRef.value = timeRef.value.getSeconds();
                                    }

                                    if ("GPSLatitude" in tags && "GPSLatitudeRef" in tags && "GPSLongitude" in tags && "GPSLongitudeRef" in tags) {
                                        let latitude = tags["GPSLatitude"][0] / 1.0 + tags["GPSLatitude"][1] / 60.0 + tags["GPSLatitude"][2] / 3600.0;
                                        let longitude = tags["GPSLongitude"][0] / 1.0 + tags["GPSLongitude"][1] / 60.0 + tags["GPSLongitude"][2] / 3600.0;

                                        if ("S" === tags["GPSLatitudeRef"]) {
                                            latitude *= -1
                                        }

                                        if ("W" === tags["GPSLongitudeRef"]) {
                                            longitude *= -1
                                        }

                                        map.panTo(new google.maps.LatLng(latitude, longitude));

                                        latitudeRef.value = latitude.toFixed(5);
                                        longitudeRef.value = longitude.toFixed(5);

                                        try {
                                            const response = await geocoder.geocode({
                                                location: {
                                                    lat: latitude,
                                                    lng: longitude,
                                                },
                                                language: "en"
                                            });

                                            if (response.results.length > 0) {
                                                addressRef.value = response.results[0].formatted_address;
                                            }
                                        } catch (error) {
                                            console.error(error);
                                        }
                                    }
                                });
                            };
                            image.src = reader.result;
                        }

                        resolve(reader.result);
                    };
                    reader.onerror = () => {
                        reject(reader.error);
                    };
                    reader.readAsDataURL(file);
                }),
            };
            mediaDataTypesRef.value = null;
            mediaDataRef.value = null;

            if (mediaFileRef.value.type.startsWith('image/')) {
                mediaPreviewRef.value = await resizeImage(mediaFileRef.value.dataURL, 512);
            } else {
                if (mediaFileRef.value.type === "text/csv") {
                    const result = toFormattedData(await new Promise(function (resolve, reject) {
                        const reader = new FileReader();

                        reader.addEventListener("load", async (e) => {
                            resolve(await csv({ output: "csv", noheader: true }).fromString(reader.result));
                        });
                        reader.addEventListener("error", (e) => {
                            reject(reader.error);
                        });
                        reader.readAsText(file);
                    }));

                    if (result !== null) {
                        mediaDataTypesRef.value = result[0];
                        mediaDataRef.value = result[1];
                    }
                }

                mediaPreviewRef.value = null;
            }

            for (const item of typesItemsRef.value) {
                if (mediaFileRef.value.type.startsWith(item.name)) {
                    item.checked = true;
                    typeRef.value = item.name;
                } else {
                    item.checked = false;
                }
            }

            mediaUrlRef.value = "";
        } catch (error) {
            console.error(error);
        }

        isLoadingRef.value = false;

        return;
    }
};
const resetMedia = (event) => {
    mediaFileRef.value = null;
    mediaDataTypesRef.value = null;
    mediaDataRef.value = null;
    mediaPreviewRef.value = null;

    for (const item of typesItemsRef.value) {
        item.checked = false;
    }
};
const clearImageUrl = (event) => {
    mediaUrlRef.value = "";
};
const pasteImageUrl = async (event) => {
    try {
        const text = await navigator.clipboard.readText();

        if (text.startsWith("https://")) {
            mediaUrlRef.value = text;
        } else {
            shake(event.currentTarget || event.target);
        }
    } catch (error) {
        console.error(error);
    }
};
const pasteDescription = async (event) => {
    try {
        descriptionRef.value = await navigator.clipboard.readText();
    } catch (error) {
        console.error(error);
    }
};
const latitudeChange = (event) => {
    if (isFinite(latitudeRef.value) && isFinite(longitudeRef.value)) {
        const location = map.getCenter();

        if (latitudeRef.value !== String(location.lat()) || longitudeRef.value !== String(location.lng())) {
            map.panTo(
                new google.maps.LatLng(
                    Number(latitudeRef.value),
                    Number(longitudeRef.value)
                )
            );
        }

        hasLocationErrorRef.value = false;
    } else {
        hasLocationErrorRef.value = true;
    }
};
const longitudeChange = (event) => {
    if (isFinite(latitudeRef.value) && isFinite(longitudeRef.value)) {
        const location = map.getCenter();

        if (latitudeRef.value !== String(location.lat()) || longitudeRef.value !== String(location.lng())) {
            map.panTo(
                new google.maps.LatLng(
                    Number(latitudeRef.value),
                    Number(longitudeRef.value)
                )
            );
        }

        hasLocationErrorRef.value = false;
    } else {
        hasLocationErrorRef.value = true;
    }
};
const geocode = async (event) => {
    if (addressRef.value.length > 0) {
        try {
            const response = await geocoder.geocode({ address: addressRef.value });

            if (response.results.length > 0) {
                const location = response.results[0].geometry.location;

                latitudeRef.value = String(location.lat());
                longitudeRef.value = String(location.lng());

                map.panTo(
                    new google.maps.LatLng(
                        Number(latitudeRef.value),
                        Number(longitudeRef.value)
                    )
                );
            }
        } catch (error) {
            console.error(error);
        }
    }
};
const resetTime = (event) => {
    timeRef.value = new Date();
    timeYearRef.value = timeRef.value.getFullYear();
    timeMonthRef.value = timeRef.value.getMonth();
    timeDayRef.value = timeRef.value.getDate();
    timeHoursRef.value = timeRef.value.getHours();
    timeMinutesRef.value = timeRef.value.getMinutes();
    timeSecondsRef.value = timeRef.value.getSeconds();
};
function timeIsValid(d, m, y) {
    function daysInMonth(m, y) { // m is 0 indexed: 0-11
        switch (m) {
            case 1:
                return (y % 4 == 0 && y % 100) || y % 400 == 0 ? 29 : 28;
            case 8: case 3: case 5: case 10:
                return 30;
            default:
                return 31
        }
    }

    return m >= 0 && m < 12 && d > 0 && d <= daysInMonth(m, y);
}
const timeDateChange = (event) => {
    const date = new Date(event.currentTarget.value);

    hasTimeErrorRef.value = !timeIsValid(date.getDate(), date.getMonth(), date.getFullYear());

    if (!hasTimeErrorRef.value) {
        timeRef.value.setFullYear(date.getFullYear());
        timeRef.value.setMonth(date.getMonth());
        timeRef.value.setDate(date.getDate());
    }
};
const timeMonthChange = (event) => {
    hasTimeErrorRef.value = !timeIsValid(timeRef.value.getDate(), Number(event.currentTarget.value) - 1, timeRef.value.getFullYear());

    if (!hasTimeErrorRef.value) {
        timeRef.value.setMonth(Number(event.currentTarget.value) - 1);
    }
};
const timeDayChange = (event) => {
    hasTimeErrorRef.value = !timeIsValid(Number(event.currentTarget.value), timeRef.value.getMonth(), timeRef.value.getFullYear());

    if (!hasTimeErrorRef.value) {
        timeRef.value.setDate(Number(event.currentTarget.value));
    }
};
const timeHoursChange = (event) => {
    timeRef.value.setHours(Number(event.currentTarget.value));

    hasTimeErrorRef.value = isNaN(timeRef.value.getDate());
};
const timeMinutesChange = (event) => {
    timeRef.value.setMinutes(Number(event.currentTarget.value));

    hasTimeErrorRef.value = isNaN(timeRef.value.getDate());
};
const timeSecondsChange = (event) => {
    timeRef.value.setSeconds(Number(event.currentTarget.value));

    hasTimeErrorRef.value = isNaN(timeRef.value.getDate());
};
const collapseCategories = () => {
    categoriesIsCollapsedRef.value = !categoriesIsCollapsedRef.value;
};
const collapseTypes = () => {
    typesIsCollapsedRef.value = !typesIsCollapsedRef.value;
};
const clearCategories = () => {
    for (const item of categoriesItemsRef.value) {
        if (item.checked) {
            item.checked = false;
        }
    }
};
const clearTypes = () => {
    for (const item of typesItemsRef.value) {
        if (item.checked) {
            item.checked = false;
        }
    }
};
const selectCategory = (index) => {
    categoriesItemsRef.value[index].checked = !categoriesItemsRef.value[index].checked;
    categoriesRef.value = categoriesItemsRef.value.filter(x => x.checked).map(x => x.name);
};
const selectType = (index) => {
    typesItemsRef.value[index].checked = !typesItemsRef.value[index].checked;

    for (let i = 0; i < typesItemsRef.value.length; i++) {
        if (index !== i && typesItemsRef.value[i].checked) {
            typesItemsRef.value[i].checked = false;
        }
    }

    if (typesItemsRef.value[index].checked) {
        typeRef.value = typesItemsRef.value[index].name;
    } else if (typesItemsRef.value.every(x => !x.checked)) {
        typeRef.value = "";
    }
};
const nextCategories = async (pageIndex, pageLength, isFetchingRef) => {
    if (categoriesItemsRef.value.length <= pageIndex * maxCategoriesLength) {
        isFetchingRef.value = true;

        try {
            const items = await getCategories(pageIndex * maxCategoriesLength, pageLength);
            let length;

            if (items.length > maxCategoriesLength) {
                categoriesIsContinuousRef.value = true;
                length = maxCategoriesLength;
            } else {
                categoriesIsContinuousRef.value = false;
                length = items.length;
            }

            for (let i = 0; i < length; i++) {
                categoriesItemsRef.value.push({ checked: categoriesRef.value.find(x => x === items[i].name) !== undefined, name: items[i].name });
            }
        } catch (error) {
            console.error(error);
        }

        isFetchingRef.value = false;
    }

    categoriesPageIndexRef.value = pageIndex;
};
const previousCategories = async (pageIndex) => {
    categoriesIsContinuousRef.value = true;
    categoriesPageIndexRef.value = pageIndex;
};
const nextTypes = async (pageIndex, pageLength, isFetchingRef) => {
    if (typesItemsRef.value.length <= pageIndex * maxTypesLength) {
        typesIsLoadingRef.value = isFetchingRef.value = true;

        try {
            const items = await getTypes(null, null, pageIndex * maxTypesLength, pageLength);
            let length;

            if (items.length > maxTypesLength) {
                typesIsContinuousRef.value = true;
                length = maxTypesLength;
            } else {
                typesIsContinuousRef.value = false;
                length = items.length;
            }

            if (typeRef.value !== null && typeRef.value.length > 0) {
                for (let i = 0; i < length; i++) {
                    typesItemsRef.value.push({ checked: typeRef.value.startsWith(items[i]), name: items[i] });
                }
            } else if (mediaFileRef.value === null) {
                for (let i = 0; i < length; i++) {
                    typesItemsRef.value.push({ checked: false, name: items[i] });
                }
            } else {
                for (let i = 0; i < length; i++) {
                    if (mediaFileRef.value.type.startsWith(items[i])) {
                        typesItemsRef.value.push({ checked: true, name: items[i] });
                        typeRef.value = items[i];
                    } else {
                        typesItemsRef.value.push({ checked: false, name: items[i] });
                    }
                }
            }
        } catch (error) {
            console.error(error);
        }

        typesIsLoadingRef.value = isFetchingRef.value = false;
    }

    typesPageIndexRef.value = pageIndex;
};
const previousTypes = async (pageIndex) => {
    typesIsContinuousRef.value = true;
    typesPageIndexRef.value = pageIndex;
};
const shake = (element) => {
    element.animate(
        [
            { transform: "translate3d(0, 0, 0)" },
            { transform: "translate3d(8px, 0, 0)" },
            { transform: "translate3d(-8px, 0, 0)" },
            { transform: "translate3d(7px, 0, 0)" },
            { transform: "translate3d(-7px, 0, 0)" },
            { transform: "translate3d(6px, 0, 0)" },
            { transform: "translate3d(-6px, 0, 0)" },
            { transform: "translate3d(5px, 0, 0)" },
            { transform: "translate3d(-5px, 0, 0)" },
            { transform: "translate3d(4px, 0, 0)" },
            { transform: "translate3d(-4px, 0, 0)" },
            { transform: "translate3d(3px, 0, 0)" },
            { transform: "translate3d(-3px, 0, 0)" },
            { transform: "translate3d(2px, 0, 0)" },
            { transform: "translate3d(-2px, 0, 0)" },
            { transform: "translate3d(1px, 0, 0)" },
            { transform: "translate3d(-1px, 0, 0)" },
            { transform: "translate3d(0, 0, 0)" },
        ],
        { duration: 1000, iterations: 1 }
    );
};
const locate = async () => {
    if ("permissions" in navigator) {
        const permissionStatus = await navigator.permissions.query({ name: "geolocation" });

        if (permissionStatus.state == "granted" || permissionStatus.state == "prompt") {
            isLocatingRef.value = true;
            navigator.geolocation.getCurrentPosition((position) => {
                isLocatingRef.value = false;
                latitudeRef.value = String(position.coords.latitude);
                longitudeRef.value = String(position.coords.longitude)
                map.panTo(
                    new google.maps.LatLng(
                        position.coords.latitude,
                        position.coords.longitude
                    )
                );
            }, (error) => {
                isLocatingRef.value = false;
                console.error(error);
            }, {
                enableHighAccuracy: true,
                timeout: 30000,
                maximumAge: 0
            });
        }
    } else {
        isLocatingRef.value = true;

        navigator.geolocation.getCurrentPosition((position) => {
            isLocatingRef.value = false;
            latitudeRef.value = String(position.coords.latitude);
            longitudeRef.value = String(position.coords.longitude)
            map.panTo(
                new google.maps.LatLng(
                    position.coords.latitude,
                    position.coords.longitude
                )
            );
        }, (error) => {
            isLocatingRef.value = false;
            console.error(error);
        }, {
            enableHighAccuracy: true,
            timeout: 30000,
            maximumAge: 0
        });
    }
};
const upload = async (event, completed) => {
    let url = null;
    let thumbnailUrl = null;

    isUploadingRef.value = true;

    if (mediaFileRef.value !== null) {
        progressRef.value = 0.5;

        try {
            const result = await uploadMedia(await getAccessToken(props.auth0), mediaFileRef.value.dataURL);

            url = result.url;

            if ("thumbnail" in result) {
                thumbnailUrl = result.thumbnail.url;
            }

            progressRef.value = 1;
        } catch (error) {
            console.error(error);
        }
    } else if (mediaUrlRef.value.length > 0) {
        url = mediaUrlRef.value;
    }

    let location = null;
    let createdDate = null;
    let media = null;

    if (longitudeRef.value.length > 0 && latitudeRef.value.length > 0 && isFinite(longitudeRef.value) && isFinite(latitudeRef.value)) {
        location = new Location(Number(longitudeRef.value), Number(latitudeRef.value));

        if (addressRef.value.length > 0) {
            location.address = addressRef.value;
        }
    }

    if (isFinite(timeYearRef.value) && isFinite(timeMonthRef.value) && isFinite(timeDayRef.value) && isFinite(timeHoursRef.value) && isFinite(timeMinutesRef.value) && isFinite(timeSecondsRef.value)) {
        createdDate = new Date(Number(timeYearRef.value), Number(timeMonthRef.value), Number(timeDayRef.value), Number(timeHoursRef.value), Number(timeMinutesRef.value), Number(timeSecondsRef.value));
    }

    if (url === null || typeRef.value === null || location === null || createdDate === null) {
        shake(event.currentTarget || event.target);
    } else {
        try {
            if (mediaIDRef.value === null) {
                media = await insertMedium(await getAccessToken(props.auth0), url, typeRef.value, categoriesRef.value, descriptionRef.value, props.user.email/*props.user.sub*/, location, createdDate, mediaDataTypesRef.value, mediaDataRef.value)
                media.thumbnailUrl = thumbnailUrl;
            } else {
                media = await updateMedium(await getAccessToken(props.auth0), mediaIDRef.value, url, typeRef.value, categoriesRef.value, descriptionRef.value, props.user.email/*props.user.sub*/, location, null, mediaDataTypesRef.value, mediaDataRef.value)
            }

            if (completed !== null) {
                completed();
            }

            emit("updated", event, media);
        } catch (error) {
            shake(event.currentTarget || event.target);
            console.error(error);
        }
    }

    isUploadingRef.value = false;
    progressRef.value = 0;
};
const uploadCompleted = () => {
    isUploadedRef.value = true;
    window.setTimeout(() => {
        isUploadedRef.value = false;
    }, 3000);
};
const requestDelete = (event) => {
    deleteConfirmation.visible = true;
    deleteConfirmation.dismiss = false;
};
const deleteItem = async (event) => {
    isDeletingRef.value = true;

    try {
        const media = await deleteMedium(await getAccessToken(props.auth0), mediaIDRef.value);

        if (media === null) {
            shake(deleteButtonRef.value);
        } else {
            emit("updated", event, null);
        }
    } catch (error) {
        shake(deleteButtonRef.value);
        console.error(error);
    }

    isDeletingRef.value = false;
};
const initialize = async () => {
    isInitializedRef.value = true;

    const loader = new Loader({
        apiKey: GoogleMapsConfig.API_KEY,
        version: GoogleMapsConfig.VERSION,
        language: navigator.language,
    });

    await loader.load();

    map = new google.maps.Map(mapRef.value, GoogleMapsConfig.MAP_OPTIONS);
    map.addListener("center_changed", () => {
        const location = map.getCenter();

        latitudeRef.value = String(location.lat());
        longitudeRef.value = String(location.lng());
    });
    geocoder = new google.maps.Geocoder();

    if (props.media === null) {
        if ("permissions" in navigator) {
            const permissionStatus = await navigator.permissions.query({ name: "geolocation" });

            if (permissionStatus.state == "granted" || permissionStatus.state == "prompt") {
                isLocatingRef.value = true;
                navigator.geolocation.getCurrentPosition((position) => {
                    isLocatingRef.value = false;
                    latitudeRef.value = String(position.coords.latitude);
                    longitudeRef.value = String(position.coords.longitude)
                    map.setCenter(
                        new google.maps.LatLng(
                            position.coords.latitude,
                            position.coords.longitude
                        )
                    );
                }, (error) => {
                    isLocatingRef.value = false;
                    console.error(error);
                }, {
                    enableHighAccuracy: true,
                    timeout: 30000,
                    maximumAge: 0
                });
            }
        } else {
            isLocatingRef.value = true;

            navigator.geolocation.getCurrentPosition((position) => {
                isLocatingRef.value = false;
                latitudeRef.value = String(position.coords.latitude);
                longitudeRef.value = String(position.coords.longitude)
                map.setCenter(
                    new google.maps.LatLng(
                        position.coords.latitude,
                        position.coords.longitude
                    )
                );
            }, (error) => {
                isLocatingRef.value = false;
                console.error(error);
            }, {
                enableHighAccuracy: true,
                timeout: 30000,
                maximumAge: 0
            });
        }
    } else {
        map.setCenter(
            new google.maps.LatLng(
                props.media.location.latitude,
                props.media.location.longitude
            )
        );

        longitudeRef.value = String(props.media.location.longitude);
        latitudeRef.value = String(props.media.location.latitude);
    }
};

onMounted(async () => {
    initialize();

    if (mediaIDRef.value !== null) {
        const media = await getMedium(mediaIDRef.value);

        if ("dataTypes" in media && media.dataTypes !== null) {
                mediaDataTypesRef.value = [];
            
            for (const type of media.dataTypes) {
                mediaDataTypesRef.value.push(type);
            }
        }

        if ("data" in media && media.data !== null) {
            mediaDataRef.value = [];

            for (const mediaDataItem of media.data) {
                mediaDataRef.value.push({ id: mediaDataItem.id, values: mediaDataItem.values, time: mediaDataItem.time, location: new Location(mediaDataItem.location.longitude, mediaDataItem.location.latitude, mediaDataItem.location.address !== null && mediaDataItem.location.address.length > 0 ? mediaDataItem.location.address : null) });
            }
        }
    }
});
onUnmounted(() => {
    isInitializedRef.value = false;
});
onActivated(async () => {
    if (!isInitializedRef.value) {
        initialize();
    }

    if (mediaIDRef.value !== null) {
        const media = await getMedium(mediaIDRef.value);

        if ("dataTypes" in media && media.dataTypes !== null) {
                mediaDataTypesRef.value = [];
            
            for (const type of media.dataTypes) {
                mediaDataTypesRef.value.push(type);
            }
        }

        if ("data" in media && media.data !== null) {
            mediaDataRef.value = [];

            for (const mediaDataItem of media.data) {
                mediaDataRef.value.push({ id: mediaDataItem.id, values: mediaDataItem.values, time: mediaDataItem.time, location: new Location(mediaDataItem.location.longitude, mediaDataItem.location.latitude, mediaDataItem.location.address !== null && mediaDataItem.location.address.length > 0 ? mediaDataItem.location.address : null) });
            }
        }
    }
});
onDeactivated(() => { });
watch(mediaUrlRef, (currentValue, oldValue) => {
    if (currentValue !== null) {
        mediaFileRef.value = null;
        mediaDataTypesRef.value = null;
        mediaDataRef.value = null;
    }
});
</script>

<template>
    <div id="uploader">
        <div class="flyout-left">
            <div class="wrap">
                <div class="block">
                    <nav class="panel">
                        <div class="panel-block">
                            <nav class="level is-mobile">
                                <div class="level-left">
                                    <div class="level-item">
                                        <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                                            Media
                                        </h3>
                                    </div>
                                    <transition name="fade" mode="out-in">
                                        <div class="level-item"
                                            v-show="mediaIDRef === null && (mediaFileRef !== null || mediaUrlRef.length > 0)"
                                            key="attaced">
                                            <span class="icon is-primary">
                                                <i class="fa-solid fa-check"></i>
                                            </span>
                                        </div>
                                    </transition>
                                    <transition name="fade" mode="out-in">
                                        <div class="level-item" v-show="mediaDataRef !== null" key="data">
                                            <span class="icon">
                                                <i class="fa-solid fa-table"></i>
                                            </span>
                                        </div>
                                    </transition>
                                    <div class="level-item" v-if="mediaIDRef !== null">
                                        <span class="is-size-7 has-text-weight-bold has-text-grey"
                                            v-text="mediaIDRef"></span>
                                    </div>
                                </div>
                                <div class="level-right">
                                    <div class="level-item" v-if="mediaIDRef !== null">
                                        <a class="button is-rounded" target="_blank" v-bind:href="mediaUrlRef"><span
                                                class="icon is-small"><i class="fa-solid fa-link"></i></span></a>
                                    </div>
                                    <div class="level-item is-invisible" v-else>
                                        <button class="button toggle is-rounded"
                                            @click="mediaIsCollapsedRef = !mediaIsCollapsedRef">
                                            <span class="icon is-small" v-bind:class="{ collapsed: mediaIsCollapsedRef }">
                                                <i class="fa-solid fa-chevron-up"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <template v-if="mediaIDRef === null">
                                <transition name="fade" mode="out-in">
                                    <div class="block" v-show="!mediaIsCollapsedRef" key="collapse">
                                        <div class="control">
                                            <div class="drop"
                                                v-bind:style="{ animationPlayState: isDraggingRef ? 'running' : 'paused', pointerEvents: typesIsLoadingRef ? 'none' : 'auto' }"
                                                @dragover.prevent="dragover($event)"
                                                @dragleave.prevent="isDraggingRef = false"
                                                @drop.stop.prevent="drop($event)">
                                                <transition name="fade" mode="out-in">
                                                    <div class="image" v-if="mediaFileRef === null" v-bind:key="null">
                                                        <div class="level">
                                                            <div class="level-item">
                                                                <label
                                                                    class="file button is-circle has-text-weight-bold file-label">
                                                                    <input class="file-input" type="file" name="upload"
                                                                        style="pointer-events: none"
                                                                        v-bind:disabled="isFetchingRef || isLoadingRef || typesIsLoadingRef"
                                                                        @change="browse($event)" />
                                                                    <div class="file-cta_">
                                                                        <span class="icon">
                                                                            <i class="fa-solid fa-file"></i>
                                                                        </span>
                                                                    </div>
                                                                </label>
                                                            </div>
                                                            <div class="level-item">
                                                                <span
                                                                    class="is-size-7 is-uppercase has-text-weight-bold has-text-centered has-text-grey">Browse
                                                                    or Drag & Drop</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div class="image" v-else v-bind:key="mediaFileRef.filename">
                                                        <transition name="fade" mode="out-in">
                                                            <div class="image" v-if="mediaPreviewRef !== null"
                                                                :key="mediaFileRef.filename">
                                                                <picture class="image">
                                                                    <img v-bind:src="mediaPreviewRef"
                                                                        v-bind:alt="mediaFileRef.filename" />
                                                                </picture>
                                                                <div class="control">
                                                                    <button class="button is-circle" type="button"
                                                                        @click="resetMedia($event)" key="menu">
                                                                        <span class="icon is-small has-text-danger">
                                                                            <i class="fa-solid fa-xmark"></i>
                                                                        </span>
                                                                    </button>
                                                                </div>
                                                            </div>
                                                            <div class="image" v-else :key="null">
                                                                <div class="level">
                                                                    <div class="level-item">
                                                                        <label
                                                                            class="file button is-circle has-text-weight-bold file-label">
                                                                            <input class="file-input" type="file"
                                                                                name="upload" style="pointer-events: none"
                                                                                v-bind:disabled="isFetchingRef || isLoadingRef"
                                                                                @change="browse($event)" />
                                                                            <div class="file-cta_">
                                                                                <span class="icon">
                                                                                    <i class="fa-solid fa-file"></i>
                                                                                </span>
                                                                            </div>
                                                                        </label>
                                                                    </div>
                                                                    <div class="level-item">
                                                                        <span
                                                                            class="is-size-7 has-text-weight-bold has-text-centered has-text-grey">{{
                                                                                mediaFileRef.filename
                                                                            }}</span>
                                                                    </div>
                                                                </div>
                                                                <div class="control">
                                                                    <button class="button is-circle" type="button"
                                                                        @click="resetMedia($event)" key="menu">
                                                                        <span class="icon is-small has-text-danger">
                                                                            <i class="fa-solid fa-xmark"></i>
                                                                        </span>
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        </transition>
                                                    </div>
                                                </transition>
                                            </div>
                                        </div>
                                    </div>
                                </transition>
                            </template>
                            <template v-else-if="props.media.type.startsWith('image')">
                                <div class="image">
                                    <picture class="image">
                                        <img v-bind:src="'thumbnailUrl' in props.media && props.media.thumbnailUrl !== null ? props.media.thumbnailUrl : props.media.url" v-bind:alt="props.media.id" />
                                    </picture>
                                </div>
                            </template>
                            <transition name="fade" mode="out-in">
                                <div class="block" v-show="!mediaIsCollapsedRef" key="collapse">
                                    <div class="field has-addons">
                                        <div class="control is-expanded">
                                            <input class="input is-size-7 has-text-weight-bold" type="text"
                                                placeholder="URL" v-bind:disabled="mediaIDRef !== null"
                                                v-model="mediaUrlRef" />
                                        </div>
                                        <div class="control" v-if="mediaIDRef === null">
                                            <button type="button" class="button" v-bind:disabled="mediaIDRef !== null"
                                                @click="pasteImageUrl($event)">
                                                <span class="icon is-small">
                                                    <i class="fa-solid fa-paste"></i>
                                                </span>
                                            </button>
                                        </div>
                                        <div class="control" v-if="mediaIDRef === null">
                                            <button type="button" class="button"
                                                v-bind:disabled="mediaIDRef !== null || mediaUrlRef.length === 0"
                                                @click="clearImageUrl($event)">
                                                <span class="icon is-small has-text-danger">
                                                    <i class="fa-solid fa-xmark"></i>
                                                </span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </transition>
                        </div>
                        <div class="panel-block">
                            <nav class="level is-mobile">
                                <div class="level-left">
                                    <div class="level-item">
                                        <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                                            Description
                                        </h3>
                                    </div>
                                </div>
                                <div class="level-right">
                                    <div class="level-item">
                                        <button class="button is-rounded" @click="pasteDescription">
                                            <span class="icon is-small">
                                                <i class="fa-solid fa-paste"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <div class="block">
                                <div class="field">
                                    <div class="control">
                                        <textarea class="textarea is-small" placeholder="Enter a description"
                                            v-model="descriptionRef"></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <ListBox name="Types" :page-length="maxTypesLength" :is-enabled="user !== null && isInitializedRef"
                            :is-collapsed="typesIsCollapsedRef" :is-continuous="typesIsContinuousRef" :items="typesItemsRef"
                            :page-index="typesPageIndexRef" :is-badge-visible="false" @collapse="collapseTypes"
                            @clear="clearTypes" @select="selectType" @next="nextTypes" @previous="previousTypes" />
                    </nav>
                </div>
            </div>
        </div>
        <div class="flyout-left">
            <div class="wrap">
                <div class="block">
                    <nav class="panel">
                        <div class="panel-block">
                            <nav class="level is-mobile">
                                <div class="level-left">
                                    <div class="level-item">
                                        <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                                            Location
                                        </h3>
                                    </div>
                                </div>
                                <div class="level-right">
                                    <div class="level-item">
                                        <button class="button is-rounded" v-bind:disabled="user === null || isLocatingRef"
                                            @click="locate">
                                            <transition name="fade" mode="out-in">
                                                <span class="icon" v-if="isLocatingRef" key="locating">
                                                    <i class="fas fa-spinner updating"></i>
                                                </span>
                                                <span class="icon is-small" v-else key="ready">
                                                    <i class="fa-solid fa-location-arrow"></i>
                                                </span>
                                            </transition>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <div class="field">
                                <nav class="level is-mobile">
                                    <div class="level-left">
                                        <div class="level-item">
                                            <span
                                                class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Longitude</span>
                                        </div>
                                    </div>
                                    <div class="level-right">
                                        <div class="level-item">
                                            <input class="input is-size-7 is-outlined has-text-weight-bold has-text-right"
                                                type="text" size="16" placeholder="Enter a longitude"
                                                v-bind:class="{ 'has-error': hasLocationErrorRef }" v-model="longitudeRef"
                                                @change="longitudeChange" />
                                        </div>
                                    </div>
                                </nav>
                            </div>
                            <div class="field">
                                <nav class="level is-mobile">
                                    <div class="level-left">
                                        <div class="level-item">
                                            <span
                                                class="is-size-7 is-uppercase has-text-weight-bold has-text-grey no-spin">Latitude</span>
                                        </div>
                                    </div>
                                    <div class="level-right">
                                        <div class="level-item">
                                            <input class="input is-size-7 is-outlined has-text-weight-bold has-text-right"
                                                type="text" size="16" placeholder="Enter a latitude"
                                                v-bind:class="{ 'has-error': hasLocationErrorRef }" v-model="latitudeRef"
                                                @change="latitudeChange" />
                                        </div>
                                    </div>
                                </nav>
                            </div>
                            <div class="block">
                                <div class="field has-addons">
                                    <div class="control is-expanded">
                                        <input class="input is-size-7 has-text-weight-bold" type="text"
                                            placeholder="Address" v-model="addressRef" />
                                    </div>
                                    <div class="control">
                                        <button type="button" class="button" @click="geocode($event)">
                                            <span class="icon is-small">
                                                <i class="fa-solid fa-location-crosshairs"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="panel-block">
                            <nav class="level is-mobile">
                                <div class="level-left">
                                    <div class="level-item">
                                        <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                                            Time
                                        </h3>
                                    </div>
                                </div>
                                <div class="level-right">
                                    <div class="level-item">
                                        <button class="button is-rounded" @click="resetTime">
                                            <span class="icon is-small">
                                                <i class="fa-solid fa-clock"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <div class="block">
                                <div class="field">
                                    <div class="control">
                                        <input class="input is-size-7 has-text-weight-bold" type="date"
                                            v-bind:class="{ 'has-error': hasTimeErrorRef }" v-bind:disabled="!isInitializedRef" v-bind:value="(Array(4).join('0') + timeYearRef).slice(-4) + '-' + (Array(2).join('0') + (timeMonthRef + 1)).slice(-2) + '-' + (Array(2).join('0') + timeDayRef).slice(-2)"
                                            @change="timeDateChange" />
                                        <div class="select is-normal">
                                            <select class="is-size-7 has-text-weight-bold"
                                                v-bind:class="{ 'has-error': hasTimeErrorRef }"
                                                v-bind:disabled="!isInitializedRef" @change="timeHoursChange">
                                                <option v-for="i in [...Array(24).keys()]" v-bind:key="i"
                                                    v-bind:selected="i === timeHoursRef" v-text="i"></option>
                                            </select>
                                        </div>
                                        <span class="is-size-7 is-uppercase has-text-weight-bold">:</span>
                                        <div class="select is-normal">
                                            <select class="is-size-7 has-text-weight-bold"
                                                v-bind:class="{ 'has-error': hasTimeErrorRef }"
                                                v-bind:disabled="!isInitializedRef" @change="timeMinutesChange">
                                                <option v-for="i in [...Array(60).keys()]" v-bind:key="i"
                                                    v-bind:selected="i === timeMinutesRef" v-text="i"></option>
                                            </select>
                                        </div>
                                        <span class="is-size-7 is-uppercase has-text-weight-bold">:</span>
                                        <div class="select is-normal">
                                            <select class="is-size-7 has-text-weight-bold"
                                                v-bind:class="{ 'has-error': hasTimeErrorRef }"
                                                v-bind:disabled="!isInitializedRef" @change="timeSecondsChange">
                                                <option v-for="i in [...Array(60).keys()]" v-bind:key="i"
                                                    v-bind:selected="i === timeSecondsRef" v-text="i"></option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <ListBox name="Categories" :page-length="maxCategoriesLength"
                            :is-enabled="user !== null && isInitializedRef" :is-collapsed="categoriesIsCollapsedRef"
                            :is-continuous="categoriesIsContinuousRef" :items="categoriesItemsRef"
                            :page-index="categoriesPageIndexRef" @collapse="collapseCategories" @clear="clearCategories"
                            @select="selectCategory" @next="nextCategories" @previous="previousCategories" />
                    </nav>
                </div>
            </div>
            <div class="bottom">
                <div class="block">
                    <div class="panel-block">
                        <div class="control">
                            <button class="button is-rounded is-outlined is-fullwidth is-size-7 is-primary" type="submit"
                                v-bind:disabled="user === null || isUploadingRef || isDeletingRef || mediaFileRef === null && (mediaUrlRef.length === 0 || !mediaUrlRef.toLowerCase().startsWith('https://')) || !typesItemsRef.some(x => x.checked) || longitudeRef.length === 0 || latitudeRef.length === 0"
                                @click="upload($event, uploadCompleted)">
                                <transition name="fade" mode="out-in">
                                    <span class="icon" v-if="isUploadedRef" key="uploaded">
                                        <i class="fa-solid fa-check"></i>
                                    </span>
                                    <span class="icon" v-else-if="isUploadingRef" key="uploading">
                                        <i class="fas fa-spinner updating"></i>
                                    </span>
                                    <span class="icon" v-else key="ready">
                                        <i class="fa-solid fa-cloud-arrow-up"></i>
                                    </span>
                                </transition>
                                <span class="is-uppercase has-text-weight-bold">Save</span>
                            </button>
                        </div>
                    </div>
                    <div class="panel-block" v-if="props.isDeletable">
                        <div class="control">
                            <button class="button is-rounded is-outlined is-fullwidth is-size-7 is-danger" type="submit"
                                v-bind:disabled="user === null || isUploadingRef || isDeletingRef"
                                @click="requestDelete($event)" ref="deleteButtonRef">
                                <transition name="fade" mode="out-in">
                                    <span class="icon" v-if="isDeletingRef" key="deleting">
                                        <i class="fas fa-spinner updating"></i>
                                    </span>
                                    <span class="icon" v-else key="ready">
                                        <i class="fa-solid fa-trash"></i>
                                    </span>
                                </transition>
                                <span class="is-uppercase has-text-weight-bold">Delete</span>
                            </button>
                        </div>
                    </div>
                    <div class="panel-block" v-if="props.isClosable">
                        <div class="control">
                            <button class="button is-rounded is-outlined is-fullwidth is-size-7" v-bind:disabled="user === null" @click="close($event)">
                                <span class="icon">
                                    <i class="fa-solid fa-xmark"></i>
                                </span>
                                <span class="is-uppercase has-text-weight-bold">Close</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div id="map">
            <div class="content" ref="mapRef"></div>
            <div class="crosshairs icon"><i class="fa-solid fa-crosshairs"></i></div>
        </div>
        <div class="right is-hidden" v-if="props.isClosable">
            <button class="button is-primary" type="button" @click="close($event)">
                <span class="icon is-small">
                    <i class="fa-solid fa-xmark"></i>
                </span>
            </button>
        </div>
        <div class="modal" :class="{ 'is-active': deleteConfirmation.visible }">
            <transition name="fade" mode="out-in">
                <div class="modal-background" v-if="deleteConfirmation.visible && !deleteConfirmation.dismiss"
                    key="background"></div>
            </transition>
            <div class="wrap" @animationend="deleteConfirmation.visible = $event.srcElement.className !== 'wrap'"
                :style="{ animationPlayState: deleteConfirmation.dismiss ? 'running' : 'paused' }">
                <div class="modal-card" :style="{ animationPlayState: deleteConfirmation.visible ? 'running' : 'paused' }"
                    v-if="deleteConfirmation.visible" key="alert">
                    <header class="modal-card-head">
                        <p class="modal-card-title is-uppercase is-size-7 has-text-weight-bold">Confirmation</p>
                    </header>
                    <section class="modal-card-body">
                        <p class="modal-card-title is-size-7">Are you sure you wanto to delete
                            this?</p>
                    </section>
                    <footer class="modal-card-foot">
                        <div class="field">
                            <div class="control">
                                <button class="button is-danger"
                                    @click="deleteConfirmation.dismiss = true; deleteItem($event);">
                                    <span class="icon">
                                        <i class="fa-solid fa-trash"></i>
                                    </span>
                                    <span class="is-uppercase has-text-weight-bold">Delete</span>
                                </button>
                            </div>
                            <div class="control">
                                <button class="button" @click=" deleteConfirmation.dismiss = true;">
                                    <span class="icon">
                                        <i class="fa-solid fa-xmark"></i>
                                    </span>
                                    <span class="is-uppercase has-text-weight-bold">Cancel</span>
                                </button>
                            </div>
                        </div>
                    </footer>
                </div>
            </div>
        </div>
        <transition name="fade">
            <div class="progress" v-if="progressRef > 0" v-cloak>
                <div class="bar animating" v-bind:style="{ width: String(Math.floor(100.0 * progressRef)) + '%' }">
                </div>
            </div>
        </transition>
    </div>
</template>

<style lang="scss" scoped>
#uploader {
    position: absolute;
    display: flex;
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    flex-direction: row;
    align-items: flex-start;
    justify-content: flex-start;
    background: transparent;

    #map {
        display: flex;
        position: relative;
        width: 100%;
        /*aspect-ratio: 1 / 1;*/
        height: 100%;
        justify-content: center;
        align-items: center;
        background: #f5f5f5;

        button {
            border-radius: 0 !important;
        }

        .content {
            display: block;
            position: relative;
            margin: 0;
            width: 100%;
            height: 100%;
        }

        .crosshairs {
            display: block;
            position: absolute;
            margin: 0;
            width: 1.0rem;
            height: 1.0rem;
            font-size: 1.0rem;
            line-height: 1.0rem;
            left: 50%;
            right: 50%;
            top: 50%;
            transform-origin: 0% 0%;
            transform: translate(-50%, -50%);
            color: var(--accent-color);
        }
    }

    .flyout-left:nth-of-type(1)>.wrap>.block>.panel {
        >.panel-block:nth-of-type(1) {
            border-bottom: 0px none transparent;

            >nav.level {
                background: hsl(0, 0%, 96%);
            }

            .block:nth-of-type(1) {
                border-top: 1px solid hsl(0deg, 0%, 93%);
                padding-top: 0.5em !important;
            }
        }

        >.panel-block:nth-of-type(2) {
            /*>nav.level {
                background: hsl(0, 0%, 96%);
            }*/

            .block:nth-of-type(1) {
                /*border-top: 1px solid hsl(0deg, 0%, 93%);*/
                padding-top: 0.5em !important;
            }
        }
    }

    .flyout-left:nth-of-type(2)>.wrap>.block>.panel {
        >.panel-block:nth-of-type(1) {
            >nav.level {
                background: hsl(0, 0%, 96%);
            }

            >.field:nth-of-type(1) {
                border-top: 1px solid hsl(0deg, 0%, 93%);
                padding-top: 0.5em !important;
            }
        }

        >.panel-block:nth-of-type(2) {
            >nav.level {
                background: hsl(0, 0%, 96%);
            }

            .block:nth-of-type(1) {
                border-top: 1px solid hsl(0deg, 0%, 93%);
                padding-top: 0.5em !important;
            }
        }
    }

    .flyout-left,
    .flyout-right {
        position: relative;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-end;
        top: 0px;
        margin: 0;
        border-right: 1px solid hsl(0deg, 0%, 93%);
        padding: 0px;
        width: fit-content;
        height: 100%;
        max-height: 100%;
        background: transparent;

        >.wrap {
            flex-basis: auto;
            width: fit-content;
            height: 100%;
            max-height: 100%;
            overflow-x: hidden;
            overflow-y: auto;

            >.block {
                width: 320px;
                height: fit-content;

                .panel {
                    background: transparent;
                    border-radius: 4px;
                    box-shadow: none;

                    .panel-block {
                        flex-direction: column;
                        padding: 0;

                        >.block {
                            margin: 0;
                            padding: 0em 0.75em;
                            width: 100%;

                            >.field.has-addons {
                                background: #ffffff;
                            }
                        }

                        >.block:first-of-type:last-of-type {
                            margin: 0;
                            padding: 0em 0.75em 0.5em 0.75em;
                            width: 100%;
                        }

                        >#map {
                            margin-top: 0.5em;
                        }

                        >.block:last-child {
                            margin: 0;
                            padding: 0.5em 0.75em;
                        }

                        >.level {
                            margin: 0;
                            padding: 0em 0.75em;
                            width: 100%;

                            >.level-left>.level-item>.panel-heading {
                                margin: 0 !important;
                                padding: 0;
                                background: transparent;
                            }

                            >.level-right {
                                margin: 0px 0px 0px 12px;

                                button,
                                .button {
                                    background: transparent !important;
                                }

                                button.is-rounded,
                                .button.is-rounded {
                                    border-radius: 9999px !important;
                                    padding: 12px !important;
                                    box-shadow: none !important;

                                    >span.icon {
                                        margin: 0 !important;
                                        width: 1rem !important;
                                        height: 1rem !important;
                                    }
                                }

                                button.toggle {
                                    >span {
                                        transform: rotate(180deg);
                                    }

                                    >span.collapsed {
                                        transition: transform 0.5s ease;
                                        transform: rotate(0deg);
                                    }
                                }
                            }
                        }

                        >.field {
                            padding: 0em 0.75em;

                            >.level .level-item {
                                input {
                                    background: #ffffff;
                                    color: #000000
                                }
                            }
                        }

                        .field:not(:last-of-type):first-of-type {
                            margin-bottom: 0em;
                        }

                        .field:not(:last-of-type):not(:first-of-type) {
                            margin-top: 0.5em;
                            margin-bottom: 0em;
                        }
                    }

                    .panel-tabs:not(:last-child),
                    .panel-block:not(:last-child) {
                        border-bottom: 1px solid hsl(0deg, 0%, 93%);

                        .drop {
                            display: flex;
                            margin: 0;
                            padding: 4px;
                            width: 100%;
                            aspect-ratio: 16 / 9;
                            border-radius: 4px;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            background: linear-gradient(90deg,
                                    hsl(0deg, 0%, 93%) 50%,
                                    transparent 50%),
                                linear-gradient(90deg, hsl(0deg, 0%, 93%) 50%, transparent 50%),
                                linear-gradient(0deg, hsl(0deg, 0%, 93%) 50%, transparent 50%),
                                linear-gradient(0deg, hsl(0deg, 0%, 93%) 50%, transparent 50%);
                            background-repeat: repeat-x, repeat-x, repeat-y, repeat-y;
                            background-size: 16px 4px, 16px 4px, 4px 16px, 4px 16px;
                            background-position: 0% 0%, 100% 100%, 0% 100%, 100% 0px;
                            animation: selecting 10s linear infinite;
                            animation-play-state: paused;
                            overflow: hidden;

                            div.image {
                                display: flex;
                                margin: 0;
                                border-radius: 4px;
                                padding: 0;
                                width: 100%;
                                height: 100%;
                                background-position: 50% 50%;
                                background-size: contain;
                                background-repeat: no-repeat;
                                flex-direction: column;
                                align-items: center;
                                justify-content: center;
                                overflow: hidden;
                                image-rendering: -webkit-optimize-contrast;

                                >picture {
                                    height: 100%;
                                    border-radius: 4px;
                                    overflow: hidden;

                                    >img {
                                        object-fit: cover;
                                        height: 100%;
                                    }
                                }

                                label {
                                    transition: 0.5s;
                                }

                                label:hover {
                                    background-color: hsl(0deg, 0%, 93%, 0.75);
                                    transition: 0.5s;
                                }

                                .control {
                                    position: absolute;
                                    top: 0;
                                    right: 0;
                                    margin: 4px 4px 0px 0px;
                                    width: auto !important;
                                }

                                .level {
                                    display: flex;
                                    margin: 0;
                                    padding: 0.5em 0.75em;
                                    flex-direction: column;
                                    align-items: center;
                                    justify-content: center;

                                    .level-item:not(:last-child) {
                                        margin: 0px 0px 6px 0px;
                                        padding: 0;
                                    }
                                }
                            }

                            .button {
                                box-shadow: none !important;
                            }

                            button.is-circle,
                            .button.is-circle {
                                margin: 0px;
                                padding: 16px !important;
                                height: initial;
                                border-radius: 290486px;

                                span {
                                    margin: 0 !important;
                                    width: 0.75rem !important;
                                    height: 0.75rem !important;
                                    color: var(--accent-color);
                                }
                            }

                            button.is-primary.is-circle,
                            .button.is-primary.is-circle {
                                border-radius: 290486px;
                                overflow: hidden;
                                background-color: var(--primary-background-color) !important;
                                color: #ffffff !important;
                                transition: 0.5s;

                                span {
                                    color: #ffffff !important;
                                }
                            }
                        }
                    }
                }

                button {
                    border-radius: 4px;
                    box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
                        0 0px 0 1px rgb(10 10 10 / 2%) !important;
                }
            }

            >.block.wide {
                width: 801px !important;
            }
        }

        >.block {
            width: 320px;
            height: fit-content;

            .panel {
                background: transparent;
                border-radius: 4px;
                box-shadow: none;
            }
        }

        >.block.wide {
            width: 801px !important;
        }

        >.block {
            width: fit-content;
            height: 100%;

            >.panel {
                width: fit-content;
                height: 100%;
            }
        }

        >.top {
            .panel-block:first-child {
                border-bottom: 1px solid hsl(0deg, 0%, 93%);
                border-radius: 0px;
            }
        }

        >.bottom {
            .panel-block {
                border-top: 1px solid hsl(0deg, 0%, 93%);
                border-bottom: 0px none transparent;
                border-radius: 0px;
                padding: 0.5em 0.75em;

                .is-danger {
                    background-color: hsl(348, 100%, 61%) !important;
                    color: #ffffff !important;
                    transition: 0.5s;

                    span {
                        color: #ffffff !important;
                    }
                }
            }
        }

        >.top,
        >.bottom {
            flex-shrink: 0;
            width: 100%;
            height: fit-content;
            min-height: fit-content;
            overflow-x: hidden;
            overflow-y: hidden;
            box-sizing: border-box;

            >.block {
                width: 320px;
                height: fit-content;

                .panel {
                    background: transparent;
                    border-radius: 4px;
                    box-shadow: none;

                    .panel-block {
                        display: flex;
                        flex-direction: row;
                        justify-content: flex-start;
                        align-items: flex-end;
                    }
                }

                button {
                    box-sizing: border-box;
                    border-radius: 4px;
                    height: fit-content;
                    box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
                        0 0px 0 1px rgb(10 10 10 / 2%) !important;
                }
            }

            >.block.wide {
                width: 801px !important;
            }
        }

        >.top+.block {
            width: fit-content;
            height: 100%;

            >nav.panel {
                width: fit-content;
                height: 100%;
            }
        }

        .field {
            width: 100%;

            input.is-outlined,
            select {
                border: 1px solid hsl(0deg, 0%, 93%) !important;
            }

            input.is-outlined.has-error,
            select.has-error {
                border-color: var(--error-color) !important;
            }

            input[type="text"] {
                margin: 0;
                border: 0px none transparent;
                padding: 16px 12px 16px 12px;
                background-color: transparent;
                box-shadow: none;
                backface-visibility: hidden;
                /*border: 1px solid hsl(0deg, 0%, 93%);*/
                color: #000000;
            }

            textarea {
                margin: 0;
                border: 1px solid hsl(0deg, 0%, 93%);
                padding: 12px 12px 12px 12px;
                background-color: #ffffff;
                box-shadow: none;
                color: #000000;
            }

            .textarea:not([rows]) {
                max-height: 40em;
                min-height: 20em;
            }

            input::placeholder,
            textarea::placeholder {
                color: rgba(0, 0, 0, 0.5);
                text-transform: uppercase;
                text-shadow: none;
            }

            button.is-rounded {
                border-radius: 9999px !important;
            }

            .control {
                margin: 0;
                display: flex;
                justify-content: flex-end;
                align-items: center;

                >input[type="number"] {
                    background: #ffffff;
                    font-size: 0.75rem !important;
                    width: calc(calc(0.75rem * 4) + calc(calc(0.75em - 1px) * 2));
                }

                >input:is([type="date"], [type="time"], [type="datetime-local"], [type="month"], [type="week"]) {
                    display: inline-block;
                    color: #000000;
                    margin: 0px 8px 0px 0px;
                    border: 1px solid hsl(0deg, 0%, 93%) !important;
                    background: #ffffff;
                    font-size: 0.75rem !important;
                    line-height: 0.75rem;
                    text-align: center;
                }

                >.select>select {
                    background: #ffffff;
                }

                >span {
                    margin: 0;
                    padding: 4px 2px 4px 2px;
                }
            }
        }

        .has-addons {
            margin: 0;
            border: 1px solid hsl(0deg, 0%, 93%);
            border-radius: 4px;

            .control>input {
                border: 0px none transparent;
            }

            .control>button {
                background: transparent;
                box-shadow: none !important;
            }
        }

        .control:not(:first-child) {
            margin: 0px 0px 0px 0.5rem;
        }
    }

    .flyout-right {
        position: absolute !important;
        right: 0px !important;
    }

    .right {
        position: absolute;
        right: 0;
        top: 0;
        margin: 16px 0px 0px 0px;
        padding: env(safe-area-inset-top, 0px) calc(env(safe-area-inset-right, 0px) + 16px) 0px 0px;
        touch-action: none;

        button {
            margin: 0px;
            border: 0px none transparent !important;
            padding: 12px !important;
            background: #ffffff !important;
            box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.1) !important;
            background-clip: padding-box;
            height: initial;
            color: #ffffff !important;

            >span.icon {
                margin: 0 !important;
                width: 1rem !important;
                height: 1rem !important;
            }
        }

        button.is-rounded,
        .button.is-rounded {
            padding: 16px;
        }

        button.is-circle,
        .button.is-circle {
            margin: 0px;
            padding: 16px !important;
            height: initial;
            border-radius: 290486px;

            span {
                margin: 0 !important;
                width: 0.75rem !important;
                height: 0.75rem !important;
                color: var(--accent-color);
            }
        }
    }

    .modal {
        .modal-background {
            background: rgba(0, 0, 0, 0.75);
        }

        .wrap {
            margin: 0;
            padding: 0;
            opacity: 1;
            transform: scale(1, 1);
            animation: popup .5s ease forwards reverse 1;
            animation-play-state: paused;

            .modal-card {
                border-radius: 4px;
                width: auto !important;
                opacity: 1;
                transform: scale(0.75, 0.75);
                animation: popup .5s ease forwards 1;
                animation-play-state: paused;

                >.modal-card-head {
                    margin: 0;
                    border-bottom: 0px none transparent;
                    border-radius: 0;
                    background: #ffffff;
                    padding: 0.5em 0.75em 0em 0.75em;

                    p {
                        color: var(--accent-color);
                    }
                }

                >.modal-card-body {
                    background: #ffffff !important;

                    p {
                        color: #000000;
                    }
                }

                section {
                    padding: 0.5em 0.75em;
                }

                >.modal-card-foot {
                    margin: 0;
                    border-top: 1px solid hsl(0deg, 0%, 93%);
                    border-radius: 0;
                    padding: 0;
                    background: #ffffff;

                    .field {
                        display: flex;
                        margin: 0;
                        padding: 0.5em 0.375em;
                        justify-content: space-between;
                        align-items: flex-start;
                        width: 100%;

                        .control {
                            margin: 0;
                            padding: 0em 0.375em;
                            width: 100%;
                        }

                        .button {
                            margin: 0;
                            width: 100%;
                        }

                        .button.is-danger {
                            background-color: hsl(348, 100%, 61%) !important;
                            color: #ffffff !important;
                            transition: 0.5s;

                            span {
                                color: #ffffff !important;
                            }
                        }
                    }
                }
            }
        }
    }
}

@keyframes selecting {
    to {
        background-position: 100% 0%, 0% 100%, 0% 0%, 100% 100%;
    }
}

::-webkit-full-page-media, :future, :root .class_name{
    /* ここに書く */
}
</style>
