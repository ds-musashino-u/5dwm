<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { Loader } from "@googlemaps/js-api-loader";
import { ref, onActivated, onDeactivated } from "vue";

const map = ref(null);
const props = defineProps({
  text: String,
});
/*const emit = defineEmits(["reveal", "select"]);
const select = (event) => {
  emit("select", event.target.dataset);
};*/

onActivated(async () => {
  const loader = new Loader({
    apiKey: "AIzaSyB-cMc1l64QCZqJ6NeNrXUIimQmkiqCXZk",
    version: "weekly",
    language: "en",
  });

  await loader.load();

  const googleMap = new google.maps.Map(map.value, {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 8,
  });
});
onDeactivated(() => { });

// https://www.5dwm.mydns.jp:8181/5dtest/QuerySearch

</script>

<template>
  <div id="search">
    <div id="map" ref="map"></div>
    <div class="center">
      <div class="field has-addons">
        <div class="control">
          <input class="input" type="text" placeholder="Keywords" />
        </div>
        <div class="control">
          <a class="button is-primary">Search</a>
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
      }
    }
  }
}
</style>
