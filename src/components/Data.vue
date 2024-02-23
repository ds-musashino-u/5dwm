<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, reactive, onMounted, onUnmounted, onActivated, onDeactivated, watch } from "vue";
import { getAccessToken } from "../presenters/auth.mjs";
import { search as searchWorldMap, ResultItem } from "../presenters/search.mjs";
import { Media, getMedia } from "../presenters/media.mjs";
import { Category, getCategories, insertCategory, updateCategory, deleteCategory } from "../presenters/categories.mjs";
import Uploader from "./Uploader.vue";

const isInitializedRef = ref(false);
const isEnabledRef = ref(true);
const isFetchingUsersRef = ref(false);
const dataPanelRef = ref(null);
const overlayRef = ref(null);
const editPanelRef = ref(null);
const queryRef = ref("");
const pageIndexRef = ref(0);
const pageLengthRef = ref(100);
const isFetchingRef = ref(false);
const isContinuousRef = ref(true);
const totalCountRef = ref(0);
const lastUpdatedRef = ref(0);
const usersRef = ref([{ name: "All", checked: true }/*, { name: "Alice", checked: false }, { name: "Bob", checked: false }*/]);
const dataSourcesRef = ref([{ name: "Media", checked: true, columns: [{ name: "", value: "url", width: "calc(1.5rem + calc(0.75rem * 1.5))" }, { name: "ID", value: "id", width: "5%" }, { name: "Type", value: "type", width: "5%" }, { name: "Categories", value: "categories", width: "10%" }, { name: "Longitude", value: "longitude", width: "10%" }, { name: "Latitude", value: "latitude", width: "10%" }, { name: "Address", value: "address", width: "10%" }, { name: "Created", value: "createdAt", width: "10%" }, { name: "User", value: "username", width: "10%" }, { name: "Description", value: "description", width: "auto" }] }, { name: "Categories", checked: false, columns: [{ name: "ID", value: "id", width: "5%" }, { name: "Name", value: "name", width: "50%" }, { name: "Updated", value: "updatedAt", width: "45%" }] }]);
const dataItemsRef = ref([]);
const categoriesItemsRef = ref([]);
const editingItemRef = ref(null);
const isSavingRef = ref(false);
const isDeletingRef = ref(false);
const deleteButtonRef = ref(null);
const deleteConfirmation = reactive({ visible: false, dismiss: false });
let updatedTime = 0;
const props = defineProps({
    auth0: Object,
    user: Object,
    text: String,
    updatedTime: Number,
    isAdmin: Boolean
});
const emit = defineEmits(["select", "completed", "updated"]);
const selectDataSource = (event, index) => {
    dataSourcesRef.value[index].checked = !dataSourcesRef.value[index].checked;

    for (let i = 0; i < dataSourcesRef.value.length; i++) {
        if (index !== i) {
            dataSourcesRef.value[i].checked = false;
        }
    }

    pageIndexRef.value = 0;
    totalCountRef.value = 0;
    isContinuousRef.value = true;

    update();
};
const resetDataSource = (event) => {
    for (const source of dataSourcesRef.value) {
        if (source.name === "Media") {
            source.checked = true;
        } else {
            source.checked = false;
        }
    }
};
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
const selectItem = (event, index) => {
    dataItemsRef.value[index].checked = !dataItemsRef.value[index].checked;

    if (dataItemsRef.value[index].checked) {
        const dataSource = dataSourcesRef.value.find(x => x.checked).name;

        if (dataSource === "Media") {
            editingItemRef.value = { source: dataSource, data: Object.assign({}, dataItemsRef.value[index].data) };
        } else if (dataSource === "Categories") {
            editingItemRef.value = { source: dataSource, insert: false, update: true, delete: true, schemes: [{ key: "id", name: "ID", ignore: true }, { key: "name", name: "Name", ignore: false }, { key: "updatedAt", name: "Updated", ignore: true }], data: Object.assign({}, dataItemsRef.value[index].data) };
        }
    }

    for (let i = 0; i < dataItemsRef.value.length; i++) {
        if (index !== i && dataItemsRef.value[i].checked) {
            dataItemsRef.value[i].checked = false;
        }
    }

    emit("select", dataItemsRef.value[index], pageIndexRef.value * pageLengthRef.value + index);
};
const update = async (event, reset = false) => {
    const dataSource = dataSourcesRef.value.find(x => x.checked).name;

    if (reset) {
        pageIndexRef.value = 0;
        totalCountRef.value = 0;
        isContinuousRef.value = true;
    }

    isFetchingRef.value = true;

    if (dataSource === "Media") {
        dataItemsRef.value.splice(0);

        try {
            const query = queryRef.value;
            const [resultItems, totalCount, timestamp] = await searchWorldMap(await getAccessToken(props.auth0), query.split(/\s/).reduce((x, y) => {
                if (y.length > 0) {
                    x.push(y);
                }

                return x;
            }, []), [], [], props.isAdmin ? [] : [props.user.email], null, null, null, "created_at", "desc", pageIndexRef.value * pageLengthRef.value, pageLengthRef.value);

            if (dataSourcesRef.value.find(x => x.checked).name === "Media" && query === queryRef.value) {
                for (const resultItem of resultItems) {
                    dataItemsRef.value.push({ data: Object.assign(resultItem.media, { longitude: resultItem.media.location.longitude, latitude: resultItem.media.location.latitude, address: resultItem.media.location.address }), checked: false });
                }

                totalCountRef.value = totalCount;
                lastUpdatedRef.value = timestamp;
            }
        } catch (error) {
            shake(dataPanelRef.value);
            console.error(error);
        }
    } else if (dataSource === "Categories" && categoriesItemsRef.value.length <= pageIndexRef.value * pageLengthRef.value) {
        dataItemsRef.value.splice(0);

        try {
            const items = await getCategories(
                pageIndexRef.value * pageLengthRef.value,
                pageLengthRef.value + 1
            );
            let length;

            if (dataSourcesRef.value.find(x => x.checked).name === "Categories") {
                if (items.length > pageLengthRef.value) {
                    isContinuousRef.value = true;
                    length = pageLengthRef.value;
                } else {
                    isContinuousRef.value = false;
                    length = items.length;
                }

                for (let i = 0; i < length; i++) {
                    dataItemsRef.value.push({ data: { id: items[i].id, name: items[i].name, updatedAt: items[i].updatedAt }, checked: false });
                }
            }
        } catch (error) {
            shake(dataPanelRef.value);
            console.error(error);
        }
    }

    isFetchingRef.value = false;
};
const next = async () => {
    if (isContinuousRef.value || pageIndexRef.value <= ~~Math.ceil(totalCountRef.value / pageLengthRef.value)) {
        pageIndexRef.value++;

        await update();
    }
};
const previous = async () => {
    if (pageIndexRef.value > 0) {
        pageIndexRef.value--;
        isContinuousRef.value = true;

        await update();
    }
};
const requestAdd = () => {
    const dataSource = dataSourcesRef.value.find(x => x.checked).name;

    if (dataSource === "Categories") {
        editingItemRef.value = { insert: true, update: false, delete: false, schemes: [{ key: "name", name: "Name", ignore: false }], source: dataSource, data: { name: "" } };
    }
};
const saveItem = async (event) => {
    isSavingRef.value = true;

    if (editingItemRef.value.insert) {
        try {
            const category = await insertCategory(await getAccessToken(props.auth0), editingItemRef.value.data.name);

            if (category === null) {
                shake(editPanelRef.value);
            } else {
                for (let i = 0; i < dataItemsRef.value.length; i++) {
                    dataItemsRef.value[i].checked = false;
                }

                editingItemRef.value = null;
                update();
            }
        } catch (error) {
            shake(editPanelRef.value);
            console.error(error);
        }
    } else if (editingItemRef.value.update) {
        try {
            const category = await updateCategory(await getAccessToken(props.auth0), editingItemRef.value.data.id, editingItemRef.value.data.name);

            if (category === null) {
                shake(editPanelRef.value);
            } else {
                for (let i = 0; i < dataItemsRef.value.length; i++) {
                    dataItemsRef.value[i].checked = false;
                }

                editingItemRef.value = null;
                update();
            }
        } catch (error) {
            shake(editPanelRef.value);
            console.error(error);
        }
    }

    isSavingRef.value = false;
};
const requestDelete = (event) => {
    deleteConfirmation.visible = true;
    deleteConfirmation.dismiss = false;
};
const deleteItem = async (event) => {
    isDeletingRef.value = true;

    try {
        if (await deleteCategory(await getAccessToken(props.auth0), editingItemRef.value.data.id) === null) {
            shake(editPanelRef.value);
        } else {
            for (let i = 0; i < dataItemsRef.value.length; i++) {
                dataItemsRef.value[i].checked = false;
            }

            editingItemRef.value = null;
            update();
        }
    } catch (error) {
        shake(editPanelRef.value);
        console.error(error);
    }

    isDeletingRef.value = false;
};
const close = () => {
    for (let i = 0; i < dataItemsRef.value.length; i++) {
        dataItemsRef.value[i].checked = false;
    }

    editingItemRef.value = null;
};
const updated = () => {
    for (let i = 0; i < dataItemsRef.value.length; i++) {
        dataItemsRef.value[i].checked = false;
    }

    editingItemRef.value = null;

    update();
};
const format = (obj) => {
    if (typeof (obj) === "string") {
        return obj.substring(0, 100);
    } else if (Array.isArray(obj)) {
        return obj.join(", ");
    } else if (typeof (obj) === "object" && "toLocaleString" in obj) {
        return obj.toLocaleString();
    } else if (typeof (obj) === "number") {
        return String(obj);
    }

    return obj;
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

onMounted(() => {
    isInitializedRef.value = true;

    update();
});
onUnmounted(() => {
    isInitializedRef.value = false;
});
onActivated(() => {
    if (!isInitializedRef.value || props.updatedTime > updatedTime) {
        isInitializedRef.value = true;
        updatedTime = props.updatedTime;

        update();
    }
});
onDeactivated(() => { });
watch(isEnabledRef, (newValue, oldValue) => {
    if (newValue !== oldValue && oldValue === false) {

    }
});
</script>

<template>
    <div id="data">
        <div class="flyout-left is-hidden">
            <div class="wrap">
                <div class="block">
                    <nav class="panel">
                        <div class="panel-block">
                            <nav class="level is-mobile">
                                <div class="level-left">
                                    <div class="level-item">
                                        <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                                            Source
                                        </h3>
                                    </div>
                                </div>
                                <div class="level-right">
                                    <div class="level-item">
                                        <button class="button is-rounded"
                                            v-bind:disabled="dataSourcesRef.reduce((x, y) => y.checked ? x + 1 : x, 0) === 0 || dataSourcesRef.find(x => x.name === 'Media' && x.checked) !== undefined"
                                            @click="resetDataSource($event)">
                                            <span class="icon is-small">
                                                <i class="fa-solid fa-arrow-rotate-left"></i>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </nav>
                            <div class="control">
                                <label v-for="(item, index) in dataSourcesRef" v-bind:key="item">
                                    <input type="checkbox" v-bind:disabled="!isEnabledRef || item.checked"
                                        @change="selectDataSource($event, index)" v-bind:checked="item.checked" />
                                    <span class="custom"></span>
                                    <span class="is-size-7 has-text-weight-bold" v-text="item.name"></span>
                                </label>
                            </div>
                        </div>
                        <div class="panel-block" v-if="false">
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
        <div id="media">
            <div class="wrap">
                <div class="block">
                    <nav class="panel">
                        <div class="panel-block">
                            <nav class="level is-mobile">
                                <div class="level-left">
                                    <div class="level-item" v-if="props.isAdmin">
                                        <div class="tabs is-toggle">
                                            <ul>
                                                <li v-for="(item, index) in dataSourcesRef"
                                                    :class="{ 'is-active': item.checked }" v-bind:key="item">
                                                    <a @click="selectDataSource($event, index)">
                                                        <span class="is-size-7 is-uppercase has-text-weight-bold"
                                                            v-text="item.name"></span>
                                                    </a>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                    <div class="level-item" v-else>
                                        <transition name="fade" mode="out-in">
                                            <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold"
                                                v-text="dataSourcesRef.find(x => x.checked).name"
                                                :key="dataSourcesRef.find(x => x.checked).name"></h3>
                                        </transition>
                                    </div>
                                </div>
                                <div class="level-right">
                                    <div class="level-item">
                                        <div class="field">
                                            <form class="field" @submit.prevent>
                                                <transition name="fade" mode="out-in">
                                                    <div class="control"
                                                        v-if="dataSourcesRef.find(x => x.checked).name === 'Media'"
                                                        key="Media">
                                                        <input class="input is-outlined is-size-7 has-text-weight-bold"
                                                            type="text" placeholder="Keywords" size="25" v-model="queryRef"
                                                            @input="update($event, true)" />
                                                    </div>
                                                    <div class="control" v-else key="Categories">
                                                        <button class="button is-rounded" @click="requestAdd($event)">
                                                            <span class="icon is-small">
                                                                <i class="fa-solid fa-plus"></i>
                                                            </span>
                                                        </button>
                                                    </div>
                                                </transition>
                                                <div class="control">
                                                    <button class="button is-rounded" :disabled="isFetchingRef"
                                                        @click="update">
                                                        <span class="icon is-small">
                                                            <i class="fa-solid fa-arrows-rotate"
                                                                :class="{ loading: isFetchingRef }"></i>
                                                        </span>
                                                    </button>
                                                </div>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                            </nav>
                            <table class="table is-fullwidth is-hoverable" ref="dataPanelRef">
                                <thead>
                                    <transition name="fade" mode="out-in">
                                        <tr :key="dataSourcesRef.find(x => x.checked).name">
                                            <th class="is-size-7 is-uppercase has-text-weight-bold has-text-grey"
                                                v-for="column in dataSourcesRef.find(x => x.checked).columns"
                                                :style="{ width: column.width }" v-text="column.name" :key="column"></th>
                                        </tr>
                                    </transition>
                                </thead>
                                <transition name="fade" mode="out-in">
                                    <tbody v-if="!isFetchingRef">
                                        <tr v-for="(item, index) in dataItemsRef" v-bind:key="item"
                                            :class="{ 'is-selected': item.checked }" @click="selectItem($event, index)">
                                            <template v-for="(column, i) in dataSourcesRef.find(x => x.checked).columns"
                                                :key="column">
                                                <td class="is-size-7 has-text-weight-bold"
                                                    :style="{ width: 'width' in column ? column.width : 'auto' }"
                                                    v-text="format(item.data[column.value])" v-if="column.value !== 'url'">
                                                </td>
                                                <td class="is-size-7 has-text-weight-bold"
                                                    :style="{ width: 'width' in column ? column.width : 'auto' }"
                                                    v-else-if="item.data.type.startsWith('image')">
                                                    <a :href="item.data.url" target="_blank">
                                                        <picture><img :src="'thumbnailUrl' in item.data && item.data.thumbnailUrl !== null ? item.data.thumbnailUrl : item.data.url" :alt="item.data.id"></picture>
                                                    </a>
                                                </td>
                                                <td class="is-size-7 has-text-weight-bold"
                                                    :style="{ width: 'width' in column ? column.width : 'auto' }" v-else>
                                                    <a :href="item.data.url" target="_blank">
                                                        <span class="icon is-small">
                                                            <i class="fa-solid fa-link"></i>
                                                        </span>
                                                    </a>
                                                </td>
                                            </template>
                                        </tr>
                                    </tbody>
                                </transition>
                            </table>
                        </div>
                    </nav>
                </div>
            </div>
            <transition name="fade">
                <div class="bottom" v-show="totalCountRef > pageLengthRef || pageIndexRef > 0 || isContinuousRef">
                    <div class="block">
                        <div class="panel-block">
                            <div class="control">
                                <nav class="level is-mobile">
                                    <div class="level-left">
                                        <div class="level-item">
                                            <button class="button is-primary"
                                                v-bind:disabled="!isInitializedRef || pageIndexRef === 0 || isFetchingRef"
                                                @click="previous($event)">
                                                <span class="icon is-small">
                                                    <i class="fa-solid fa-chevron-left"></i>
                                                </span>
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
                                                v-bind:disabled="!isInitializedRef || totalCountRef === 0 || pageIndexRef + 1 === ~~Math.ceil(totalCountRef / pageLengthRef) || isFetchingRef || !isContinuousRef"
                                                @click="next($event)">
                                                <span class="icon is-small">
                                                    <i class="fa-solid fa-chevron-right"></i>
                                                </span>
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
        <transition name="slide">
            <div id="overlay" v-if="editingItemRef !== null" :key="editingItemRef">
                <div class="flyout-left" v-if="editingItemRef.source === 'Categories'">
                    <div class="wrap" ref="overlayRef">
                        <div class="block" ref="editPanelRef">
                            <nav class="panel">
                                <div class="panel-block">
                                    <nav class="level is-mobile">
                                        <div class="level-left">
                                            <div class="level-item">
                                                <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                                                    Add a category
                                                </h3>
                                            </div>
                                        </div>
                                        <div class="level-right">
                                            <div class="level-item">
                                                <button class="button toggle is-rounded" @click="close()">
                                                    <span class="icon is-small">
                                                        <i class="fa-solid fa-xmark"></i>
                                                    </span>
                                                </button>
                                            </div>
                                        </div>
                                    </nav>
                                </div>
                                <template v-for="scheme in editingItemRef.schemes" :key="scheme">
                                    <div class="panel-block">
                                        <nav class="level is-mobile">
                                            <div class="level-left">
                                                <div class="level-item">
                                                    <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold">
                                                        {{ scheme.name }}
                                                    </h3>
                                                </div>
                                            </div>
                                            <div class="level-right" v-if="'ignore' in scheme && scheme.ignore">
                                                <div class="level-item">
                                                    <span
                                                        class="is-size-7 has-text-weight-bold has-text-grey has-text-right">
                                                        {{ format(editingItemRef.data[scheme.key]) }}
                                                    </span>
                                                </div>
                                            </div>
                                        </nav>
                                        <div class="block" v-if="'ignore' in scheme === false || !scheme.ignore">
                                            <div class="control">
                                                <div class="field has-addons">
                                                    <div class="control is-expanded">
                                                        <input class="input is-size-7 has-text-weight-bold" type="text"
                                                            :placeholder="'Enter a ' + scheme.name"
                                                            v-model="editingItemRef.data[scheme.key]" />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </template>
                            </nav>
                        </div>
                    </div>
                    <div class="bottom">
                        <div class="block">
                            <div class="panel-block">
                                <div class="control">
                                    <button class="button is-rounded is-outlined is-fullwidth is-size-7 is-primary"
                                        type="submit"
                                        v-bind:disabled="user === null || !isInitializedRef || Object.keys(editingItemRef.data).some(x => editingItemRef.data[x].length === 0) || isSavingRef || isDeletingRef"
                                        @click="saveItem($event)">
                                        <transition name="fade" mode="out-in">
                                            <span class="icon" v-if="isSavingRef" key="saving">
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
                            <div class="panel-block" v-if="editingItemRef.delete">
                                <div class="control">
                                    <button class="button is-rounded is-outlined is-fullwidth is-size-7 is-danger"
                                        type="submit"
                                        v-bind:disabled="user === null || !isInitializedRef || isSavingRef || isDeletingRef"
                                        @click="requestDelete($event)">
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
                        </div>
                    </div>
                </div>
                <Uploader v-else-if="editingItemRef.source === 'Media'" :auth0="props.auth0" :user="props.user"
                    :is-closable="true" :is-deletable="true" :media="editingItemRef.data" @close="close"
                    @updated="updated" />
                <div class="modal" :class="{ 'is-active': deleteConfirmation.visible }">
                    <transition name="fade" mode="out-in">
                        <div class="modal-background" v-if="deleteConfirmation.visible && !deleteConfirmation.dismiss"
                            key="background"></div>
                    </transition>
                    <div class="wrap" @animationend="deleteConfirmation.visible = $event.srcElement.className !== 'wrap'"
                        :style="{ animationPlayState: deleteConfirmation.dismiss ? 'running' : 'paused' }">
                        <div class="modal-card"
                            :style="{ animationPlayState: deleteConfirmation.visible ? 'running' : 'paused' }"
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
                                        <button class="button" @click="deleteConfirmation.dismiss = true;">
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
            </div>
        </transition>
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

    #overlay {
        z-index: 1;
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
        transition: 0.5s;

        .wrap>.block .panel>.panel-block:first-of-type {
            background: hsl(0, 0%, 96%);
        }

        .wrap>.block .panel>.panel-block:not(:first-of-type) {
            .level {
                display: flex;
                align-items: flex-start;
                justify-content: space-between;

                >.level-left>.level-item>h3 {
                    line-height: inherit !important;
                }

                >.level-right {
                    margin: 0 !important;
                    width: 50%;

                    >.level-item {
                        display: flex;
                        justify-content: flex-end;
                        align-items: flex-start;
                        width: 50%;

                        span {
                            padding: 0.5em 0em;
                        }
                    }
                }
            }

            .panel-heading {
                padding: 0.5em 0em;
            }
        }
    }
    
    #media>.wrap>.block .panel>.panel-block {
        background: hsl(0, 0%, 96%);

        nav.level {
            padding: 0em 0em 0em 0.75em !important;
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
                width: 320px;
                height: fit-content;

                .panel {
                    background: transparent;
                    border-radius: 4px;
                    box-shadow: none;

                    .panel-block {
                        flex-direction: column;
                        padding: 0;

                        .field {
                            background: transparent !important;

                            form input {
                                background: #ffffff !important;
                            }
                        }

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
                                display: flex;
                                padding: 0em 0.75em;
                                width: 100%;
                                background-color: transparent;
                                transition: background-color 0.5s;
                                flex-direction: row;
                                align-items: center;
                                justify-content: flex-start;
                            }

                            label:hover {
                                background-color: hsl(0deg, 0%, 93%, 0.75);
                            }

                            label>span,
                            label>div:not(.image) {
                                padding: 0.5em 0em;
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

                            label>div {
                                display: flex;
                                flex-direction: row;
                                align-items: center;
                                justify-content: flex-start;
                            }

                            label>div:not(:first-of-type) {
                                padding: 0px 0px 0px 12px;
                            }

                            label>div:nth-of-type(2) {
                                justify-content: center;

                                >a>img {
                                    object-fit: cover;
                                    display: block;
                                    margin: 0;
                                    padding: 0;
                                    aspect-ratio: 1 / 1;
                                    height: calc(1.5em + calc(0.75rem * 1.5));
                                }
                            }

                            label>div>span:not(:first-of-type) {
                                margin: 0px 0px 0px 12px;
                            }

                            label>div>span {
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
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
                            padding: 0em 0.75em 0.5em 0.75em;
                            width: 100%;
                        }

                        >.block:not(:first-of-type) {
                            padding: 0.5em 0.75em 0.5em 0.5em;
                        }

                        >.level {
                            margin: 0;
                            padding: 0em 0.75em;
                            width: 100%;

                            >.level-left {
                                >.level-item {
                                    justify-content: flex-start;

                                    >.panel-heading {
                                        margin: 0 !important;
                                        padding: 0;
                                        background: transparent;
                                    }

                                    >span:not(:first-of-type) {
                                        margin: 0px 0px 0px 12px;
                                    }

                                    .custom {
                                        position: relative;
                                        margin: 0;
                                        font-size: 1rem;
                                    }

                                    .custom:before {
                                        font-weight: 900;
                                        font-family: "Font Awesome 6 Free";
                                        content: "\f00c";
                                        color: transparent;
                                        text-shadow: none;
                                    }

                                    .tabs>ul {
                                        margin: 0;
                                        padding: 0;

                                        li {
                                            margin: 0;
                                            padding: 0;
                                            border-left: 0px none transparent;
                                            border-top: 2px solid transparent;
                                            border-right: 0px none transparent;
                                            border-bottom: 2px solid transparent;
                                            transition: 0.5s;

                                            a {
                                                margin: 0;
                                                border: 0px none transparent;
                                                padding: 0.5em 0em;
                                                background-color: transparent;
                                                height: fit-content;
                                                backface-visibility: hidden;
                                                transition: 0.5s;

                                                span {
                                                    margin: 0;
                                                    padding: 0;
                                                }
                                            }
                                        }

                                        li:not(:last-child) {
                                            margin-right: 0.75em;
                                        }

                                        li.is-active {
                                            a {
                                                color: hsl(0deg, 0%, 21%);
                                            }

                                            border-bottom: 2px solid var(--accent-color);
                                            transition: 0.5s;
                                        }
                                    }
                                }

                                .level-item:not(:last-child) {
                                    margin: 0;
                                }

                                .level-item:not(:first-of-type) {
                                    padding: 0px 0px 0px 12px;
                                }
                            }

                            >.level-right {
                                margin: 0px 0px 0px 12px;

                                .field {
                                    display: flex;
                                    flex-direction: row;
                                    align-items: center;
                                }

                                button {
                                    background: transparent !important;
                                }

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
                                    >span.icon {
                                        transform: rotate(180deg);
                                    }

                                    >span.collapsed {
                                        transition: transform 0.5s ease;
                                        transform: rotate(0deg);
                                    }
                                }
                            }
                        }

                        >.level:not(:first-of-type) {
                            padding: 0.5em 0.75em;

                            >.level-left {
                                width: 100%;
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
                background: rgba(255, 255, 255, 0.9);
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
                width: 100%;
                height: fit-content;

                .panel {
                    background: rgba(255, 255, 255, 0.9);
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
            background: #ffffff;

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

        .tabs>ul {
            margin: 0;
        }

        .has-addons {
            margin: 0;
            border: 1px solid hsl(0deg, 0%, 93%);
            border-radius: 4px;

            .control>input {
                border: 0px none transparent !important;
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

                >.panel>.panel-block {
                    table {
                        z-index: 0;
                        margin: 0;
                        padding: 0;
                        table-layout: fixed;
                        border-collapse: separate;

                        thead {
                            background: hsl(0, 0%, 96%);

                            >tr {
                                height: calc(1.0rem + 24px);
                                
                                >th {
                                    z-index: 1;
                                    position: sticky;
                                    top: 0;
                                    border-bottom: 1px solid hsl(0deg, 0%, 93%);
                                    padding-left: 0.75em;
                                    padding-top: 0.5em;
                                    padding-right: 0;
                                    padding-bottom: 0.5em;
                                    vertical-align: middle;
                                    background: hsl(0, 0%, 96%);
                                }

                                >th:last-of-type {
                                    padding-right: 0.75em;
                                }
                            }
                        }

                        tbody {
                            >tr {
                                height: calc(1.5em + calc(0.75rem * 1.5));
                                background-color: transparent;
                                transition: .5s;

                                >td {
                                    border-bottom: 0px solid transparent;
                                    padding-left: 0.75em;
                                    padding-top: 0.5em;
                                    padding-right: 0;
                                    padding-bottom: 0.5em;
                                    vertical-align: middle;
                                    white-space: nowrap;
                                    text-overflow: ellipsis;
                                    overflow: hidden;

                                    >a {
                                        display: flex;
                                        margin: 0em 0em 0em -0.75em;
                                        width: 100%;
                                        height: 100%;
                                        align-items: center;
                                        justify-content: flex-start;

                                        >span {
                                            margin: 0em 0em 0em calc(calc(calc(1.5rem + calc(0.75rem * 1.5)) - 1rem) / 2);
                                            padding: 0;
                                            flex-shrink: 0;
                                            flex-grow: 0;
                                        }

                                        >span.is-small {
                                            font-size: 1rem;
                                            line-height: 1rem;
                                            height: 1rem;
                                        }

                                        >picture {
                                            display: block;
                                            margin: -0.5em 0em -0.5em 0em;
                                            padding: 0;
                                            height: 100%;
                                            overflow: hidden;
                                            flex-shrink: 0;
                                            flex-grow: 0;

                                            >img {
                                                object-fit: cover;
                                                display: block;
                                                margin: 0;
                                                padding: 0;
                                                aspect-ratio: 1 / 1;
                                                width: calc(1.5rem + calc(0.75rem * 1.5));
                                                overflow: hidden;
                                            }
                                        }
                                    }
                                }

                                >td:last-of-type {
                                    padding-right: 0.75em;
                                }
                            }

                            >tr:nth-child(even) {
                                background-color: hsl(0, 0%, 96%);
                                transition: .5s;
                            }

                            >tr:hover {
                                background-color: hsl(0, 0%, 93%, 0.75);
                                transition: .5s;
                            }

                            >tr.is-selected {
                                color: #ffffff;
                                background-color: var(--accent-color);
                                transition: .5s;
                            }
                        }
                    }
                }
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
</style>
