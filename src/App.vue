<script>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import Sidebar from "./components/Sidebar.vue";

export default {
  components: {
    Sidebar,
  },
  data() {
    return {
      isRevealed: false,
      page: null,
    };
  },
  methods: {
    reveal: () => {
    },
    select: (data) => {
      //console.log(data.index);
      //console.log(data.name);
    },
  },
  mounted: () => {
  }
};
</script>

<template>
  <!--<img alt="Vue logo" src="./assets/logo.png" />-->
  <Sidebar v-bind:items="[{ icon: 'fas fa-search', name: 'Search' }]" @reveal="reveal" @select="select" />
  <div class="wrap">
    <div class="content">
      <span>Content is here.</span>
    </div>
  </div>
</template>

<style lang="scss">
#app {
  position: absolute;
  display: flex;
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-start;
}

#app > .wrap {
  position: relative;
  margin: 0;
  padding: 0;
  width: 100%;
  max-width: 100% !important;
  height: 100%;
}

#app > .wrap > .content {
  position: absolute;
  margin: 0;
  padding: 16px;
  width: 100%;
  height: 100%;
  min-height: 100%;
  overflow: hidden;
}
</style>
