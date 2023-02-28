<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, toRef, watchEffect } from "vue";

const props = defineProps({
  user: { type: Object, required: false, default: null },
  items: Array,
  index: { type: Number, required: false, default: 0 },
  isRevealed: { type: Boolean, required: false, default: false }
});
const emit = defineEmits(["reveal", "select"]);
const propsIndexRef = toRef(props, "index");
const selectedIndex = ref(props.index);
const reveal = () => {
  emit("reveal");
};
const select = (event) => {
  emit("select", event.target.dataset);
};

watchEffect(() => (selectedIndex.value = propsIndexRef.value));
</script>

<template>
  <div id="sidebar" class="is-hidden-mobile">
    <div class="level">
      <div class="level-item">
        <div class="level">
          <div class="level-item">
            <transition name="fade" mode="out-in">
              <button class="button" type="button" v-bind:disabled="user === null" @click="reveal" key="reveal">
                <transition name="fade" mode="out-in">
                  <span class="icon is-small" v-if="props.isRevealed" key="open">
                    <i class="fa-solid fa-xmark"></i>
                  </span>
                  <span class="icon is-small" v-else key="close">
                    <i class="fa-solid fa-bars"></i>
                  </span>
                </transition>
              </button>
            </transition>
          </div>
          <div class="level-item" v-for="(item, index) in items" v-bind:key="item">
            <button class="button" type="button" v-bind:class="{ 'has-text-primary': selectedIndex === index }"
              v-bind:disabled="user === null" v-bind:data-index="index" v-bind:data-name="item.name" @click="select">
              <span class="icon is-large">
                <i v-bind:class="item.icon"></i>
              </span>
              <span class="is-size-7 is-uppercase has-text-weight-bold">{{
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
#sidebar {
  border-right: 1px solid hsl(0deg, 0%, 93%);
}
</style>
