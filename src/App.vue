<script>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import Sidebar from './components/Sidebar.vue'

export default {
  components: {
    Sidebar
  },
  data() {
    return {
      page: null
    }
  }
}
</script>

<template>
  <img alt="Vue logo" src="./assets/logo.png" />
  <Sidebar msg="Hello Vue 3 + Vite" />
</template>

<style lang="sass">
</style>
