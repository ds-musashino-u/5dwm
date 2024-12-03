<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, onMounted, onUnmounted, onActivated, onDeactivated, reactive, toRef, watch } from "vue";

const props = defineProps({
  isCollapsed: { type: Boolean, required: false, default: false },
  isExpandable: { type: Boolean, required: false, default: false },
  item: { type: Object, required: false, default: null },
  canBack: { type: Boolean, required: false, default: true },
  color: { type: String, required: false, default: window.getComputedStyle(document.documentElement).getPropertyValue("--accent-color") },
  error: { type: Object, required: false, default: null }
});
const emit = defineEmits(["load", "unload", "back", "colorChanged", "fetchCollection", "selectCollectionItem", "disposeCollection"]);
const isInitializedRef = ref(false);
const inputColorRef = ref(props.color);
const selectedColorRef = ref(props.color);
const collectionPageIndexRef = ref(0);
const collectionIsFetchingRef = ref(false);
const collectionItemsRef = ref([]);
const selectCollectionItemRef = ref(null);

const load = (event, item) => {
  emit("load", item);
};
const unload = (event, item) => {
  emit("unload", item);
};
const back = (event) => {
  emit("back");
};
const resetColor = (event) => {
  selectedColorRef.value = inputColorRef.value = window.getComputedStyle(document.documentElement).getPropertyValue("--accent-color");

  emit("colorChanged", props.item, selectedColorRef.value);
};
const colorChanged = (event) => {
  if (/^#(?:[0-9a-f]{3}){1,2}$/i.test(inputColorRef.value)) {
    selectedColorRef.value = inputColorRef.value;

    emit("colorChanged", props.item, selectedColorRef.value);
  }
};
const loadCollection = () => {
  emit("fetchCollection", props.item.media.collection, collectionPageIndexRef, collectionItemsRef, collectionIsFetchingRef);
};
const selectCollectionItem = (event, index, collection) => {
  if (props.item.media.id === collection.item.media.id) {
    selectCollectionItemRef.value = null;
  } else {
    selectCollectionItemRef.value = collection.item;
  }

  emit("selectCollectionItem", collection);
};
const initialize = async () => {
  isInitializedRef.value = true;

  if (props.item.media.collection !== null) {
    await loadCollection();
  }
};

onMounted(() => {
  initialize();
});
onUnmounted(() => {
  isInitializedRef.value = false;

  emit("disposeCollection", collectionItemsRef);
});
onActivated(() => {
  if (!isInitializedRef.value) {
    initialize();
  }
});
onDeactivated(() => {
  emit("disposeCollection", collectionItemsRef);
});
</script>

