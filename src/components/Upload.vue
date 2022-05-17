<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, onActivated, onDeactivated } from "vue";

const props = defineProps({
  auth0: Object,
  user: Object,
  text: String,
});
const emit = defineEmits(["completed", "updated"]);
const isUploading = ref(false);
const isUpdating = ref(false);
const pictures = ref([]);
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
        reader.readAsDataURL(file);
      });

      const response = await fetch(
        "https://www.5dworldmap.com/api/v1/upload",
        {
          mode: "cors",
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ image: dataURL }),
        }
      );

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

  emit("completed");
  update();
};
const update = async () => {
  isUpdating.value = true;

  try {
    const response = await fetch("https://www.5dworldmap.com/api/v1/recent", {
      mode: "cors",
      method: "GET",
    });

    if (response.ok) {
      pictures.value.splice(0);

      for (const item of await response.json()) {
        pictures.value.push(item);
      }
    } else {
      throw new Error(response.statusText);
    }
  } catch (error) {
    console.error(error);
  }

  isUpdating.value = false;

  emit("updated");
};

onActivated(() => {
  update();
});
onDeactivated(() => {
});
</script>

<template>
  <div id="upload">
    <div class="level">
      <div class="level-item">
        <span>{{ text }}</span>
      </div>
      <div class="level-item">
        <label
          class="
            file
            button
            is-rounded is-size-7
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
            v-bind:disabled="isUploading"
            @change="upload($event)"
          />
          <div class="file-cta_">
            <transition name="fade" mode="out-in">
              <span class="icon" v-if="isUploading" key="uploading">
                <i class="fas fa-spinner updating"></i>
              </span>
              <span class="icon" v-else key="ready">
                <i class="fa-solid fa-cloud-arrow-up"></i>
              </span>
            </transition>
            <span>Upload</span>
          </div>
        </label>
      </div>
      <div class="level-item">
        <button
          class="button is-rounded is-size-7 has-text-weight-bold"
          type="button"
          v-bind:disabled="isUpdating"
          @click="update()"
        >
          <span class="icon is-small">
            <i class="fa-solid fa-arrows-rotate" v-bind:class="{ loading: isUpdating }"></i>
          </span>
          <span>Update</span>
        </button>
      </div>
      <div class="level-item">
        <transition-group name="gallery-list" class="gallery" tag="div" v-cloak>
          <article
            class="media gallery-list-item"
            v-for="picture in pictures"
            v-bind:key="picture.id"
          >
            <div class="media-content">
              <figure>
                <p class="image is-128x128">
                  <img v-bind:src="picture.url" alt="Picture" />
                </p>
              </figure>
            </div>
          </article>
        </transition-group>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>
