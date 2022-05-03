<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref } from "vue";

const props = defineProps({
  name: { type: String, required: false, default: null },
  maxLength: { type: Number, required: false, default: 10 },
  items: { type: Array, required: false, default: null },
});
const emit = defineEmits(["select"]);
const select = (event, index) => {
  props.items[index].checked = !props.items[index].checked;

  emit("select", event.target.dataset, index);
};
const next = (event) => {
  console.log("next");
};
const previous = (event) => {
  console.log("previous");
};
</script>

<template>
  <div class="panel-block">
    <h3
      class="panel-heading is-uppercase has-text-weight-bold"
      v-text="name"
      v-if="name !== null"
    ></h3>
    <transition name="fade" mode="out-in">
      <div class="control" v-if="items === null" key="loading">
        <nav class="level">
          <div class="level-item">
            <span class="icon">
              <i class="fas fa-spinner updating"></i>
            </span>
          </div>
        </nav>
      </div>
      <div class="control" v-else key="default">
        <label v-for="(item, index) in items" v-bind:key="item">
          <input
            type="checkbox"
            @change="select($event, index)"
            v-bind:checked="item.checked"
          />
          <span class="custom"></span>
          <span
            class="is-size-6 has-text-weight-bold"
            v-text="item.name"
          ></span>
        </label>
      </div>
    </transition>
    <div class="control">
      <nav class="level">
        <div class="level-left">
          <div class="level-item">
            <button class="button" @click="previous($event)">
              <span class="icon is-small">
                <i class="fa-solid fa-chevron-left"></i>
              </span>
            </button>
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <button class="button" @click="next($event)">
              <span class="icon is-small">
                <i class="fa-solid fa-chevron-right"></i>
              </span>
            </button>
          </div>
        </div>
      </nav>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.panel-block {
  flex-direction: column;
  align-items: flex-start;
  padding: 0;

  .panel-heading {
    padding: 0.5em 0.75em;
    background: transparent;
  }

  .control {
    display: flex;

    .level {
      padding: 0.5em 0.75em;
      width: 100%;
    }

    label {
      padding: 0.5em 0.75em;
      width: 100%;
      background-color: transparent;
      transition: background-color 0.5s;
    }

    label:hover {
      background-color: hsl(0deg, 0%, 93%);
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
}
</style>
