<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onActivated, onDeactivated, watch } from "vue";
import { Endpoints } from "../presenters/endpoints.mjs";
import { search as searchWorldMap, ResultItem } from "../presenters/search.mjs";
import { getMedia } from "../presenters/media.mjs";
import { getCategories } from "../presenters/categories.mjs";
import { getTypes } from "../presenters/types.mjs";
import ListBox from "./ListBox.vue";

const isActivatedRef = ref(false);
const isEnabledRef = ref(true);
const isFetchingUsersRef = ref(false);
const pageIndexRef = ref(0);
const pageLengthRef = ref(10);
const isFetchingRef = ref(false);
const isContinuousRef = ref(true);
const totalCountRef = ref(0);
const isForwardingRef = ref(true);
const usersRef = ref([{ name: "All", checked: true }, { name: "Alice", checked: false }, { name: "Bob", checked: false }]);
const mediaRef = ref([{ name: "Foo", checked: false }, { name: "Bar", checked: false }, { name: "Baz", checked: false }]);
const isUpdatingMediaRef = ref(false);




const isDragging = ref(false);
const isLoading = ref(false);



const isUploadingRef = ref(false);

const pictures = ref([]);

const mediaIsCollapsedRef = ref(false);
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
const emit = defineEmits(["select", "completed", "updated"]);
const selectUser = (event, index) => {
    usersRef.value[index].checked = event.currentTarget.checked;

    if (index > 0) {
        if (event.currentTarget.checked) {
            usersRef.value[0].checked = false;
        } else {
            let isSelected = false;

            for (let i = 1; i < usersRef.value.length; i++) {
                if (index !== i && usersRef.value[i].checked) {
                    isSelected = true;
                }
            }

            if (!isSelected) {
                usersRef.value[0].checked = true;
            }
        }
    } else if (event.currentTarget.checked) {
        for (let i = 1; i < usersRef.value.length; i++) {
            usersRef.value[i].checked = false;
        }
    }
};
const selectMedia = (event, index) => {
    index =  pageIndexRef.value * props.pageLength + index;
    mediaRef.value[index].checked = (event.currentTarget || event.target).checked;

    for (let i = 0; i < mediaRef.value.length; i++) {
        if (index !== i && mediaRef.value[i].checked) {
            mediaRef.value[i].checked = false;
        }
    }

    emit("select", index);
};
const searchMedia = async () => {
    try {
        const idToken = await props.auth0.getIdTokenClaims();
        const [resultItems, totalCount] = await searchWorldMap(
            idToken.__raw,
            keywords,
            categories,
            types,
            users,
            image,
            time.from,
            time.to,
            "created_at",
            "desc",
            0,
            null
        );
        const bounds = new google.maps.LatLngBounds();
        let index = 0;

        Object.keys(cachedSearchResults).forEach((key) => {
            if (cachedSearchResults[key].loaded) {
                cachedSearchResults[key].layer.setMap(null);
            }

            delete cachedSearchResults[key];
        });

        isRooted.value = false;
        searchResults.splice(0);
        searchResultsRef.value.splice(0);
        searchTotalCountRef.value = resultItems.length;

        if (resultItems.some((x) => x.hasScore)) {
            resultItems.sort(
                (x, y) => (y.hasScore ? y.score : 0) - (x.hasScore ? x.score : 0)
            );
        }

        if (
            resultItems.length >
            searchPageIndexRef.value * searchPageLength + searchPageLength
        ) {
            for (const resultItem of resultItems.splice(0, searchPageLength)) {
                if (resultItem.media.location === null) {
                    searchResults.push({ marker: null, item: resultItem });
                    searchResultsRef.value.push(resultItem);
                    cachedSearchResults[
                        searchPageIndexRef.value * searchPageLength + index
                    ] = resultItem;
                } else {
                    const marker = new google.maps.Marker({
                        position: {
                            lat: resultItem.media.location.latitude,
                            lng: resultItem.media.location.longitude,
                        },
                        map: map,
                        title: resultItem.media.description,
                        label: String(index + 1),
                        animation: google.maps.Animation.DROP,
                    });

                    marker.addListener("click", markerClick);
                    bounds.extend(
                        new google.maps.LatLng(
                            resultItem.media.location.latitude,
                            resultItem.media.location.longitude
                        )
                    );

                    searchResults.push({ marker: marker, item: resultItem });
                    searchResultsRef.value.push(resultItem);
                    cachedSearchResults[
                        searchPageIndexRef.value * searchPageLength + index
                    ] = resultItem;
                }

                index++;
            }

            for (const resultItem of resultItems) {
                if (
                    resultItem.media.type.startsWith("kml") ||
                    resultItem.media.type.startsWith("kmz")
                ) {
                    resultItem["loading"] = false;
                    resultItem["loaded"] = false;
                }

                cachedSearchResults[
                    searchPageIndexRef.value * searchPageLength + index
                ] = resultItem;
                index++;
            }
        } else {
            for (const resultItem of resultItems) {
                if (
                    resultItem.media.type.startsWith("kml") ||
                    resultItem.media.type.startsWith("kmz")
                ) {
                    resultItem["loading"] = false;
                    resultItem["loaded"] = false;
                }

                if (resultItem.media.location === null) {
                    searchResults.push({ marker: null, item: resultItem });
                    searchResultsRef.value.push(resultItem);
                    cachedSearchResults[
                        searchPageIndexRef.value * searchPageLength + index
                    ] = resultItem;
                } else {
                    const marker = new google.maps.Marker({
                        position: {
                            lat: resultItem.media.location.latitude,
                            lng: resultItem.media.location.longitude,
                        },
                        map: map,
                        label: String(index + 1),
                        animation: google.maps.Animation.DROP,
                    });
                    marker.addListener("click", markerClick);
                    bounds.extend(
                        new google.maps.LatLng(
                            resultItem.media.location.latitude,
                            resultItem.media.location.longitude
                        )
                    );

                    searchResults.push({ marker: marker, item: resultItem });
                    searchResultsRef.value.push(resultItem);
                    cachedSearchResults[
                        searchPageIndexRef.value * searchPageLength + index
                    ] = resultItem;
                }

                index++;
            }
        }

        map.fitBounds(bounds);
    } catch (error) {
        console.error(error);
    }
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
    isUpdatingMediaRef.value = true;

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

    isUpdatingMediaRef.value = false;

    emit("updated");
};

