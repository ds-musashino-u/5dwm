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
  //selectedIndex.value = -1;
};
const select = (event) => {
  emit("select", event.target.dataset);
  selectedIndex.value = parseInt(event.target.dataset.index);
};
</script>

<template>
  <div id="sidebar" class="is-hidden-mobile">
    <div class="level">
      <div class="level-item">
        <div class="level">
          <div class="level-item">
            <transition name="fade" mode="out-in">
              <button class="button" type="button" @click="reveal" key="reveal">
                <span class="icon is-small">
                  <i class="fas fa-bars"></i>
                </span>
              </button>
            </transition>
          </div>
          <div
            class="level-item"
            v-for="(item, index) in items"
            v-bind:key="item"
          >
            <button
              class="button"
              type="button"
              v-bind:class="{ 'has-text-primary': selectedIndex === index }"
              v-bind:data-index="index"
              v-bind:data-name="item.name"
              @click="select"
            >
              <span class="icon is-large">
                <i v-bind:class="item.icon"></i>
              </span>
              <span class="is-size-7 has-text-weight-bold">{{
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
  position: relative;
  padding: env(safe-area-inset-top, 0px) 16px env(safe-area-inset-bottom, 0px)
    calc(env(safe-area-inset-left, 0px) + 16px);
  width: fit-content;
  height: 100%;
  background: #ffffff;

  button,
  .button {
    border: 0px solid transparent;

    span {
      pointer-events: none;
    }
  }

  > .level {
    display: flex;
    margin: 0;
    padding: 0;
    height: 100%;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;

    > .level-item:first-child {
      display: flex;
      top: 0;
      margin: 0;
      padding: 32px 0px 32px 0px;
      flex-direction: column;
      align-items: flex-start;
      justify-content: flex-start;

      > .level {
        display: flex;
        margin: 0;
        padding: 0;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;

        > .level-item:first-child {
          margin: 0;
          padding: 0;
        }

        > .level-item:not(:first-child) {
          margin: 0;
          padding: 32px 0px 0px 0px;

          button,
          .button {
            display: flex;
            align-items: center;
            margin: 0;
            padding: 0;
            background-clip: padding-box;
            height: fit-content;
            backface-visibility: hidden;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            width: 64px;

            .icon:first-child:not(:last-child) {
              margin: 0px 0px 8px 0px;
            }
          }
        }
      }
    }

    > .level-item:last-child:not(:first-child) {
      position: absolute;
      bottom: 0;
      margin: 0;
      padding: 0px 0px 32px 0px;
    }
  }
}
</style>
