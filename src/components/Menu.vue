<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref } from "vue";

const props = defineProps({
  items: Array
});
const emit = defineEmits(["reveal", "select"]);
const select = (event) => {
  emit("select", event.target.dataset);
};
</script>

<template>
  <div id="menu" ref="menu">
    <div class="columns is-centered">
      <div class="column is-half is-mobile">
        <div class="control" v-cloak>
          <transition name="fade" mode="out-in">
            <nav class="level" key="main">
              <div class="level-item" v-for="(item, index) in items" v-bind:key="item">
                <article class="media">
                  <div class="media-content">
                    <div class="content">
                      <button
                        class="button is-rounded is-size-7 is-primary"
                        type="button"
                        v-bind:data-index="index"
                        v-bind:data-name="item.name"
                        @click="select"
                      >
                        <span class="icon">
                          <i v-bind:class="item.icon"></i>
                        </span>
                        <span class="is-uppercase has-text-weight-bold">{{ item.name }}</span>
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