onActivated(async () => {
    isActivatedRef.value = true;

    update();
});
onDeactivated(() => {
    isActivatedRef.value = false;
});
watch(isEnabledRef, (newValue, oldValue) => {
  if (newValue !== oldValue && oldValue === false) {
    
  }
});
</script>

<template>
    <div id="data">
        <div class="flyout-left is-hidden">
            <div class="wrap">
                <div class="block is-hidden-mobile">
                    <nav class="panel">
                        <div class="panel-block">
                            <nav class="level is-mobile">
                                <div class="level-left">
                                    <div class="level-item">
                                        <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                                            Users
                                        </h3>
                                    </div>
                                </div>
                                <div class="level-right">
                                    <div class="level-item">
                                        <button class="button toggle is-rounded" :disabled="isFetchingUsersRef"
                                            @click="update">
                                            <span class="icon is-small">
                                                <i class="fa-solid fa-rotate"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <transition name="fade" mode="out-in">
                                <div class="control" v-if="isFetchingUsersRef && usersRef.length === 0" key="loading">
                                    <nav class="level">
                                        <div class="level-item">
                                            <span class="icon">
                                                <i class="fas fa-spinner updating"></i>
                                            </span>
                                        </div>
                                    </nav>
                                </div>
                                <div class="control" v-else key="default">
                                    <label v-for="(item, index) in usersRef" v-bind:key="item">
                                        <input type="checkbox"
                                            v-bind:disabled="!isEnabledRef || usersRef.reduce((x, y, i) => i > 0 && y.checked ? x + 1 : x, 0) === 0"
                                            @change="selectUser($event, index)" v-bind:checked="item.checked"
                                            v-if="index === 0" :key="0" />
                                        <input type="checkbox" v-bind:disabled="!isEnabledRef"
                                            @change="selectUser($event, index)" v-bind:checked="item.checked" v-else
                                            :key="index" />
                                        <span class="custom"></span>
                                        <span class="is-size-7 has-text-weight-bold" v-text="item.name"></span>
                                    </label>
                                </div>
                            </transition>
                        </div>
                    </nav>
                </div>
            </div>
        </div>
        <div id="media" ref="viewerRef">
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
                                </div>
                                <div class="level-right">
                                    <div class="level-item">
                                        <button class="button toggle is-rounded" :disabled="isFetchingRef"
                                            @click="update">
                                            <span class="icon is-small">
                                                <i class="fa-solid fa-arrows-rotate"
                                                    v-bind:class="{ loading: isFetchingRef }"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <transition name="fade" mode="out-in">
                                <div class="control" v-if="isFetchingRef && itemsRef.length === 0" key="loading">
                                    <nav class="level">
                                        <div class="level-item">
                                            <span class="icon">
                                                <i class="fas fa-spinner updating"></i>
                                            </span>
                                        </div>
                                    </nav>
                                </div>
                                <div class="control" v-else key="default">
                                    <label v-for="(item, index) in mediaRef" v-bind:key="item">
                                        <input type="checkbox" v-bind:disabled="!isEnabledRef"
                                            @change="selectMedia($event, index)" v-bind:checked="item.checked" />
                                        <span class="custom"></span>
                                        <span class="is-size-7 has-text-weight-bold" v-text="item.name"></span>
                                    </label>
                                </div>
                            </transition>
                        </div>
                    </nav>
                </div>
            </div>
            <transition name="fade">
                <div class="bottom" v-show="totalCountRef > pageLengthRef || isContinuousRef">
                    <div class="block">
                        <div class="panel-block">
                            <div class="control">
                                <nav class="level">
                                    <div class="level-left">
                                        <div class="level-item">
                                            <button class="button is-primary"
                                                v-bind:disabled="(pageIndexRef === 0 || isFetchingRef)"
                                                @click="previous($event)">
                                                <transition name="fade" mode="out-in">
                                                    <span class="icon is-small"
                                                        v-if="(!isForwardingRef && isFetchingRef)" key="fetching">
                                                        <i class="fas fa-spinner updating"></i>
                                                    </span>
                                                    <span class="icon is-small" v-else key="fetched">
                                                        <i class="fa-solid fa-chevron-left"></i>
                                                    </span>
                                                </transition>
                                            </button>
                                        </div>
                                    </div>
                                    <transition name="fade">
                                        <div class="level-item" v-if="~~Math.ceil(totalCountRef / pageLengthRef) > 0">
                                            <span class="is-size-7 has-text-weight-bold">{{ pageIndexRef + 1 }}/{{
                                                    ~~Math.ceil(totalCountRef / pageLengthRef)
                                            }}</span>
                                        </div>
                                    </transition>
                                    <div class="level-right">
                                        <div class="level-item">
                                            <button class="button is-primary"
                                                v-bind:disabled="(pageIndexRef + 1 === ~~Math.ceil(totalCountRef / pageLengthRef) || isFetchingRef)"
                                                @click="next($event)">
                                                <transition name="fade" mode="out-in">
                                                    <span class="icon is-small"
                                                        v-if="(isForwardingRef && isFetchingRef)" key="fetching">
                                                        <i class="fas fa-spinner updating"></i>
                                                    </span>
                                                    <span class="icon is-small" v-else key="fetched">
                                                        <i class="fa-solid fa-chevron-right"></i>
                                                    </span>
                                                </transition>
                                            </button>
                                        </div>
                                    </div>
                                </nav>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
    </div>
