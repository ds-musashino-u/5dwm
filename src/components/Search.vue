<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onActivated, onDeactivated } from "vue";
import { getCategories } from "../presenters/categories.mjs";
import { getTypes } from "../presenters/types.mjs";
import { getMedia } from "../presenters/media.mjs";
import { getUsers } from "../presenters/users.mjs";
import { GoogleMapsConfig } from "../presenters/google-maps-config.mjs";
import { search as searchWorldMap } from "../presenters/search.mjs";
import ListBox from "./ListBox.vue";
import Results from "./Results.vue";
import Preview from "./Preview.vue";

const mapRef = ref(null);
const searchPanelRef = ref(null);
const queryRef = ref("");
const isDragging = ref(false);
const isLoading = ref(false);
const imageIsCollapsedRef = ref(true);
const imageDataUrlRef = ref(null);
const maxCategoriesLength = 10;
const categoriesIsCollapsedRef = ref(true);
const categoriesIsContinuousRef = ref(false);
const categoriesItemsRef = ref([]);
const categoriesPageIndexRef = ref(0);
const maxTypesLength = 25;
const typesIsCollapsedRef = ref(true);
const typesIsContinuousRef = ref(false);
const typesItemsRef = ref([]);
const typesPageIndexRef = ref(0);
const maxUsersLength = 10;
const usersIsCollapsedRef = ref(true);
const usersIsContinuousRef = ref(false);
const usersItemsRef = ref([]);
const usersPageIndexRef = ref(0);
const isSearchingRef = ref(false);
const searchPageIndexRef = ref(0);
const searchTotalCountRef = ref(null);
const searchResultsRef = ref([]);
const selectedMediaRef = ref(null);
const props = defineProps({
  auth0: Object,
  user: Object,
  text: String,
});
let map = null;
const searchPageLength = 20;
const searchResults = [];
const cachedSearchResults = {};

onActivated(async () => {
  const loader = new Loader({
    apiKey: GoogleMapsConfig.API_KEY,
    version: "weekly",
    language: navigator.language,
  });

  await loader.load();

  map = new google.maps.Map(mapRef.value, {
    center: { lat: 21.028344772352863, lng: 105.85271637244875 },
    zoom: 4,
    mapTypeId: "terrain",
    zoomControl: true,
    mapTypeControl: false,
    scaleControl: true,
    streetViewControl: false,
    rotateControl: true,
    fullscreenControl: false,
  });

  try {
    const categories = await getCategories();

    console.log(categories);
    /*console.log("insert");
    const cat = await insertCategory("foobarbaz");

    console.log(cat);

    console.log(await getCategory(cat.id));

    console.log("update");
    const cat2 = await updateCategory(cat.id, "Hogehogehoge");

    console.log(cat2);

    console.log(await getCategory(cat2.id));

    console.log("delete");

    console.log(await deleteCategory(cat2.id));

    console.log(await getCategory(cat2.id));*/
  } catch (error) {
    console.error(error);
  }

  try {
    const media = await getMedia("image*", "created_at", "desc", 0, 10);

    console.log(media);

    /*console.log(await getMedium(media[0].id));

    console.log("insert");
    const m = await insertMedium("https://5dworldmap.com/foobar.png", "image/png", ["foo", "bar"], "foo bar baz", "foobar", new Location(105.85271637244875, 21.028344772352863, "foo"));

    console.log(m);
    console.log(await getMedium(m.id));

    console.log("delete");

    console.log(await deleteMedium(m.id));
    console.log(await getMedium(m.id));*/
  } catch (error) {
    console.error(error);
  }

  try {
    const users = await getUsers();

    console.log(users);

    //console.log(await getUser(users[0].username));
  } catch (error) {
    console.error(error);
  }
});
onDeactivated(() => {});

