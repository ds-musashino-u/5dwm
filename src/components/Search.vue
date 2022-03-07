<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onActivated, onDeactivated } from "vue";
import { getUsers } from "../presenters/users.mjs"

const mapRef = ref(null);
const queryRef = ref("");
const props = defineProps({
  text: String,
});
/*const emit = defineEmits(["reveal", "select"]);
const select = (event) => {
  emit("select", event.target.dataset);
};*/

onActivated(async () => {
  const loader = new Loader({
    apiKey: "AIzaSyCJfuPZn56-CDI74WPsUPGrQ3bI6hm7H9c",
    version: "weekly",
    language: "en",
  });

  await loader.load();

  const map = new google.maps.Map(mapRef.value, {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 8,
    mapTypeId: "terrain",
    zoomControl: true,
    mapTypeControl: false,
    scaleControl: true,
    streetViewControl: false,
    rotateControl: true,
    fullscreenControl: false
  });

  const users = await getUsers();

  console.log(users);
});
onDeactivated(() => { });

const search = async (event, query) => {
  //emit("search", event);
  //Endpoints.SEARCH_URL
  //https://5dworldmap.com/api/v1/echo
  const imageUrl = "";
  const keywords = "air pollution";
  const categories = "";
  const kinds = "";
  const databases = "";

  console.log(query);

  try {
    const response = await fetch("https://5dworldmap.com/api/v1/echo", {
      mode: "cors",
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: encodeURI(`https://www.5dwm.mydns.jp:8181/5dtest/QuerySearch?imgurl=${imageUrl}&keyword=${keywords}&ctg=${categories}&kind=${kinds}&db=${databases}`) })
    });

    if (response.ok) {
      console.log(await response.json());
    } else {
      throw new Error(response.statusText);
    }
  } catch (error) {
    console.error(error);
  }
};

// https://www.5dwm.mydns.jp:8181/5dtest/QuerySearch
// var data = "imgurl=" + imageUrl + "&keyword=" + keywords + "&ctg=" + categories + "&kind=" + kinds + "&db=" + databases;
// imgurl=&keyword=&ctg={"air pollution"}&kind=&db=

</script>

<template>
  <div id="search">
    <div id="map" ref="mapRef"></div>
    <div class="center">
      <form onsubmit="return false;">
        <div class="field has-addons">
          <div class="control">
            <input class="input is-size-7" type="text" placeholder="Keywords" v-model="queryRef" />
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

  .center {
    z-index: 1;
    position: relative;
    display: block;
    top: 10px;
    margin: 0 auto;
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