<template>
  <div class="panel-block">
    <div class="top">
      <div class="panel">
        <div class="panel-block">
          <nav class="level is-mobile">
            <div class="level-left">
              <div class="level-item">
                <button class="button is-rounded is-primary" v-bind:disabled="!canBack" @click="back($event)">
                  <span class="icon is-small">
                    <i class="fa-solid fa-arrow-left"></i>
                  </span>
                </button>
              </div>
            </div>
          </nav>
        </div>
      </div>
    </div>
    <div class="wrap">
      <div class="panel">
        <div class="panel-block">
          <nav class="level is-mobile">
            <div class="level-left">
              <transition name="fade" mode="out-in">
                <div class="level-item" v-if="selectCollectionItemRef === null" key="alt">
                  <span class="icon is-small" v-if="'data' in item.media && item.media.data !== null">
                    <i class="fa-solid fa-table"></i>
                  </span>
                  <span class="icon is-small" v-else-if="item.media.type.startsWith('image')">
                    <i class="fa-solid fa-file-image"></i>
                  </span>
                  <span class="icon is-small" v-else-if="item.media.type.startsWith('video')">
                    <i class="fa-solid fa-file-video"></i>
                  </span>
                  <span class="icon is-small" v-else-if="item.media.type.startsWith('audio')">
                    <i class="fa-solid fa-file-audio"></i>
                  </span>
                  <span class="icon is-small" v-else-if="item.media.type.startsWith('text')">
                    <i class="fa-solid fa-file-lines"></i>
                  </span>
                  <span class="icon is-small" v-else>
                    <i class="fa-solid fa-file"></i>
                  </span>
                </div>
                <div class="level-item" v-else key="default">
                  <span class="icon is-small" v-if="'data' in selectCollectionItemRef.media && selectCollectionItemRef.media.data !== null">
                    <i class="fa-solid fa-table"></i>
                  </span>
                  <span class="icon is-small" v-else-if="selectCollectionItemRef.media.type.startsWith('image')">
                    <i class="fa-solid fa-file-image"></i>
                  </span>
                  <span class="icon is-small" v-else-if="selectCollectionItemRef.media.type.startsWith('video')">
                    <i class="fa-solid fa-file-video"></i>
                  </span>
                  <span class="icon is-small" v-else-if="selectCollectionItemRef.media.type.startsWith('audio')">
                    <i class="fa-solid fa-file-audio"></i>
                  </span>
                  <span class="icon is-small" v-else-if="selectCollectionItemRef.media.type.startsWith('text')">
                    <i class="fa-solid fa-file-lines"></i>
                  </span>
                  <span class="icon is-small" v-else>
                    <i class="fa-solid fa-file"></i>
                  </span>
                </div>
              </transition>
              <transition name="fade" mode="out-in">
                <div class="level-item" v-if="selectCollectionItemRef !== null && 'index' in selectCollectionItemRef" key="alt">
                  <span class="icon is-small" v-if="selectCollectionItemRef.index !== null">
                    <span class="is-size-7 is-uppercase has-text-weight-bold">{{ selectCollectionItemRef.index + 1 }}</span>
                  </span>
                </div>
                <div class="level-item" v-else-if="'index' in item && item.index !== null" key="default">
                  <span class="icon is-small">
                    <span class="is-size-7 is-uppercase has-text-weight-bold">{{ item.index + 1 }}</span>
                  </span>
                </div>
              </transition>
              <transition name="fade" mode="out-in">
                <div class="level-item" v-if="selectCollectionItemRef !== null && (selectCollectionItemRef.media.type.startsWith('kml') || selectCollectionItemRef.media.type.startsWith('kmz') || 'data' in selectCollectionItemRef.media && selectCollectionItemRef.media.data !== null)" key="alt">
                  <span class="icon is-small has-text-dark">
                    <i class="fa-solid fa-chart-simple"></i>
                  </span>
                  <transition name="fade" mode="out-in">
                    <div class="control" v-if="'data' in selectCollectionItemRef.media && selectCollectionItemRef.media.data !== null && selectCollectionItemRef.media.data.length === 0" key="loading">
                      <span class="icon">
                        <i class="fas fa-spinner updating"></i>
                      </span>
                    </div>
                    <div class="control" v-else key ="loaded">
                      <div class="tabs is-toggle">
                        <ul :style="{ pointerEvents: selectCollectionItemRef.loading ? 'none' : 'auto' }">
                          <li :class="{ 'is-active': !selectCollectionItemRef.loaded }" >
                            <a @click="selectCollectionItemRef.loaded ? unload($event, selectCollectionItemRef) : load($event, selectCollectionItemRef)">
                              <span class="is-size-7 is-uppercase has-text-weight-bold">Off</span>
                            </a>
                          </li>
                          <li :class="{ 'is-active': selectCollectionItemRef.loaded }">
                            <a @click="selectCollectionItemRef.loaded ? unload($event, selectCollectionItemRef) : load($event, selectCollectionItemRef)">
                              <span class="is-size-7 is-uppercase has-text-weight-bold">On</span>
                            </a>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </transition>
                </div>
                <div class="level-item" v-else-if="item.media.type.startsWith('kml') || item.media.type.startsWith('kmz') || 'data' in item.media && item.media.data !== null" key="default">
                  <span class="icon is-small has-text-dark">
                    <i class="fa-solid fa-chart-simple"></i>
                  </span>
                  <transition name="fade" mode="out-in">
                    <div class="control" v-if="'data' in item.media && item.media.data !== null && item.media.data.length === 0" key="loading">
                      <span class="icon">
                        <i class="fas fa-spinner updating"></i>
                      </span>
                    </div>
                    <div class="control" v-else key ="loaded">
                      <div class="tabs is-toggle">
                        <ul :style="{ pointerEvents: item.loading ? 'none' : 'auto' }">
                          <li :class="{ 'is-active': !item.loaded }" >
                            <a @click="item.loaded ? unload($event, item) : load($event, item)">
                              <span class="is-size-7 is-uppercase has-text-weight-bold">Off</span>
                            </a>
                          </li>
                          <li :class="{ 'is-active': item.loaded }">
                            <a @click="item.loaded ? unload($event, item) : load($event, item)">
                              <span class="is-size-7 is-uppercase has-text-weight-bold">On</span>
                            </a>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </transition>
                </div>
              </transition>
              <transition name="fade" mode="out-in">
                <div class="level-item" v-if="selectCollectionItemRef !== null && 'data' in selectCollectionItemRef.media && selectCollectionItemRef.media.data !== null" key="alt">
                  <button class="button is-flat" type="button" v-bind:disabled="selectCollectionItemRef.media.data.length === 0" @click="resetColor($event)">
                    <span class="icon is-small has-text-dark">
                      <i class="fa-solid fa-palette"></i>
                    </span>
                  </button>
                </div>
                <div class="level-item" v-else-if="'data' in item.media && item.media.data !== null" key="default">
                  <button class="button is-flat" type="button" v-bind:disabled="item.media.data.length === 0" @click="resetColor($event)">
                    <span class="icon is-small has-text-dark">
                      <i class="fa-solid fa-palette"></i>
                    </span>
                  </button>
                </div>
              </transition>
              <transition name="fade" mode="out-in">
                <div class="level-item" v-if="selectCollectionItemRef !== null && 'data' in selectCollectionItemRef.media && selectCollectionItemRef.media.data !== null" key="alt">
                  <input class="input is-outlined is-size-7 has-text-weight-bold" type="color" v-bind:disabled="selectCollectionItemRef.media.data.length === 0" v-model="inputColorRef"
                      @input="colorChanged($event, selectCollectionItemRef)" />
                </div>
                <div class="level-item" v-else-if="'data' in item.media && item.media.data !== null" alt="default">
                  <input class="input is-outlined is-size-7 has-text-weight-bold" type="color" v-bind:disabled="item.media.data.length === 0" v-model="inputColorRef"
                      @input="colorChanged($event, item)" />
                </div>
              </transition>
            </div>
            <div class="level-right">
              <div class="level-item">
                <a class="button is-rounded" target="_blank" v-bind:href="selectCollectionItemRef === null ? item.media.url : selectCollectionItemRef.media.url"><span class="icon is-small"><i class="fa-solid fa-link"></i></span></a>
              </div>
              <div class="level-item" v-if="isExpandable">
                <button class="button toggle is-rounded" @click="isCollapsed = !isCollapsed">
                  <span class="icon is-small" v-bind:class="{ collapsed: isCollapsed }">
                    <i class="fa-solid fa-chevron-up"></i>
                  </span>
                </button>
              </div>
            </div>
          </nav>
          <transition name="fade" mode="out-in">
            <div class="level is-mobile has-background-danger" v-if="props.error !== null">
              <div class="level-left">
                <div class="level-item">
                  <span class="icon is-small has-text-white">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                  </span>
                </div>
                <div class="level-item" v-if="'url' in props.error && props.error.url !== null">
                  <a :href="props.error.url" target="_blank" class="is-size-7 is-uppercase is-underlined has-text-weight-bold has-text-white" :title="props.error.message">{{ props.error.message }}</a>
                </div>
                <div class="level-item" v-else>
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-white">{{ props.error.message }}</span>
                </div>
              </div>
            </div>
          </transition>
          <transition name="fade" mode="out-in">
            <div class="control" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.media.type.startsWith('image') && selectCollectionItemRef.media.url.startsWith('https://')" key="alt">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <picture class="image">
                        <img v-bind:src="'thumbnailUrl' in selectCollectionItemRef.media && selectCollectionItemRef.media.thumbnailUrl !== null ? selectCollectionItemRef.media.thumbnailUrl : selectCollectionItemRef.media.url" v-bind:alt="selectCollectionItemRef.media.id" />
                      </picture>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
            <div class="control" v-else-if="!isCollapsed && item.media.type.startsWith('image') && item.media.url.startsWith('https://')" key="default">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <picture class="image">
                        <img v-bind:src="'thumbnailUrl' in item.media && item.media.thumbnailUrl !== null ? item.media.thumbnailUrl : item.media.url" v-bind:alt="item.media.id" />
                      </picture>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
          </transition>
          <transition name="fade" mode="out-in">
            <div class="control" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.media.type.startsWith('video') && selectCollectionItemRef.media.url.startsWith('https://')" key="alt">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <video controls :src="selectCollectionItemRef.media.url"></video>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
            <div class="control" v-else-if="!isCollapsed && item.media.type.startsWith('video') && item.media.url.startsWith('https://')" key="default">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <video controls :src="item.media.url"></video>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
          </transition>
          <transition name="fade" mode="out-in">
            <div class="control" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.media.type.startsWith('audio') && selectCollectionItemRef.media.url.startsWith('https://')" key="alt">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <audio controls :src="selectCollectionItemRef.media.url"></audio>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
            <div class="control" v-else-if="!isCollapsed && item.media.type.startsWith('audio') && item.media.url.startsWith('https://')" key="default">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <audio controls :src="item.media.url"></audio>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
          </transition>
        </div>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && item.media.collection !== null" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Collection</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.collection"></span>
                </div>
              </div>
            </div>
            <div class="control">
              <transition-group name="gallery-list" class="gallery" tag="div" v-cloak>
                <article class="media gallery-list-item" v-for="(collectionItem, index) in collectionItemsRef" v-bind:key="index">
                  <div class="media-content">
                    <div class="stack">
                      <button class="button image is-64x64" :class="{ 'is-selected': selectCollectionItemRef === null ? item.media.id === collectionItem.item.media.id : selectCollectionItemRef.media.id === collectionItem.item.media.id }" type="button"
                        @click="selectCollectionItem($event, index, collectionItem)">
                        <picture class="image" v-if="item.media.type.startsWith('image') && item.media.url.startsWith('https://')">
                          <img v-bind:src="'thumbnailUrl' in collectionItem.item.media && collectionItem.item.media.thumbnailUrl !== null ? collectionItem.item.media.thumbnailUrl : collectionItem.item.media.url" v-bind:alt="String(index)" />
                        </picture>
                        <span class="icon" v-if="'data' in collectionItem.item.media && collectionItem.item.media.data !== null">
                          <i class="fa-solid fa-table fa-lg"></i>
                        </span>
                        <span class="icon" v-else-if="collectionItem.item.media.type.startsWith('image')">
                          <i class="fa-solid fa-file-image fa-lg"></i>
                        </span>
                        <span class="icon" v-else-if="collectionItem.item.media.type.startsWith('video')">
                          <i class="fa-solid fa-file-video fa-lg"></i>
                        </span>
                        <span class="icon" v-else-if="collectionItem.item.media.type.startsWith('audio')">
                          <i class="fa-solid fa-file-audio fa-lg"></i>
                        </span>
                        <span class="icon" v-else-if="collectionItem.item.media.type.startsWith('text')">
                          <i class="fa-solid fa-file-lines fa-lg"></i>
                        </span>
                        <span class="icon" v-else>
                          <i class="fa-solid fa-file fa-lg"></i>
                        </span>
                      </button>
                    </div>
                  </div>
                </article>
              </transition-group>
            </div>
            <transition name="fade" mode="out-in">
              <div class="level" v-if="collectionIsFetchingRef" key="fetching">
                <div class="level-item">
                  <span class="icon">
                    <i class="fas fa-spinner updating"></i>
                  </span>
                </div>
              </div>
              <div class="level" v-else-if="collectionPageIndexRef !== null" key="more">
                <div class="level-item">
                  <button class="button is-size-7" @click="loadCollection($event)">
                    <span class="icon is-small">
                      <i class="fa-solid fa-plus"></i>
                    </span>
                    <span class="is-uppercase has-text-weight-bold">More</span>
                  </button>
                </div>
              </div>
            </transition>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="selectCollectionItemRef === null" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">ID</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.id"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">ID</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="selectCollectionItemRef.media.id"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.hasScore" key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Score</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="selectCollectionItemRef.score"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed && item.hasScore" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Score</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.score"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.media.location !== null" key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Longitude</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="String(selectCollectionItemRef.media.location.longitude)"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed && item.media.location !== null" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Longitude</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="String(item.media.location.longitude)"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.media.location !== null" key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Latitude</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="String(selectCollectionItemRef.media.location.latitude)"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed && item.media.location !== null" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Latitude</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="String(item.media.location.latitude)"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.media.location !== null && selectCollectionItemRef.media.location.hasAddress" key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Address</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <p class="is-size-7 has-text-weight-bold has-text-right" v-text="selectCollectionItemRef.media.location.address"></p>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed && item.media.location !== null && item.media.location.hasAddress" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Address</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <p class="is-size-7 has-text-weight-bold has-text-right" v-text="item.media.location.address"></p>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null" key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Time</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="selectCollectionItemRef.media.createdAt.toLocaleString()"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Time</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.createdAt.toLocaleString()"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.media.categories.length > 0" key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Categories</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item" v-for="category in selectCollectionItemRef.media.categories" v-bind:key="category">
                  <span class="is-size-7 has-text-weight-bold" v-text="category"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed && item.media.categories.length > 0" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Categories</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item" v-for="category in item.media.categories" v-bind:key="category">
                  <span class="is-size-7 has-text-weight-bold" v-text="category"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null" key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Type</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="selectCollectionItemRef.media.type"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Type</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.type"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null" key="alt">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">User</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="selectCollectionItemRef.media.username"></span>
                </div>
              </div>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed" key="default">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">User</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.username"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && selectCollectionItemRef !== null && selectCollectionItemRef.media.description !== null && selectCollectionItemRef.media.description.length > 0" key="alt">
            <div class="content">
              <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Description</span>
              <p class="is-size-7 has-text-weight-bold" v-text="selectCollectionItemRef.media.description"></p>
            </div>
          </div>
          <div class="panel-block" v-else-if="!isCollapsed && item.media.description !== null && item.media.description.length > 0" key="default">
            <div class="content">
              <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Description</span>
              <p class="is-size-7 has-text-weight-bold" v-text="item.media.description"></p>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.panel-block {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 0;
  width: fit-content;
  height: 100%;
  max-height: 100%;

  .wrap {
    flex-basis: auto;
    width: fit-content;
    height: 100%;
    max-height: 100%;
    overflow-x: hidden;
    overflow-y: auto;

    .panel {
      border-radius: 0;
      width: fit-content;
      box-shadow: none !important;

      >.panel-block:nth-of-type(1)>nav.level:first-child {
        background: hsl(0, 0%, 96%);
      }

      >.panel-block {
        width: 320px;
        height: fit-content;

        .level>.level-right>.level-item .button {
          background: transparent !important;
        }

        input[type="color"] {
          appearance: none;
          margin: 0 !important;
          border: 2px solid var(--accent-color) !important;
          border-radius: 290486px !important;
          padding: 0;
          width: 1.0rem !important;
          aspect-ratio: 1;
          box-shadow: none;
          overflow: hidden;
          block-size: auto;
        }

        input[type="color"]::-webkit-color-swatch-wrapper {
          padding: 0;
        }

        input[type="color"]::-webkit-color-swatch {
          border: none;
        }

        .control {
          display: flex;
          flex-direction: column;
          justify-content: flex-start;
          align-items: center;
          padding: 0em 0.75em;
          width: 320px;
          height: fit-content;

          .gallery {
            display: flex;
            flex-shrink: 0;
            margin: -4px -2px 0px -2px;
            flex-direction: row;
            flex-wrap: wrap;
            justify-content: start;
            align-items: flex-start;
            width: calc(100% + 4px);

            .media {
              display: inline-block;
              margin: 4px 2px 0px 2px;
              border: 0px none transparent !important;
              padding: 0;
              width: calc(20% - 4px);

              .media-content {
                border-radius: 0px;
                width: 100%;
                background: hsl(0deg, 0%, 93%);
                overflow: hidden;

                .stack {
                  position: relative;
                  width: 100%;
                  aspect-ratio: 1 / 1;

                  button::after {
                      pointer-events: none;
                      position: absolute;
                      border: 2px var(--accent-color) solid;
                      opacity: 1;
                      background: transparent;
                      width: 100%;
                      min-height: 100%;
                      content: "";
                      opacity: 0;
                      transition: 0.5s;
                  }

                  button.is-selected::after {
                      opacity: 1;
                      transition: 0.5s;
                  }

                  button:not(.toggle) {
                    z-index: 1;
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 100%;
                    aspect-ratio: 1 / 1;
                    border-radius: 0px;
                    box-shadow: none !important;
                    overflow: hidden;
                    background: transparent !important;

                    picture {
                      margin: 0;
                      padding: 0;
                      width: 100%;
                      height: 100%;

                      img {
                        object-fit: cover;
                        width: 100%;
                        height: 100%;
                      }
                    }

                    .icon {
                      position: absolute;
                      top: 100%;
                      left: 100%;
                      margin: 0 !important;
                      width: 1rem !important;
                      height: 1rem !important;
                      transform: translate(-100%, -100%);
                      padding: 0px 8px 8px 0px;
                    }

                    .badge {
                      position: absolute;
                      top: 0%;
                      left: 0%;
                      margin: 0 !important;
                      border-radius: 0px 0px 0px 0px;
                      padding: 8px 12px 8px 12px;
                      background: var(--accent-color);
                      color: #ffffff;
                    }
                  }

                  .heading {
                    z-index: 1;
                    position: absolute;
                    display: flex;
                    flex-direction: row;
                    justify-content: flex-start;
                    align-items: center;
                    top: 0%;
                    left: 0%;
                    margin: 0;
                    padding: 0;
                    background: var(--accent-color);

                    .badge {
                      position: relative !important;
                      margin: 0 !important;
                      border-radius: 0px 0px 0px 0px;
                      padding: 4px 8px 4px 8px;
                      color: #ffffff;
                    }
                  }

                  .heading.is-selected {
                    background: #ffffff;

                    .badge {
                      color: var(--accent-color);
                    }
                  }

                  button.toggle {
                    position: relative;
                    z-index: 1;
                    top: 0%;
                    left: 0%;
                    margin: 0 !important;
                    padding: 2px 8px 2px 8px !important;
                    width: fit-content !important;
                    height: fit-content !important;
                    box-shadow: none !important;
                    line-height: 1.5rem !important;
                    background: transparent !important;

                    >span.icon {
                      margin: 0 !important;
                      width: 1.5rem !important;
                      height: 1.5rem !important;
                      font-size: 1.5rem !important;
                      line-height: 1.5rem !important;

                      >i {
                        color: #ffffff !important;
                      }
                    }
                  }
                }
              }

              figure {
                margin: 0;
                padding: 0;

                .image {
                  overflow: hidden;

                  img {
                    object-fit: cover;
                    width: 100%;
                    height: 100%;
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  .top {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    border-bottom: 1px solid hsl(0deg, 0%, 93%);

    .panel {
      border-radius: 0;
      width: fit-content;
      box-shadow: none !important;

      >.panel-block:nth-of-type(1)>nav.level:first-child {
        background: hsl(0, 0%, 96%);
      }
    }

    .panel-block {
      border-radius: 0;
      width: 320px;
      box-shadow: none !important;

      >.level {
        padding: 0.5em 0.75em;
      }
    }
  }

  .bottom {
    border-top: 1px solid hsl(0deg, 0%, 93%);

    .control {
      padding: 0;

      >.level {
        padding: 0.5em 0.75em;
      }
    }
  }

  .top,
  .bottom {
    flex-shrink: 0;
    width: fit-content;
    height: fit-content;
    min-height: fit-content;
    overflow-x: hidden;
    overflow-y: hidden;
    box-sizing: border-box;

    button {
      border-radius: 4px;
      box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
        0 0px 0 1px rgb(10 10 10 / 2%) !important;
    }
  }

  .panel-block:not(:first-child)>.level {
    padding: 0.5em 0.75em;
  }

  .panel-block {
    flex-direction: column;
    align-items: flex-start;
    padding: 0;

    .level {
      margin: 0;
      padding: 0em 0.75em;
      width: 100%;
      flex-direction: row;

      .panel-heading {
        margin: 0;
        padding: 0;
        background: transparent;
      }

      .badge {
        padding: 4px !important;
        border-radius: 290486px;
        width: 0.75rem !important;
        height: 0.75rem !important;
        background: var(--accent-color);
        color: #ffffff !important;
        font-size: 0.75rem;
        line-height: 100%;
        overflow: hidden;
        box-sizing: content-box;
        text-align: center;
      }

      >.level-left>.level-item> {
        button.is-flat {
          width: fit-content !important;
          height: fit-content !important;
          padding: 0px !important;
          box-shadow: none !important;
          line-height: 1.0rem !important;
          background: transparent !important;

          >span.icon {
            margin: 0 !important;
            width: 1.0rem !important;
            height: 1.0rem !important;
            font-size: 1.0rem !important;
            line-height: 1.0rem !important;
          }
        }

        .control {
          width: fit-content;

          >.tabs.is-toggle {
            ul {
              margin: 0;

              >li>a {
                padding: 0.25em 0.5em;
                transition: 0.5s;
              }

              >li:not(.is-active)>a {
                background: #ffffff;
              }
            }
          }
        }

        span.icon+.control {
          margin-left: 0.75rem;
        }

        button.toggle {
          width: fit-content !important;
          height: fit-content !important;
          padding: 8px !important;
          box-shadow: none !important;
          line-height: 1.5rem !important;
          background: transparent !important;

          >span.icon {
            margin: 0 !important;
            width: 1.5rem !important;
            height: 1.5rem !important;
            font-size: 1.5rem !important;
            line-height: 1.5rem !important;
          }
        }
      }

      >.level-right {
        margin: 0;

        >.level-item {
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

          .button.toggle {
            >span {
              transform: rotate(180deg);
            }

            >span.collapsed {
              transition: transform 0.5s ease;
              transform: rotate(0deg);
            }
          }

          .control {
            justify-content: flex-end;

            >input {
              width: auto;
            }

            >span+input {
              margin: 0px 0px 0px 4px;
            }
          }

          span {
            text-align: right;
          }
        }
      }
    }

    :not(nav).level {
      align-items: flex-start;

      >.level-left {
        margin: 0;
        flex-direction: column;
        align-items: flex-start;

        .level-item:not(:last-child) {
          margin: 0px 0px 0.5em 0px;
        }
      }

      >.level-right {
        margin: 0;
        width: 50%;
        flex-direction: column;

        >.level-item {
          width: 100%;
          justify-content: flex-end;
        }

        .level-item:not(:last-child) {
          margin: 0px 0px 0.5em 0px;
        }
      }
    }

    .level.has-background-danger>.level-left {
      flex-direction: row;
      padding: 0.5em 0em;

      >.level-item:not(:last-child) {
        margin: 0px 0.5em 0px 0px;
      }

      a,
      a:focus,
      a:link,
      a:visited,
      a:active {
        color: #ffffff !important;
        transition: .5s;
      }

      a:hover {
        opacity: 0.5;
        color: #ffffff !important;
        transition: .5s;
      }
    }

    .control {
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      align-items: center;
      padding: 0 !important;
      width: 320px;

      .level {
        padding: 0;
        width: 100%;

        >.level-item>.media {
          display: inline-block;
          margin: 0;
          border: 0px none transparent !important;
          padding: 0;
          width: 100%;

          .media-content {
            display: flex;
            width: 100%;

            picture {
              margin: 0;
              padding: 0;
              width: 100%;
              height: 100%;

              img {
                object-fit: contain;
                width: 320px;
              }
            }

            video, audio {
              margin: 0;
              padding: 0;
              width: 100%;
            }
          }
        }
      }
    }

    .control:last-child {
      padding: 12px 0px 0px 0px;
    }

    .content {
      margin: 0;
      padding: 0.5em 0.75em;
      width: 100%;

      span+p,
      p {
        margin: 0.5em 0px 0px 0px;
        overflow-wrap: break-word;
      }
    }
  }

  .panel-block:not(:last-child) {
    border-bottom: 1px solid hsl(0deg, 0%, 93%);
  }
}
</style>
