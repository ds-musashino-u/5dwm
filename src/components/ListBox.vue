<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref } from "vue";

const props = defineProps({
  items: Array,
});
const emit = defineEmits(["select"]);
const select = (event) => {
  emit("select", event.target.dataset);
};
</script>

<template>
  <div class="panel-block">
    <h3 class="panel-heading is-uppercase has-text-weight-bold">Categories</h3>
    <label class="control">
      <input type="checkbox" @change="select" v-bind:checked="true" />
      <span class="custom"></span>
      <span class="is-size-6 has-text-weight-bold">Test</span>
    </label>
    <label class="control">
      <input type="checkbox" @change="select" v-bind:checked="true" />
      <span class="custom"></span>
      <span class="is-size-6 has-text-weight-bold">Sample</span>
    </label>
    <div class="control">
      <button class="button is-link is-outlined is-fullwidth">Next</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.panel-block {
  flex-direction: column;
  align-items: flex-start;

  .panel-heading {
    padding: 0px 0px 6px 6px;
    background: transparent;
  }

  label {
    padding: 6px 6px 6px 6px;
  }

  label > span {
    user-select: none;
  }

  label > span:not(:first-of-type) {
    margin: 0px 0px 0px 12px;
  }

  label input[type="checkbox"],
  label input[type="radio"] {
    display: none;
  }

  label .custom {
    position: relative;
    margin: 0;
    font-size: 1rem;
  }

  label input[type="checkbox"] + .custom:before,
  label input[type="radio"] + .custom:before {
    font-weight: 900;
    font-family: "Font Awesome 6 Free";
    content: "\f00c";
    color: transparent;
    text-shadow: none;
  }

  label input[type="checkbox"]:checked + .custom:before,
  label input[type="radio"]:checked + .custom:before {
    color: var(--accent-color);
    transition: 0.5s;
  }
}
</style>
