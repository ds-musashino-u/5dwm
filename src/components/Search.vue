<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onActivated, onDeactivated } from "vue";
import { getCategories } from "../presenters/categories.mjs";
import { getUsers } from "../presenters/users.mjs";
import { search as searchWorldMap } from "../presenters/search.mjs";

const mapRef = ref(null);
const queryRef = ref("");
const props = defineProps({
  text: String,
});
/*const emit = defineEmits(["reveal", "select"]);
const select = (event) => {
  emit("select", event.target.dataset);
};*/
let map = null;
const results = [];

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
  } catch (error) {
    console.error(error);
  }

  try {
    const users = await getUsers();

    console.log(users);
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

const search = async (event, query) => {
  //emit("search", event);
  //Endpoints.SEARCH_URL
  //https://5dworldmap.com/api/v1/echo
  console.log(query);  

  for (const result of results) {
    result.marker.setMap(null);
  }

  results.splice(0);

  if (map !== null) {
    try {
      const searchItems = await searchWorldMap(["air pollution"]);
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
        bounds.extend(new google.maps.LatLng(media.location.latitude, media.location.longitude));

        results.push({ marker: marker, media: media });
      }

      map.fitBounds(bounds);
    } catch (error) {
      console.error(error);
    }
  }
};

// https://www.5dwm.mydns.jp:8181/5dtest/QuerySearch
// var data = "imgurl=" + imageUrl + "&keyword=" + keywords + "&ctg=" + categories + "&kind=" + kinds + "&db=" + databases;
// imgurl=&keyword=&ctg={"air pollution"}&kind=&db=
</script>

<template>
  <div id="search">
    <div id="map" ref="mapRef"></div>
    <div class="wrap">
      <form onsubmit="return false;">
        <div class="field has-addons">
          <div class="control">
            <input
              class="input is-size-7"
              type="text"
              placeholder="Keywords"
              v-model="queryRef"
            />
          </div>
          <div class="control">
            <button
              class="button is-rounded is-size-7 is-primary"
              type="submit"
              @click="search($event, queryRef)"
            >
              <span class="icon">
                <i class="fa-solid fa-magnifying-glass"></i>
              </span>
              <span class="has-text-weight-bold">Search</span>
            </button>
          </div>
        </div>
      </form>
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
    display: block;
    top: 10px;
    margin: 0px 16px 0px 16px;
    width: fit-content;
    background: #ffffff;
    border-radius: 290486px;
    overflow: hidden;

    .field {
      margin: 0px -8px 0px -8px;
      padding: 8px;

      .control {
        margin: 0px 8px 0px 8px;
        display: flex;
        justify-content: flex-start;
        align-items: center;

        input {
          margin: 0px 0px 0px 8px;
          border: 0px none transparent;
          background-color: transparent;
          box-shadow: none;
          backface-visibility: hidden;
        }

        input::placeholder {
          color: rgba(0, 0, 0, 0.5);
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
