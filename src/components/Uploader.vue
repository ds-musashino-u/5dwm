<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onActivated, onDeactivated, watch } from "vue";
import { getCategories } from "../presenters/categories.mjs";
import { getTypes } from "../presenters/types.mjs";
import { getMedia } from "../presenters/media.mjs";
import { Endpoints } from "../presenters/endpoints.mjs";
import { GoogleMapsConfig } from "../presenters/google-maps-config.mjs";
import ListBox from "./ListBox.vue";

const mapRef = ref(null);
let map = null;
const isActivatedRef = ref(false);
const isDraggingRef = ref(false);
const isLoading = ref(false);

const isUploadingRef = ref(false);
const isUpdating = ref(false);
const pictures = ref([]);

const mediaIsCollapsedRef = ref(false);
const mediaRef = ref(null);
const mediaUrlRef = ref("");
const maxCategoriesLength = 10;
const categoriesIsCollapsedRef = ref(false);
const categoriesIsContinuousRef = ref(false);
const categoriesItemsRef = ref([]);
const categoriesPageIndexRef = ref(0);
const maxTypesLength = 25;
const typesIsCollapsedRef = ref(false);
const typesIsContinuousRef = ref(false);
const typesItemsRef = ref([]);
const typesPageIndexRef = ref(0);
const props = defineProps({
    auth0: Object,
    user: Object,
    text: String,
});
const emit = defineEmits(["completed", "updated"]);
const dragover = (event) => {
    isDraggingRef.value = true;
    event.dataTransfer.dropEffect = "copy";
};
const drop = async (event) => {
    isDraggingRef.value = false;

    for (const file of event.dataTransfer.files) {
        isLoading.value = true;

        try {
            mediaUrlRef.value = "";
            mediaRef.value = {
                filename: file.name,
                type: file.type,
                dataURL: await new Promise(function (resolve, reject) {
                    const reader = new FileReader();

                    reader.addEventListener("load", (e) => {
                        resolve(e.target.result);
                    });
                    reader.addEventListener("error", (e) => {
                        reject(reader.error);
                    });
                    reader.readAsDataURL(file);
                }),
            };
        } catch (error) {
            console.error(error);
        }

        isLoading.value = false;

        return;
    }
};
const browse = async (event) => {
    for (const file of event.currentTarget.files) {
        isLoading.value = true;

        try {
            mediaUrlRef.value = "";
            mediaRef.value = {
                filename: file.name,
                type: file.type,
                dataURL: await new Promise(function (resolve, reject) {
                    const reader = new FileReader();

                    reader.onload = () => {
                        resolve(reader.result);
                    };
                    reader.onerror = () => {
                        reject(reader.error);
                    };
                    reader.readAsDataURL(file);
                }),
            };
        } catch (error) {
            console.error(error);
        }

        isLoading.value = false;

        return;
    }
};
const reset = (event) => {
    mediaRef.value = null;
};
const clearImageUrl = (event) => {
    mediaUrlRef.value = "";
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
    categoriesItemsRef.value[index].checked =
        !categoriesItemsRef.value[index].checked;
};
const selectType = (index) => {
    typesItemsRef.value[index].checked = !typesItemsRef.value[index].checked;
};
const nextCategories = async (pageIndex, pageLength, isFetchingRef) => {
    if (categoriesItemsRef.value.length <= pageIndex * maxCategoriesLength) {
        isFetchingRef.value = true;

        try {
            const items = await getCategories(
                pageIndex * maxCategoriesLength,
                pageLength
            );
            let length;

            if (items.length > maxCategoriesLength) {
                categoriesIsContinuousRef.value = true;
                length = maxCategoriesLength;
            } else {
                categoriesIsContinuousRef.value = false;
                length = items.length;
            }

            for (let i = 0; i < length; i++) {
                categoriesItemsRef.value.push({ checked: false, name: items[i].name });
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
        isFetchingRef.value = true;

        try {
            const items = await getTypes(
                null,
                null,
                pageIndex * maxTypesLength,
                pageLength
            );
            let length;

            if (items.length > maxTypesLength) {
                typesIsContinuousRef.value = true;
                length = maxTypesLength;
            } else {
                typesIsContinuousRef.value = false;
                length = items.length;
            }

            for (let i = 0; i < length; i++) {
                typesItemsRef.value.push({ checked: false, name: items[i] });
            }
        } catch (error) {
            console.error(error);
        }

        isFetchingRef.value = false;
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
const upload = async (event) => {
    isUploadingRef.value = true;

    for (const file of event.currentTarget.files) {
        try {
            const dataURL = await new Promise(function (resolve, reject) {
                const reader = new FileReader();

                reader.onload = () => {
                    resolve(reader.result);
                };
                reader.onerror = () => {
                    reject(reader.error);
                };
                reader.readAsDataURL(file);
            });

            const response = await fetch(
                "https://www.5dworldmap.com/api/v1/upload",
                {
                    mode: "cors",
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ image: dataURL }),
                }
            );

            if (response.ok) {
                console.log(await response.json());
            } else {
                throw new Error(response.statusText);
            }
        } catch (error) {
            console.error(error);
        }
    }

    isUploadingRef.value = false;

    emit("completed");
    update();
};
const update = async () => {
    isUpdating.value = true;

    try {
        const response = await fetch("https://www.5dworldmap.com/api/v1/recent", {
            mode: "cors",
            method: "GET",
        });

        if (response.ok) {
            pictures.value.splice(0);

            for (const item of await response.json()) {
                pictures.value.push(item);
            }
        } else {
            throw new Error(response.statusText);
        }
    } catch (error) {
        console.error(error);
    }

    isUpdating.value = false;

    emit("updated");
};

onActivated(async () => {
    isActivatedRef.value = true;

    update();

    const loader = new Loader({
        apiKey: GoogleMapsConfig.API_KEY,
        version: "quarterly",
        language: navigator.language,
    });

    await loader.load();

    map = new google.maps.Map(mapRef.value, {
        center: { lat: 35.6809591, lng: 139.7673068 },
        zoom: 4,
        mapTypeId: "terrain",
        zoomControl: true,
        mapTypeControl: false,
        scaleControl: true,
        streetViewControl: false,
        rotateControl: true,
        fullscreenControl: false,
    });
});
onDeactivated(() => {
    isActivatedRef.value = false;
});
watch(mediaUrlRef, (currentValue, oldValue) => {
    if (currentValue !== null) {
        mediaRef.value = null;
    }
});
</script>

<template>
    <div id="uploader">
        <div class="flyout-left">
            <div class="wrap">
                <div class="block is-hidden-mobile">
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
                                        <div class="level-item" v-show="mediaRef !== null || mediaUrlRef.length > 0"
                                            key="attaced">
                                            <span class="icon is-primary">
                                                <i class="fa-solid fa-check"></i>
                                            </span>
                                        </div>
                                    </transition>
                                </div>
                                <div class="level-right is-invisible">
                                    <div class="level-item">
                                        <button class="button toggle is-rounded"
                                            @click="mediaIsCollapsedRef = !mediaIsCollapsedRef">
                                            <span class="icon is-small"
                                                v-bind:class="{ collapsed: mediaIsCollapsedRef }">
                                                <i class="fa-solid fa-chevron-up"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <transition name="fade" mode="out-in">
                                <div class="block" v-show="!mediaIsCollapsedRef" key="collapse">
                                    <div class="control">
                                        <div class="drop" v-bind:style="{
                                            animationPlayState: isDraggingRef ? 'running' : 'paused',
                                        }" @dragover.prevent="dragover($event)" @dragleave.prevent="isDraggingRef = false"
                                            @drop.stop.prevent="drop($event)">
                                            <transition name="fade" mode="out-in">
                                                <div class="image" v-if="mediaRef === null" v-bind:key="null">
                                                    <div class="level">
                                                        <div class="level-item">
                                                            <label class="
                                file
                                button
                                is-circle
                                has-text-weight-bold
                                file-label
                              ">
                                                                <input class="file-input" type="file" name="upload"
                                                                    style="pointer-events: none"
                                                                    v-bind:disabled="isLoading"
                                                                    @change="browse($event)" />
                                                                <div class="file-cta_">
                                                                    <span class="icon">
                                                                        <i class="fa-solid fa-file"></i>
                                                                    </span>
                                                                </div>
                                                            </label>
                                                        </div>
                                                        <div class="level-item">
                                                            <span class="
                                is-size-7 is-uppercase
                                has-text-weight-bold has-text-grey
                              ">Browse or Drag & Drop</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div class="image" v-else v-bind:key="mediaRef">
                                                    <transition name="fade" mode="out-in">
                                                        <div class="image" v-if="mediaRef.type.startsWith('image/')"
                                                            key="image">
                                                            <picture class="image">
                                                                <img v-bind:src="mediaRef.dataURL"
                                                                    v-bind:alt="mediaRef.filename" />
                                                            </picture>
                                                            <div class="control">
                                                                <button class="button is-circle" type="button"
                                                                    @click="reset($event)" key="menu">
                                                                    <span class="icon is-small has-text-danger">
                                                                        <i class="fa-solid fa-xmark"></i>
                                                                    </span>
                                                                </button>
                                                            </div>
                                                        </div>
                                                        <div class="image" v-else :key="mediaRef.type">
                                                            <div class="level">
                                                                <div class="level-item">
                                                                    <label class="
                                file
                                button
                                is-circle
                                has-text-weight-bold
                                file-label
                              ">
                                                                        <input class="file-input" type="file"
                                                                            name="upload" style="pointer-events: none"
                                                                            v-bind:disabled="isLoading"
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
                                                                        class="is-size-7 has-text-weight-bold has-text-grey">{{
                                                                                mediaRef.filename
                                                                        }}</span>
                                                                </div>
                                                            </div>
                                                            <div class="control">
                                                                <button class="button is-circle" type="button"
                                                                    @click="reset($event)" key="menu">
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
                            <transition name="fade" mode="out-in">
                                <div class="block" v-show="!mediaIsCollapsedRef" key="collapse">
                                    <div class="field has-addons">
                                        <div class="control is-expanded">
                                            <input class="input is-size-7 has-text-weight-bold" type="text"
                                                placeholder="URL" v-model="mediaUrlRef" />
                                        </div>
                                        <div class="control">
                                            <button type="button" class="button"
                                                v-bind:disabled="mediaUrlRef.length === 0"
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
                                <div class="level-right is-invisible">
                                    <div class="level-item">
                                        <button class="button toggle is-rounded"
                                            @click="mediaIsCollapsedRef = !mediaIsCollapsedRef">
                                            <span class="icon is-small"
                                                v-bind:class="{ collapsed: mediaIsCollapsedRef }">
                                                <i class="fa-solid fa-chevron-up"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <div class="field">
                                <div class="control">
                                    <textarea class="textarea is-small" placeholder="Enter a description"></textarea>
                                </div>
                            </div>
                        </div>
                    </nav>
                </div>
            </div>
        </div>
        <div class="flyout-left">
            <div class="wrap">
                <div class="block is-hidden-mobile">
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
                                <div class="level-right is-invisible">
                                    <div class="level-item">
                                        <button class="button toggle is-rounded"
                                            @click="locationIsCollapsedRef = !locationIsCollapsedRef">
                                            <span class="icon is-small"
                                                v-bind:class="{ collapsed: locationIsCollapsedRef }">
                                                <i class="fa-solid fa-chevron-up"></i>
                                            </span>
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
                                            <input class="input is-size-7 is-outlined has-text-weight-bold" type="text"
                                                size="16" placeholder="Enter a longitude"
                                                v-bind:class="{ 'has-error': hasErrorRef }" v-bind:value="fromYearRef"
                                                @change="fromYearChange" />
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
                                            <input class="input is-size-7 is-outlined has-text-weight-bold" type="text"
                                                size="16" placeholder="Enter a latitude"
                                                v-bind:class="{ 'has-error': hasErrorRef }" v-bind:value="fromYearRef"
                                                @change="fromYearChange" />
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
                                        <button type="button" class="button" @click="clearImageUrl($event)">
                                            <span class="icon is-small">
                                                <i class="fa-solid fa-location-crosshairs"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div id="map">
                                <div class="content" ref="mapRef"></div><span class="crosshairs icon"><i
                                        class="fa-solid fa-crosshairs"></i></span>
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
                                <div class="level-right is-invisible">
                                    <div class="level-item">
                                        <button class="button toggle is-rounded"
                                            @click="mediaIsCollapsedRef = !mediaIsCollapsedRef">
                                            <span class="icon is-small"
                                                v-bind:class="{ collapsed: mediaIsCollapsedRef }">
                                                <i class="fa-solid fa-chevron-up"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <div class="field">
                                <div class="control">
                                    <input class="input is-size-7 is-outlined has-text-weight-bold" type="number"
                                        size="4" placeholder="Year" v-bind:class="{ 'has-error': hasErrorRef }"
                                        v-bind:disabled="!isEnabled" v-bind:value="fromYearRef"
                                        @change="fromYearChange" />
                                    <span class="is-size-7 is-uppercase has-text-weight-bold">/</span>
                                    <div class="select is-normal">
                                        <select class="is-size-7 has-text-weight-bold"
                                            v-bind:class="{ 'has-error': hasErrorRef }" v-bind:disabled="!isEnabled"
                                            @change="fromMonthChange">
                                            <option v-for="i in [...Array(12).keys()]" v-bind:key="i"
                                                v-bind:selected="i === fromMonthRef" v-text="i + 1"></option>
                                        </select>
                                    </div>
                                    <span class="is-size-7 is-uppercase has-text-weight-bold">/</span>
                                    <div class="select is-normal">
                                        <select class="is-size-7 has-text-weight-bold"
                                            v-bind:class="{ 'has-error': hasErrorRef }" v-bind:disabled="!isEnabled"
                                            @change="fromDayChange">
                                            <option v-for="i in [...Array(31).keys()]" v-bind:key="i"
                                                v-bind:selected="i + 1 === fromDayRef" v-text="i + 1"></option>
                                        </select>
                                    </div>
                                    <div class="select is-normal">
                                        <select class="is-size-7 has-text-weight-bold"
                                            v-bind:class="{ 'has-error': hasErrorRef }" v-bind:disabled="!isEnabled"
                                            @change="fromHoursChange">
                                            <option v-for="i in [...Array(24).keys()]" v-bind:key="i"
                                                v-bind:selected="i === fromHoursRef" v-text="i"></option>
                                        </select>
                                    </div>
                                    <span class="is-size-7 is-uppercase has-text-weight-bold">:</span>
                                    <div class="select is-normal">
                                        <select class="is-size-7 has-text-weight-bold"
                                            v-bind:class="{ 'has-error': hasErrorRef }" v-bind:disabled="!isEnabled"
                                            @change="fromMinutesChange">
                                            <option v-for="i in [...Array(60).keys()]" v-bind:key="i"
                                                v-bind:selected="i === fromMinutesRef" v-text="i"></option>
                                        </select>
                                    </div>
                                    <span class="is-size-7 is-uppercase has-text-weight-bold">:</span>
                                    <div class="select is-normal">
                                        <select class="is-size-7 has-text-weight-bold"
                                            v-bind:class="{ 'has-error': hasErrorRef }" v-bind:disabled="!isEnabled"
                                            @change="fromSecondsChange">
                                            <option v-for="i in [...Array(60).keys()]" v-bind:key="i"
                                                v-bind:selected="i === fromSecondsRef" v-text="i"></option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </nav>
                </div>
            </div>
        </div>
        <div class="flyout-left">
            <div class="wrap">
                <div class="block is-hidden-mobile">
                    <nav class="panel">
                        <ListBox name="Categories" :page-length="maxCategoriesLength"
                            :is-enabled="user !== null && isActivatedRef" :is-collapsed="categoriesIsCollapsedRef"
                            :is-continuous="categoriesIsContinuousRef" :items="categoriesItemsRef"
                            :page-index="categoriesPageIndexRef" @collapse="collapseCategories" @clear="clearCategories"
                            @select="selectCategory" @next="nextCategories" @previous="previousCategories" />
                        <ListBox name="Types" :page-length="maxTypesLength" :is-enabled="user !== null && isActivatedRef"
                            :is-collapsed="typesIsCollapsedRef" :is-continuous="typesIsContinuousRef"
                            :items="typesItemsRef" :page-index="typesPageIndexRef" @collapse="collapseTypes"
                            @clear="clearTypes" @select="selectType" @next="nextTypes" @previous="previousTypes" />
                    </nav>
                </div>
            </div>
            <div class="bottom">
                <div class="block">
                    <div class="panel-block">
                        <div class="control">
                            <button class="
                  button
                  is-rounded is-outlined is-fullwidth is-size-7 is-primary
                " type="submit" v-bind:disabled="user === null || isUploadingRef" @click="search()">
                                <transition name="fade" mode="out-in">
                                    <span class="icon" v-if="isUploadingRef" key="uploading">
                                        <i class="fas fa-spinner updating"></i>
                                    </span>
                                    <span class="icon" v-else key="ready">
                                        <i class="fa-solid fa-cloud-arrow-up"></i>
                                    </span>
                                </transition>
                                <span class="is-uppercase has-text-weight-bold">Upload</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
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
    background: #ffffff;

    #map {
        display: flex;
        position: relative;
        width: 100%;
        aspect-ratio: 1 / 1;
        justify-content: center;
        align-items: center;

        button {
            border-radius: 0 !important;
        }

        .content {
            display: block;
            position: relative;
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
            transform-origin: 0% 0%;
            transform: translate(-50%, -50%);
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
                width: 400px;
                height: fit-content;

                .panel {
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 8px;
                    box-shadow: none;

                    .panel-block {
                        flex-direction: column;
                        padding: 0;

                        >.block {
                            margin: 0;
                            padding: 0em 0.75em;
                            width: 100%;
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

                                button.is-rounded {
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
                            border-radius: 8px;
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
                                border-radius: 8px;
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
                                    border-radius: 8px;
                                    overflow: hidden;

                                    >img {
                                        object-fit: cover;
                                        height: 100%;
                                    }
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
                    border-radius: 8px;
                    box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
                        0 0px 0 1px rgb(10 10 10 / 2%) !important;
                }
            }

            >.block.wide {
                width: 801px !important;
            }
        }

        >.block {
            width: 400px;
            height: fit-content;

            .panel {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 8px;
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
            .panel-block:last-child {
                border-top: 1px solid hsl(0deg, 0%, 93%);
                border-radius: 0px;
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
                width: 400px;
                height: fit-content;

                .panel {
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 8px;
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
                    border-radius: 8px;
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

            input[type="text"] {
                margin: 0;
                border: 0px none transparent;
                padding: 16px 12px 16px 12px;
                background-color: transparent;
                box-shadow: none;
                backface-visibility: hidden;
                /*border: 1px solid hsl(0deg, 0%, 93%);*/
            }

            textarea {
                margin: 0;
                border: 1px solid hsl(0deg, 0%, 93%);
                padding: 12px 12px 12px 12px;
                background-color: transparent;
                box-shadow: none;
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

            .has-error {
                border-color: var(--error-color);
            }

            .control {
                margin: 0;
                display: flex;
                justify-content: flex-start;
                align-items: center;

                >input[type="number"] {
                    background: transparent;
                    font-size: 0.75rem !important;
                    width: calc(calc(0.75rem * 4) + calc(calc(0.75em - 1px) * 2));
                }

                >.select:nth-of-type(2):not(:last-of-type) {
                    margin: 0px 8px 0px 0px;
                    padding: 0;
                }

                >.select>select {
                    background: transparent;
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
}

@keyframes selecting {
    to {
        background-position: 100% 0%, 0% 100%, 0% 0%, 100% 100%;
    }
}
</style>