</template>

<style lang="scss" scoped>
#data {
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

    #media,
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

                        .control {
                            display: flex;
                            margin: 0;
                            padding: 0;
                            flex-direction: column;
                            justify-content: flex-start;
                            align-items: center;

                            .level {
                                padding: 0.5em 0.75em;
                                width: 100%;
                            }

                            label {
                                padding: 0.5em 0.75em;
                                width: 100%;
                                background-color: transparent;
                                transition: background-color 0.5s;
                            }

                            label:hover {
                                background-color: hsl(0deg, 0%, 93%);
                            }

                            label>span {
                                user-select: none;
                            }

                            label>span:not(:first-of-type) {
                                margin: 0px 0px 0px 12px;
                            }

                            label input[type="checkbox"],
                            label input[type="radio"] {
                                display: none;
                            }

                            label .custom {
                                position: relative;
                                margin: 0;
                                font-size: 1rem;
                            }

                            label input[type="checkbox"]+.custom:before,
                            label input[type="radio"]+.custom:before {
                                font-weight: 900;
                                font-family: "Font Awesome 6 Free";
                                content: "\f00c";
                                color: transparent;
                                text-shadow: none;
                                transition: 0.5s;
                            }

                            label input[type="checkbox"]:checked+.custom:before,
                            label input[type="radio"]:checked+.custom:before {
                                color: var(--accent-color);
                                transition: 0.5s;
                            }
                        }

                        .control:last-child {
                            padding: 0;
                        }

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
                width: 100%;
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

    #media {
        display: flex;
        position: relative;
        width: 100%;
        height: 100%;

        >.wrap {
            width: 100%;

            .block {
                width: 100%;
            }
        }
    }
}

@keyframes selecting {
    to {
        background-position: 100% 0%, 0% 100%, 0% 0%, 100% 100%;
    }
}
</style>