const markerClick = (event) => {
  const element = searchResults.find(
    (x) =>
      x.marker !== null &&
      event.latLng.lat === x.marker.position.lat &&
      event.latLng.lng === x.marker.position.lng
  );

  if (element !== undefined) {
    selectedMediaRef.value = element.media;
  }
};
const dragover = (event) => {
  isDragging.value = true;
  event.dataTransfer.dropEffect = "copy";
};
const drop = (event) => {
  isDragging.value = false;

  for (const file of event.dataTransfer.files) {
    const name = file.name.toLowerCase();

    if (
      name.endsWith(".apng") ||
      name.endsWith(".png") ||
      name.endsWith(".jpg") ||
      name.endsWith(".jpeg") ||
      name.endsWith(".webp")
    ) {
      const reader = new FileReader();

      reader.addEventListener("load", (e) => {
        imageDataUrlRef.value = e.target.result;
      });
      reader.readAsDataURL(file);
    }
  }
};
const browse = async (event) => {
  for (const file of event.currentTarget.files) {
    isLoading.value = true;
    console.log(file);

    try {
      imageDataUrlRef.value = await new Promise(function (resolve, reject) {
        const reader = new FileReader();

        reader.onload = () => {
          resolve(reader.result);
        };
        reader.onerror = () => {
          reject(reader.error);
        };
        reader.readAsDataURL(file);
      });
    } catch (error) {
      console.error(error);
    }

    isLoading.value = false;

    return;
  }
};
const reset = (event) => {
  imageDataUrlRef.value = null;
};
const collapseCategories = () => {
  categoriesIsCollapsedRef.value = !categoriesIsCollapsedRef.value;
};
const collapseTypes = () => {
  typesIsCollapsedRef.value = !typesIsCollapsedRef.value;
};
const collapseUsers = () => {
  usersIsCollapsedRef.value = !usersIsCollapsedRef.value;
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
const clearUsers = () => {
  for (const item of usersItemsRef.value) {
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
const selectUser = (index) => {
  usersItemsRef.value[index].checked = !usersItemsRef.value[index].checked;
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
  typesPageIndexRef.value = pageIndex;
};
const nextUsers = async (pageIndex, pageLength, isFetchingRef) => {
  if (usersItemsRef.value.length <= pageIndex * maxUsersLength) {
    isFetchingRef.value = true;

    try {
      const items = await getUsers(pageIndex * maxUsersLength, pageLength);
      let length;

      if (items.length > maxUsersLength) {
        usersIsContinuousRef.value = true;
        length = maxUsersLength;
      } else {
        usersIsContinuousRef.value = false;
        length = items.length;
      }

      for (let i = 0; i < length; i++) {
        usersItemsRef.value.push({ checked: false, name: items[i].username });
      }
    } catch (error) {
      console.error(error);
    }

    isFetchingRef.value = false;
  }

  usersPageIndexRef.value = pageIndex;
};
const previousUsers = async (pageIndex) => {
  usersPageIndexRef.value = pageIndex;
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
const search = async (ignoreCache = true) => {
  if (ignoreCache) {
    Object.keys(cachedSearchResults).forEach((key) => {
      delete cachedSearchResults[key];
    });
  }

  if (map === null) {
    shake(searchPanelRef.value);
  } else {
    const keywords = queryRef.value.split(/\s/);
    const categories = categoriesItemsRef.value
      .filter((x) => x.checked)
      .map((x) => x.name);
    const types = typesItemsRef.value
      .filter((x) => x.checked)
      .map((x) => x.name);
    const users = usersItemsRef.value
      .filter((x) => x.checked)
      .map((x) => x.name);

    if (
      keywords.every((x) => x.length === 0) &&
      categories.length === 0 &&
      types.length === 0 &&
      users.length === 0
    ) {
      shake(searchPanelRef.value);

      return;
    }

    const range = [...Array(searchPageLength).keys()].map(
      (x) => searchPageIndexRef.value * searchPageLength + x
    );

    for (const result of searchResults) {
      if (result.marker !== null) {
        result.marker.setMap(null);
      }
    }

    if (range.every((x) => x in cachedSearchResults)) {
      const bounds = new google.maps.LatLngBounds();
      
      searchResults.splice(0);
      searchResultsRef.value.splice(0);

      for (const index of range) {
        const item = cachedSearchResults[index];

        if (item.media.location !== null) {
          const marker = new google.maps.Marker({
            position: {
              lat: item.media.location.latitude,
              lng: item.media.location.longitude,
            },
            map,
            title: item.media.description,
            animation: google.maps.Animation.DROP,
          });

          marker.addListener("click", markerClick);
          bounds.extend(
            new google.maps.LatLng(
              item.media.location.latitude,
              item.media.location.longitude
            )
          );

          item.marker = marker;
        }

        searchResults.push(item);
        searchResultsRef.value.push(item);
      }

      map.fitBounds(bounds);
    } else {
      isSearchingRef.value = true;

      try {
        const idToken = await props.auth0.getIdTokenClaims();
        const [searchItems, totalCount] = await searchWorldMap(
          idToken.__raw,
          keywords,
          categories,
          types,
          users,
          imageDataUrlRef.value,
          "created_at",
          "desc",
          searchPageIndexRef.value * searchPageLength,
          searchPageLength
        );
        const bounds = new google.maps.LatLngBounds();
        let index = 0;

        searchResults.splice(0);
        searchResultsRef.value.splice(0);
        searchTotalCountRef.value = totalCount;

        for (const media of searchItems) {
          if (media.location === null) {
            const item = { marker: null, media: media };

            searchResults.push(item);
            searchResultsRef.value.push(item);
            cachedSearchResults[
              searchPageIndexRef.value * searchPageLength + index
            ] = item;
          } else {
            const marker = new google.maps.Marker({
              position: {
                lat: media.location.latitude,
                lng: media.location.longitude,
              },
              map,
              title: media.description,
              animation: google.maps.Animation.DROP,
            });
            const item = { marker: marker, media: media };

            marker.addListener("click", markerClick);
            bounds.extend(
              new google.maps.LatLng(
                media.location.latitude,
                media.location.longitude
              )
            );

            searchResults.push(item);
            searchResultsRef.value.push(item);
            cachedSearchResults[
              searchPageIndexRef.value * searchPageLength + index
            ] = item;
          }

          index++;
        }

        map.fitBounds(bounds);
      } catch (error) {
        shake(searchPanelRef.value);
        console.error(error);
      }

      isSearchingRef.value = false;
    }
  }
};
const back = (event) => {
  if (selectedMediaRef.value !== null) {
    selectedMediaRef.value = null;
  } else if (searchTotalCountRef.value !== null) {
    for (const result of searchResults) {
      if (result.marker !== null) {
        result.marker.setMap(null);
      }
    }

    searchResults.splice(0);
    searchResultsRef.value.splice(0);
    searchPageIndexRef.value = 0;
    searchTotalCountRef.value = null;

    Object.keys(cachedSearchResults).forEach((key) => {
      delete cachedSearchResults[key];
    });
  }
};
const selectMedia = (item) => {
  selectedMediaRef.value = item.media;
};
const nextResults = (index) => {
  searchPageIndexRef.value = index;

  search(false);
};
const previousResults = (index) => {
  searchPageIndexRef.value = index;

  search(false);
};
</script>

<template>
  <div id="search">
    <div id="map" ref="mapRef"></div>
    <div class="wrap">
      <div class="block is-hidden-mobile" ref="searchPanelRef">
        <transition name="slide" mode="out-in">
          <nav
            class="panel"
            v-if="selectedMediaRef !== null"
            key="selectedMediaRef"
          >
            <div class="panel-block">
              <nav class="level is-mobile">
                <div class="level-left">
                  <div class="level-item">
                    <button class="button is-rounded" @click="back($event)">
                      <span class="icon is-small">
                        <i class="fa-solid fa-arrow-left"></i>
                      </span>
                    </button>
                  </div>
                </div>
              </nav>
            </div>
            <Preview :item="selectedMediaRef" />
          </nav>
          <nav
            class="panel"
            v-else-if="searchTotalCountRef === null"
            key="search"
          >
            <div class="panel-block">
              <form @submit.prevent>
                <div class="control">
                  <input
                    class="input is-outlined has-text-weight-bold"
                    type="text"
                    placeholder="Keywords"
                    v-model="queryRef"
                  />
                </div>
              </form>
            </div>
            <div class="panel-block">
              <nav class="level is-mobile">
                <div class="level-left">
                  <div class="level-item">
                    <h3 class="panel-heading is-uppercase has-text-weight-bold">
                      Image
                    </h3>
                  </div>
                  <transition name="fade" mode="out-in">
                    <div
                      class="level-item"
                      v-show="imageDataUrlRef !== null"
                      key="attaced"
                    >
                      <span class="icon is-primary">
                        <i class="fa-solid fa-check"></i>
                      </span>
                    </div>
                  </transition>
                </div>
                <div class="level-right">
                  <div class="level-item">
                    <button
                      class="button toggle is-rounded"
                      @click="imageIsCollapsedRef = !imageIsCollapsedRef"
                    >
                      <span
                        class="icon is-small"
                        v-bind:class="{ collapsed: imageIsCollapsedRef }"
                      >
                        <i class="fa-solid fa-chevron-up"></i>
                      </span>
                    </button>
                  </div>
                </div>
              </nav>
              <transition name="fade" mode="out-in">
                <div
                  class="control"
                  v-show="!imageIsCollapsedRef"
                  key="collapse"
                >
                  <div
                    class="drop"
                    v-bind:style="{
                      animationPlayState: isDragging ? 'running' : 'paused',
                    }"
                    @dragover.prevent="dragover($event)"
                    @dragleave.prevent="isDragging = false"
                    @drop.stop.prevent="drop($event)"
                  >
                    <transition name="fade" mode="out-in">
                      <div
                        class="image"
                        v-if="imageDataUrlRef === null"
                        v-bind:key="imageDataUrlRef"
                      >
                        <div class="level">
                          <div class="level-item">
                            <label
                              class="
                                file
                                button
                                is-circle
                                has-text-weight-bold
                                file-label
                              "
                            >
                              <input
                                class="file-input"
                                type="file"
                                name="upload"
                                accept="image/apng, image/png, image/jpeg, image/webp"
                                style="pointer-events: none"
                                v-bind:disabled="isLoading"
                                @change="browse($event)"
                              />
                              <div class="file-cta_">
                                <span class="icon">
                                  <i class="fa-solid fa-file-image"></i>
                                </span>
                              </div>
                            </label>
                          </div>
                          <div class="level-item">
                            <span
                              class="
                                is-size-7 is-uppercase
                                has-text-weight-bold
                              "
                              >Image</span
                            >
                          </div>
                        </div>
                      </div>
                      <div class="image" v-else key="empty">
                        <div
                          class="image"
                          v-bind:style="{
                            backgroundImage: 'url(' + imageDataUrlRef + ')',
                          }"
                        >
                          <div class="control">
                            <button
                              class="button is-circle"
                              type="button"
                              @click="reset($event)"
                              key="menu"
                            >
                              <span class="icon is-small has-text-danger">
                                <i class="fa-solid fa-xmark"></i>
                              </span>
                            </button>
                          </div>
                        </div>
                      </div>
                    </transition>
                  </div>
                </div>
              </transition>
            </div>
            <ListBox
              name="Categories"
              :max-length="maxCategoriesLength"
              :is-enabled="user !== null && searchTotalCountRef === null"
              :is-collapsed="categoriesIsCollapsedRef"
              :is-continuous="categoriesIsContinuousRef"
              :items="categoriesItemsRef"
              :page-index="categoriesPageIndexRef"
              @collapse="collapseCategories"
              @clear="clearCategories"
              @select="selectCategory"
              @next="nextCategories"
              @previous="previousCategories"
            />
            <ListBox
              name="Types"
              :max-length="maxTypesLength"
              :is-enabled="user !== null && searchTotalCountRef === null"
              :is-collapsed="typesIsCollapsedRef"
              :is-continuous="typesIsContinuousRef"
              :items="typesItemsRef"
              :page-index="typesPageIndexRef"
              @collapse="collapseTypes"
              @clear="clearTypes"
              @select="selectType"
              @next="nextTypes"
              @previous="previousTypes"
            />
            <ListBox
              name="Users"
              :max-length="maxUsersLength"
              :is-enabled="user !== null && searchTotalCountRef === null"
              :is-collapsed="usersIsCollapsedRef"
              :is-continuous="usersIsContinuousRef"
              :items="usersItemsRef"
              :page-index="usersPageIndexRef"
              @collapse="collapseUsers"
              @clear="clearUsers"
              @select="selectUser"
              @next="nextUsers"
              @previous="previousUsers"
            />
            <div class="panel-block">
              <div class="control">
                <button
                  class="
                    button
                    is-rounded is-outlined is-fullwidth is-size-6 is-primary
                  "
                  type="submit"
                  v-bind:disabled="user === null || isSearchingRef"
                  @click="search"
                >
                  <transition name="fade" mode="out-in">
                    <span class="icon" v-if="isSearchingRef" key="searching">
                      <i class="fas fa-spinner updating"></i>
                    </span>
                    <span class="icon" v-else key="ready">
                      <i class="fa-solid fa-magnifying-glass"></i>
                    </span>
                  </transition>
                  <span class="is-uppercase has-text-weight-bold">Search</span>
                </button>
              </div>
            </div>
          </nav>
          <nav class="panel" v-else key="results">
            <div class="panel-block">
              <nav class="level is-mobile">
                <div class="level-left">
                  <div class="level-item">
                    <button class="button is-rounded" @click="back($event)">
                      <span class="icon is-small">
                        <i class="fa-solid fa-arrow-left"></i>
                      </span>
                    </button>
                  </div>
                </div>
              </nav>
            </div>
            <Results
              :is-fetching="isSearchingRef"
              :items="searchResultsRef"
              :count="searchTotalCountRef"
              :page-index="searchPageIndexRef"
              :page-length="searchPageLength"
              @select="selectMedia"
              @next="nextResults"
              @previous="previousResults"
              v-if="selectedMediaRef === null"
              key="results"
            />
          </nav>
        </transition>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
#search {
  position: relative;
  width: 100%;
  height: 100%;

  #map {
    position: absolute;
    width: 100%;
    height: 100%;

    button {
      border-radius: 0 !important;
    }
  }

  .wrap {
    z-index: 1;
    position: relative;
    box-sizing: border-box;
    display: block;
    top: 0px;
    margin: 0;
    padding: 16px;
    width: fit-content;
    max-height: 100%;
    background: transparent;
    overflow-x: hidden;
    overflow-y: auto;

    > .block {
      width: 400px;

      .panel {
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
          0 0px 0 1px rgb(10 10 10 / 2%);
        overflow: hidden;

        .panel-block {
          flex-direction: column;

          > .level {
            margin: 0;
            padding: 0;
            width: 100%;

            > .level-left > .level-item > .panel-heading {
              margin: 0 !important;
              padding: 0;
              background: transparent;
            }

            > .level-right {
              margin: 0px 0px 0px 12px;

              button.is-rounded {
                border-radius: 9999px !important;
                padding: 12px !important;
                box-shadow: none !important;

                > span.icon {
                  margin: 0 !important;
                  width: 1rem !important;
                  height: 1rem !important;
                }
              }

              button.toggle {
                > span {
                  transform: rotate(180deg);
                }

                > span.collapsed {
                  transition: transform 0.5s ease;
                  transform: rotate(0deg);
                }
              }
            }
          }
        }

        .panel-tabs:not(:last-child),
        .panel-block:not(:last-child) {
          border-bottom: 1px solid hsl(0deg, 0%, 93%);

          .drop {
            display: flex;
            margin: 0.5em 0px 0px 0px;
            padding: 4px;
            width: 100%;
            aspect-ratio: 16 / 9;
            border-radius: 8px;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: linear-gradient(
                90deg,
                hsl(0deg, 0%, 93%) 50%,
                transparent 50%
              ),
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

              .control {
                position: absolute;
                top: 0;
                right: 0;
                margin: 4px 4px 0px 0px;
              }

              .level {
                display: flex;
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
          }
        }
      }

      button {
        border-radius: 8px;
        box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
          0 0px 0 1px rgb(10 10 10 / 2%) !important;
      }
    }

    form {
      width: 100%;

      .control {
        margin: 0;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        width: 100%;

        input {
          margin: 0;
          border: 0px none transparent;
          padding: 24px 12px 24px 12px;
          background-color: transparent;
          box-shadow: none;
          backface-visibility: hidden;
          border: 1px solid hsl(0deg, 0%, 93%);
        }

        input::placeholder {
          color: rgba(0, 0, 0, 0.5);
          text-transform: uppercase;
          text-shadow: none;
        }

        button.is-rounded {
          border-radius: 9999px !important;
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
