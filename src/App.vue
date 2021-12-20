<script>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import Sidebar from "./components/Sidebar.vue";
import Menu from "./components/Menu.vue";

export default {
  components: {
    Sidebar,
    Menu,
  },
  data() {
    return {
      isRevealed: false,
      pageIndex: 0,
    };
  },
  methods: {
    reveal() {
      this.isRevealed = !this.isRevealed;
    },
    select(data) {
      this.pageIndex = parseInt(data.index);
      this.isRevealed = false;
    },
  },
  mounted() {},
};
</script>

<template>
  <!--<img alt="Vue logo" src="./assets/logo.png" />-->
  <Sidebar
    v-bind:items="[{ icon: 'fas fa-search', name: 'Search' }, { icon: 'fas fa-search', name: 'Search2' }]"
    v-bind:index="pageIndex"
    @reveal="reveal"
    @select="select"
  />
  <div class="wrap">
    <div class="content">
      <span>Content is here.</span>
    </div>
    <transition name="reveal">
      <Menu v-bind:items="[{ icon: 'fas fa-search', name: 'Search' }, { icon: 'fas fa-search', name: 'Search2' }]" @select="select" v-if="isRevealed" />
    </transition>
  </div>
  <div class="left is-hidden-tablet" v-cloak>
    <transition name="fade" mode="out-in">
      <button class="button" type="button" @click="reveal" key="menu">
        <span class="icon is-small">
          <i class="fas fa-bars"></i>
        </span>
      </button>
    </transition>
  </div>
</template>

<style lang="scss">
</style>
