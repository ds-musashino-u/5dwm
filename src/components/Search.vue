<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onActivated, onDeactivated } from "vue";
import { getCategories } from "../presenters/categories.mjs";
import { getMedia } from "../presenters/media.mjs";
import { getUsers } from "../presenters/users.mjs";
import { search as searchWorldMap } from "../presenters/search.mjs";
import ListBox from "./ListBox.vue";

const mapRef = ref(null);
const queryRef = ref("");
const isSearching = ref(false);
const props = defineProps({
  text: String,
});
/*const emit = defineEmits(["reveal", "select"]);
const select = (event) => {
  emit("select", event.target.dataset);
};*/
let map = null;
const results = [];
const selectedCategories = {};

onActivated(async () => {
  const loader = new Loader({
    apiKey: "AIzaSyCJfuPZn56-CDI74WPsUPGrQ3bI6hm7H9c",
    version: "weekly",
    language: "en",
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

const selectCategory = (index, item) => {
  if (index in selectedCategories) {
    if (!item.checked) {
      delete selectedCategories[index];
    }
  } else if (item.checked) {
    selectedCategories[index] = item.name;
  }
};

const fetchCategories = async (offset, length, itemsRef, isFetchingRef) => {
  isFetchingRef.value = true;

  try {
    let index = 0;

    for (const item of await getCategories(offset, length)) {
      itemsRef.value.push({ index: offset + index, name: item.name });
      index++;
    }
  } catch (error) {
    console.error(error);
  }

  isFetchingRef.value = false;
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

  if (map !== null) {
    try {
      const searchItems = await searchWorldMap(keywords.split(/\s/), Object.values(selectedCategories), []);
      const bounds = new google.maps.LatLngBounds();

      for (const media of searchItems) {
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

      map.fitBounds(bounds);
    } catch (error) {
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
      <div class="block">
        <nav class="panel">
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
          <ListBox
            name="Categories"
            :max-length="10"
            :is-collapsed="true"
            @select="selectCategory"
            @fetch="fetchCategories"
          />
          <div class="panel-block">
            <div class="control">
              <button
                class="
                  button
                  is-rounded is-outlined is-fullwidth is-size-6 is-primary
                "
                type="submit"
                v-bind:disabled="isSearching"
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
</style>
