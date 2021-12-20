<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref } from "vue";

const props = defineProps({
  items: Array,
  index: { type: Number, required: false, default: 0 },
});
const emit = defineEmits(["reveal", "select"]);

const selectedIndex = ref(props.index);
const reveal = () => {
  emit("reveal");
};
const select = (event) => {
  emit("select", event.target.dataset);
  selectedIndex.value = parseInt(event.target.dataset.index);
};
</script>

<template>
  <div id="sidebar" class="is-hidden-mobile">
    <div class="level">
      <div class="level-item">
        <div class="level">
          <div class="level-item">
            <transition name="fade" mode="out-in">
              <button class="button" type="button" @click="reveal" key="reveal">
                <span class="icon is-small">
                  <i class="fas fa-bars"></i>
                </span>
              </button>
            </transition>
          </div>
          <div
            class="level-item"
            v-for="(item, index) in items"
            v-bind:key="item"
          >
            <button
              class="button"
              type="button"
              v-bind:class="{ 'has-text-primary': selectedIndex === index }"
              v-bind:data-index="index"
              v-bind:data-name="item.name"
              @click="select"
            >
              <span class="icon is-large">
                <i v-bind:class="item.icon"></i>
              </span>
              <span class="is-size-7 has-text-weight-bold">{{
                item.name
              }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>
