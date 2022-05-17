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

const mapRef = ref(null);
const searchPanelRef = ref(null);
const queryRef = ref("");
const isDragging = ref(false);
const isLoading = ref(false);
const imageDataUrlRef = ref(null);
const isSearching = ref(false);
const props = defineProps({
  auth0: Object,
  user: Object,
  text: String,
});
/*const emit = defineEmits(["reveal", "select"]);
const select = (event) => {
  emit("select", event.target.dataset);
};*/
let map = null;
const results = [];
const selectedCategories = {};
const selectedTypes = {};
const selectedUsers = {};

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
  const element = results.find(
    (x) =>
      x.marker !== null &&
      event.latLng.lat === x.marker.position.lat &&
      event.latLng.lng === x.marker.position.lng
  );

  if (element !== undefined) {
    console.log(element);
  }
  /*for (const marker of markers) {
    if (marker.latLng === event.latLng) {
      console.log("find");
      map.setCenter(marker.getPosition());

      break;
    }
  }*/
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
const selectCategory = (index, item) => {
  if (index in selectedCategories) {
    if (!item.checked) {
      delete selectedCategories[index];
    }
  } else if (item.checked) {
    selectedCategories[index] = item.name;
  }
};
const selectType = (index, item) => {
  if (index in selectedTypes) {
    if (!item.checked) {
      delete selectedTypes[index];
    }
  } else if (item.checked) {
    selectedTypes[index] = item.name;
  }
};
const selectUser = (index, item) => {
  if (index in selectedUsers) {
    if (!item.checked) {
      delete selectedUsers[index];
    }
  } else if (item.checked) {
    selectedUsers[index] = item.name;
  }
};
const fetchCategories = async (offset, length, items, isFetchingRef) => {
  isFetchingRef.value = true;

  try {
    let index = 0;

    for (const item of await getCategories(offset, length)) {
      items.push({ index: offset + index, name: item.name });
      index++;
    }
  } catch (error) {
    console.error(error);
  }

  isFetchingRef.value = false;
};
const fetchTypes = async (offset, length, items, isFetchingRef) => {
  isFetchingRef.value = true;

  try {
    let index = 0;

    for (const item of await getTypes(null, null, offset, length)) {
      items.push({ index: offset + index, name: item });
      index++;
    }
  } catch (error) {
    console.error(error);
  }

  isFetchingRef.value = false;
};
const fetchUsers = async (offset, length, items, isFetchingRef) => {
  isFetchingRef.value = true;

  try {
    let index = 0;

    for (const item of await getUsers(offset, length)) {
      items.push({ index: offset + index, name: item.username });
      index++;
    }
  } catch (error) {
    console.error(error);
  }

  isFetchingRef.value = false;
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

const search = async (event, keywords) => {
  //emit("search", event);
  //Endpoints.SEARCH_URL
  //https://5dworldmap.com/api/v1/echo
  isSearching.value = true;

  for (const result of results) {
    result.marker.setMap(null);
  }

  results.splice(0);

  if (map === null) {
    shake(searchPanelRef.value);
  } else {
    try {
      const idToken = await props.auth0.getIdTokenClaims();
      const [searchItems, totalCount] = await searchWorldMap(
        idToken.__raw,
        keywords.split(/\s/),
        Object.values(selectedCategories),
        Object.values(selectedTypes),
        Object.values(selectedUsers)
      );
      const bounds = new google.maps.LatLngBounds();

      for (const media of searchItems) {
        if (media.location === null) {
          results.push({ marker: null, media: media });
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

          marker.addListener("click", markerClick);
          bounds.extend(
            new google.maps.LatLng(
              media.location.latitude,
              media.location.longitude
            )
          );

          results.push({ marker: marker, media: media });
        }
      }

      map.fitBounds(bounds);
    } catch (error) {
      shake(searchPanelRef.value);
      console.error(error);
    }
  }

  isSearching.value = false;
};

// https://www.5dwm.mydns.jp:8181/5dtest/QuerySearch
// var data = "imgurl=" + imageUrl + "&keyword=" + keywords + "&ctg=" + categories + "&kind=" + kinds + "&db=" + databases;
// imgurl=&keyword=&ctg={"air pollution"}&kind=&db=
</script>

<template>
  <div id="search">
    <div id="map" ref="mapRef"></div>
    <div class="wrap">
      <div class="block is-hidden-mobile">
        <nav class="panel" ref="searchPanelRef">
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
            <div class="control">
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
                          class="is-size-7 is-uppercase has-text-weight-bold"
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
          </div>
          <ListBox
            name="Categories"
            :max-length="10"
            :is-enabled="user !== null"
            :is-collapsed="true"
            @select="selectCategory"
            @fetch="fetchCategories"
          />
          <ListBox
            name="Types"
            :max-length="25"
            :is-enabled="user !== null"
            :is-collapsed="true"
            @select="selectType"
            @fetch="fetchTypes"
          />
          <ListBox
            name="Users"
            :max-length="10"
            :is-enabled="user !== null"
            :is-collapsed="true"
            @select="selectUser"
            @fetch="fetchUsers"
          />
          <div class="panel-block">
            <div class="control">
              <button
                class="
                  button
                  is-rounded is-outlined is-fullwidth is-size-6 is-primary
                "
                type="submit"
                v-bind:disabled="user === null || isSearching"
                @click="search($event, queryRef)"
              >
                <transition name="fade" mode="out-in">
                  <span class="icon" v-if="isSearching" key="searching">
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
      </div>
      <div class="block"></div>
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
    /*border-radius: 290486px;*/
    /*overflow: hidden;*/
    overflow-x: hidden;
    overflow-y: auto;

    > .block {
      .panel {
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
          0 0px 0 1px rgb(10 10 10 / 2%);

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
