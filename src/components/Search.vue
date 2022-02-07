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
  });

  await loader.load();

  const _map = new google.maps.Map(map.value, {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 8,
  });
});
onDeactivated(() => {});
</script>

<template>
  <div id="search">
    <div id="map" ref="map"></div>
    <span>{{ text }}</span>
  </div>
</template>

<style lang="scss" scoped>
#search {
  position: relative;
  width: 100%;
  height: 100%;

  #map {
    position: relative;
    width: 100%;
    height: 100%;

    button {
      border-radius: 0 !important;
    }
  }  
}
</style>
