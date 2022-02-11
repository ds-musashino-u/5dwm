<script>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import Sidebar from "./components/Sidebar.vue";
import Menu from "./components/Menu.vue";
import Search from "./components/Search.vue";
import Upload from "./components/Upload.vue";

export default {
  components: {
    Sidebar,
    Menu,
    Search,
    Upload,
  },
  data() {
    return {
      isRevealed: false,
      contentIndex: 0,
      contents: [
        { icon: "fa-solid fa-magnifying-glass", name: "Search", component: "Search" },
        { icon: "fa-solid fa-cloud-arrow-up", name: "Upload", component: "Upload" },
      ],
    };
  },
  methods: {
    reveal() {
      this.isRevealed = !this.isRevealed;
    },
    select(data) {
      this.contentIndex = parseInt(data.index);
      this.isRevealed = false;
    },
  },
  mounted() {},
};
</script>

<template>
  <!--<img alt="Vue logo" src="./assets/logo.png" />-->
  <Sidebar
    :items="contents"
    :index="contentIndex"
    @reveal="reveal"
    @select="select"
  />
  <div class="wrap">
    <div class="content">
      <keep-alive>
        <component :is="contents[contentIndex].component" v-bind="{ text: contents[contentIndex].name }"></component>
      </keep-alive>
    </div>
    <transition name="reveal">
      <Menu
        v-bind:items="contents"
        @select="select"
        v-if="isRevealed"
      />
    </transition>
  </div>
  <div class="left is-hidden-tablet" v-cloak>
    <transition name="fade" mode="out-in">
      <button class="button is-rounded" type="button" @click="reveal" key="menu">
        <span class="icon is-small">
          <i class="fas fa-bars"></i>
        </span>
      </button>
    </transition>
  </div>
</template>

<style lang="scss">
</style>
