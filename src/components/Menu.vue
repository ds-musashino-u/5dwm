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
  <div id="menu" ref="menu">
    <div
      class="columns is-centered">
      <div class="column is-half is-mobile">
        <div class="control" v-cloak>
          <transition
            name="fade"
            mode="out-in"
            v-on:before-leave="$refs.menu.scroll(0, 0)"
          >
            <nav class="level" key="main">
              <div class="level-item">
                <article class="media">
                  <div class="media-content">
                    <div class="content">
                      <button
                        class="button is-rounded is-size-6 is-primary"
                        type="button"
                      >
                        <span class="icon">
                          <i class="fas fa-search"></i>
                        </span>
                        <span class="has-text-weight-bold">Search</span>
                      </button>
                    </div>
                  </div>
                </article>
              </div>
            </nav>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
</style>
