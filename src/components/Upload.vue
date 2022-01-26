<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref } from "vue";

const props = defineProps({
  text: String,
});
const isUploading = ref(false);
const upload = async (event) => {
  isUploading.value = true;
  
  for (const file of event.currentTarget.files) {
    try {
      const dataURL = await new Promise(function (resolve, reject) {
        const reader = new FileReader();

        reader.onload = () => {
          resolve(reader.result);
        };
        reader.onerror = () => {
          reject(reader.error);
        };

        if (file) {
          reader.readAsDataURL(file);
        }
      });

      const response = await fetch("https://www.5dworldmap.com//api/v1/upload", {
        mode: "cors",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image: dataURL }),
      });

      if (response.ok) {
        console.log(await response.json());
      } else {
        throw new Error(response.statusText);
      }
    } catch (error) {
      console.error(error);
    }
  }

  isUploading.value = false;
};
</script>

<template>
  <div id="upload">
    <div class="level">
      <div class="level-item">
        <span>{{ text }}</span>
      </div>
      <div class="level-item">
        <span class="file button is-rounded is-size-7 has-text-weight-bold">
          <label class="file-label">
            <input
              class="file-input"
              type="file"
              name="upload"
              accept="image/apng, image/png, image/jpeg, image/webp"
              style="pointer-events: none"
              v-bind:disabled="isUploading"
              @change="upload($event)"
            />
            <div class="file-cta_">
              <transition name="fade" mode="out-in">
                <span class="icon" v-if="isUploading" key="uploading">
                  <i class="fas fa-spinner updating"></i>
                </span>
                <span class="icon" v-else key="ready">
                  <i class="fas fa-cloud-upload-alt"></i>
                </span>
              </transition>
              <span>Upload</span>
            </div>
          </label>
        </span>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>
