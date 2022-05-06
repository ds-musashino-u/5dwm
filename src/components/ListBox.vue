<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, toRef, watch, watchEffect } from "vue";

const props = defineProps({
  name: { type: String, required: false, default: null },
  maxLength: { type: Number, required: false, default: 10 },
  items: { type: Array, required: false, default: null },
  isCollapsed: { type: Boolean, required: false, default: false },
});
const emit = defineEmits(["select", "fetch"]);
const propsItemsRef = toRef(props, "items");
const itemsRef = ref(props.items);
const pageIndexRef = ref(0);
const nextResultRef = ref([]);
const hasNextRef = ref(false);
const isFetchingRef = ref(false);
const cachedItems = {};
const select = (event, index) => {
  itemsRef.value[index].checked = !itemsRef.value[index].checked;

  emit("select", (pageIndexRef.value * props.maxLength) + index, itemsRef.value[index]);
};
const next = (event) => {
  pageIndexRef.value++;

  emit(
    "fetch",
    pageIndexRef.value * props.maxLength,
    props.maxLength + 1,
    nextResultRef,
    isFetchingRef
  );
};
const previous = (event) => {
  if (pageIndexRef.value > 0) {
    pageIndexRef.value--;
    itemsRef.value = [];

    for (let i = 0; i < props.maxLength; i++) {
      itemsRef.value.push(
        cachedItems[pageIndexRef.value * props.maxLength + i]
      );
    }
  }
};

watch(
  nextResultRef,
  (result) => {
    if (result.length > 0) {
      let length;

      if (result.length === props.maxLength + 1) {
        length = props.maxLength;
        hasNextRef.value = true;
      } else {
        length = result.length;
        hasNextRef.value = false;
      }

      itemsRef.value = [];

      for (let i = 0; i < length; i++) {
        if (
          result[i].index in cachedItems &&
          cachedItems[result[i].index].name === result[i].name
        ) {
          itemsRef.value.push(cachedItems[result[i].index]);
        } else {
          const item = { checked: false, name: result[i].name };

          itemsRef.value.push(item);
          cachedItems[result[i].index] = item;
        }
      }

      result.splice(0);
    }
  },
  { deep: true }
);
watchEffect(() => (itemsRef.value = propsItemsRef.value));
emit(
  "fetch",
  pageIndexRef.value * props.maxLength,
  props.maxLength + 1,
  nextResultRef,
  isFetchingRef,
);
</script>

<template>
  <div class="panel-block">
    <nav class="level">
      <div class="level-left" v-if="name !== null">
        <div class="level-item">
          <h3
            class="panel-heading is-uppercase has-text-weight-bold"
            v-text="name"
          ></h3>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <button class="button is-rounded" @click="isCollapsed = !isCollapsed">
            <transition name="fade" mode="out-in">
              <span class="icon is-small" v-if="isCollapsed" key="collapsed">
                <i class="fa-solid fa-plus"></i>
              </span>
              <span class="icon is-small" v-else key="visible">
                <i class="fa-solid fa-minus"></i>
              </span>
            </transition>
          </button>
        </div>
      </div>
    </nav>
    <transition name="fade" mode="out-in">
      <div
        class="control"
        v-if="!isCollapsed && itemsRef === null"
        key="loading"
      >
        <nav class="level">
          <div class="level-item">
            <span class="icon">
              <i class="fas fa-spinner updating"></i>
            </span>
          </div>
        </nav>
      </div>
      <div class="control" v-else-if="!isCollapsed" key="default">
        <label v-for="(item, index) in itemsRef" v-bind:key="item">
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
    <transition name="fade">
      <div class="control" v-show="!isCollapsed">
        <nav class="level">
          <div class="level-left">
            <div class="level-item">
              <button
                class="button"
                v-bind:disabled="pageIndexRef === 0 || isFetchingRef"
                @click="previous($event)"
              >
                <span class="icon is-small">
                  <i class="fa-solid fa-chevron-left"></i>
                </span>
              </button>
            </div>
          </div>
          <div class="level-right">
            <div class="level-item">
              <button
                class="button"
                v-bind:disabled="!hasNextRef || isFetchingRef"
                @click="next($event)"
              >
                <span class="icon is-small">
                  <i class="fa-solid fa-chevron-right"></i>
                </span>
              </button>
            </div>
          </div>
        </nav>
      </div>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.panel-block {
  flex-direction: column;
  align-items: flex-start;
  padding: 0;

  .level {
    margin: 0;
    padding: 0.5em 0.75em;
    width: 100%;

    .panel-heading {
      margin: 0;
      padding: 0;
      background: transparent;
    }

    > .level-right > .level-item {
      button.is-rounded {
        border-radius: 9999px !important;
        padding: 12px !important;
        box-shadow: none !important;

        > span.icon {
          margin: 0 !important;
          width: 1rem !important;
          height: 1rem !important;
        }
      }
    }
  }

  .control {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;

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

  .control:last-child {
    padding: 12px 0px 0px 0px;
  }
}
</style>
