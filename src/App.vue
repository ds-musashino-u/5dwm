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
      page: null,
    };
  },
  methods: {
    reveal() {
      this.isRevealed = !this.isRevealed;
    },
    select: (data) => {
      //console.log(data.index);
      //console.log(data.name);
    },
  },
  mounted() {},
};
</script>

<template>
  <!--<img alt="Vue logo" src="./assets/logo.png" />-->
  <Sidebar
    v-bind:items="[{ icon: 'fas fa-search', name: 'Search' }]"
    @reveal="reveal"
    @select="select"
  />
  <div class="wrap">
    <div class="content">
      <span>Content is here.</span>
    </div>
    <transition name="reveal">
      <Menu v-if="isRevealed" />
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
