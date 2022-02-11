<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onActivated, onDeactivated } from "vue";
import { Endpoints } from "../Endpoints";

const mapRef = ref(null);
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
  });
});
onDeactivated(() => { });

const search = (event) => {
  //emit("search", event);
  //Endpoints.SEARCH_URL
};

// https://www.5dwm.mydns.jp:8181/5dtest/QuerySearch
// var data = "imgurl=" + imageUrl + "&keyword=" + keywords + "&ctg=" + categories + "&kind=" + kinds + "&db=" + databases;
// imgurl=&keyword=&ctg={"air pollution"}&kind=&db=

</script>

<template>
  <div id="search">
    <div id="map" ref="mapRef"></div>
    <div class="center">
      <div class="field has-addons">
        <div class="control">
          <input class="input is-size-7" type="text" placeholder="Keywords" />
        </div>
        <div class="control">
          <button class="button is-rounded is-size-7 is-primary" type="button" @click="search($event)">
            <span class="icon">
              <i class="fa-solid fa-magnifying-glass"></i>
            </span>
            <span class="has-text-weight-bold">Search</span>
          </button>
        </div>
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
