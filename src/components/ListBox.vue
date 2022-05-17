<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, reactive, toRef, watch } from "vue";

const props = defineProps({
  name: { type: String, required: false, default: null },
  maxLength: { type: Number, required: false, default: 10 },
  isEnabled: { type: Boolean, required: false, default: true },
  isCollapsed: { type: Boolean, required: false, default: false },
});
const emit = defineEmits(["select", "fetch"]);
const isEnabledRef = toRef(props, "isEnabled");
const items = reactive([]);
const pageIndexRef = ref(0);
const nextResult = reactive([]);
const hasNextRef = ref(false);
const isFetchingRef = ref(false);
const selectionCountRef = ref(0);
const cachedItems = {};
const clear = (event) => {
  let index = 0;

  for (const item of items) {
    if (item.checked) {
      item.checked = false;
      selectionCountRef.value--;

      emit(
        "select",
        pageIndexRef.value * props.maxLength + index,
        items[index]
      );
    }

    index++;
  }

  for (const key in cachedItems) {
    if (cachedItems[key].checked) {
      cachedItems[key].checked = false;
      selectionCountRef.value--;

      emit("select", key, cachedItems[key]);
    }
  }
};
const select = (event, index) => {
  items[index].checked = !items[index].checked;

  if (items[index].checked) {
    selectionCountRef.value++;
  } else {
    selectionCountRef.value--;
  }

  emit("select", pageIndexRef.value * props.maxLength + index, items[index]);
};
const next = (event) => {
  pageIndexRef.value++;

  emit(
    "fetch",
    pageIndexRef.value * props.maxLength,
    props.maxLength + 1,
    nextResult,
    isFetchingRef
  );
};
const previous = (event) => {
  if (pageIndexRef.value > 0) {
    pageIndexRef.value--;
    items.splice(0);

    for (let i = 0; i < props.maxLength; i++) {
      items.push(cachedItems[pageIndexRef.value * props.maxLength + i]);
    }
  }
};

watch(isEnabledRef, async (newValue, oldValue) => {
  if (newValue !== oldValue && oldValue === false) {
    emit(
      "fetch",
      pageIndexRef.value * props.maxLength,
      props.maxLength + 1,
      nextResult,
      isFetchingRef
    );
  }
});
watch(
  nextResult,
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

      items.splice(0);

      for (let i = 0; i < length; i++) {
        if (
          result[i].index in cachedItems &&
          cachedItems[result[i].index].name === result[i].name
        ) {
          items.push(cachedItems[result[i].index]);
        } else {
          const item = { checked: false, name: result[i].name };

          items.push(item);
          cachedItems[result[i].index] = item;
        }
      }

      result.splice(0);
    }
  },
  { deep: true }
);
</script>

<template>
  <div class="panel-block">
    <nav class="level is-mobile">
      <div class="level-left" v-if="name !== null">
        <div class="level-item">
          <h3
            class="panel-heading is-uppercase has-text-weight-bold"
            v-text="name"
          ></h3>
        </div>
        <div class="level-item">
          <span
            class="badge has-text-weight-bold"
            v-text="selectionCountRef"
          ></span>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <button
            class="button is-rounded"
            v-bind:disabled="selectionCountRef === 0"
            @click="clear($event)"
          >
            <span class="icon is-small">
              <i class="fa-solid fa-arrow-rotate-left"></i>
            </span>
          </button>
        </div>
        <div class="level-item">
          <button
            class="button toggle is-rounded"
            @click="isCollapsed = !isCollapsed"
          >
            <span
              class="icon is-small"
              v-bind:class="{ collapsed: isCollapsed }"
            >
              <i class="fa-solid fa-chevron-up"></i>
            </span>
          </button>
        </div>
      </div>
    </nav>
    <transition name="fade" mode="out-in">
      <div
        class="control"
        v-if="!isCollapsed && isFetchingRef && items.length === 0"
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
        <label v-for="(item, index) in items" v-bind:key="item">
          <input
            type="checkbox"
            v-bind:disabled="!isEnabled"
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
      <div
        class="control"
        v-show="!isCollapsed && (pageIndexRef > 0 || hasNextRef)"
      >
        <nav class="level">
          <div class="level-left">
            <div class="level-item">
              <button
                class="button"
                v-bind:disabled="
                  !isEnabled || pageIndexRef === 0 || isFetchingRef
                "
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
                v-bind:disabled="!isEnabled || !hasNextRef || isFetchingRef"
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

    .badge {
      padding: 4px !important;
      border-radius: 290486px;
      width: 0.75rem !important;
      height: 0.75rem !important;
      background: var(--accent-color);
      color: #ffffff !important;
      font-size: 0.75rem;
      line-height: 100%;
      overflow: hidden;
      box-sizing: content-box;
      text-align: center;
    }

    > .level-right > .level-item {
      margin: 0px 0px 0px 12px;

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

      button.toggle {
        > span {
          transform: rotate(180deg);
        }

        > span.collapsed {
          transition: transform 0.5s ease;
          transform: rotate(0deg);
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
