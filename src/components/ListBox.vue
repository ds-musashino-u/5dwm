<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, toRef, watch } from "vue";

const props = defineProps({
  name: { type: String, required: false, default: null },
  isEnabled: { type: Boolean, required: false, default: true },
  isBadgeVisible: { type: Boolean, required: false, default: true },
  isCollapsable: { type: Boolean, required: false, default: true },
  isCollapsed: { type: Boolean, required: false, default: false },
  isContinuous: { type: Boolean, required: false, default: false },
  items: { type: Array, required: false, default: [] },
  pageIndex: { type: Number, required: false, default: 0 },
  pageLength: { type: Number, required: false, default: 10 }
});
const emit = defineEmits(["collapse", "clear", "select", "next", "previous"]);
const isEnabledRef = toRef(props, "isEnabled");
const pageIndexRef = toRef(props, "pageIndex");
const isFetchingRef = ref(false);
const clear = (event) => {
  emit("clear");
};
const collapse = (event) => {
  emit("collapse");
}
const select = (event, index) => {
  emit("select", pageIndexRef.value * props.pageLength + index);
};
const next = (event) => {
  emit("next", pageIndexRef.value + 1, props.pageLength + 1, isFetchingRef);
};
const previous = (event) => {
  emit("previous", pageIndexRef.value - 1);
};

watch(isEnabledRef, (newValue, oldValue) => {
  if (newValue !== oldValue && oldValue === false) {
    emit("next", pageIndexRef.value, props.pageLength + 1, isFetchingRef);
  }
});
</script>

<template>
  <div class="panel-block">
    <nav class="level is-mobile">
      <div class="level-left" v-if="name !== null">
        <div class="level-item">
          <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold" v-text="name"></h3>
        </div>
        <transition name="fade">
          <div class="level-item" v-if="isBadgeVisible">
            <span class="badge has-text-weight-bold" v-text="items.reduce((x, y) => y.checked ? x + 1 : x, 0)"></span>
          </div>
        </transition>
      </div>
      <div class="level-right">
        <div class="level-item">
          <button class="button is-rounded" v-bind:disabled="items.reduce((x, y) => y.checked ? x + 1 : x, 0) === 0"
            @click="clear($event)">
            <span class="icon is-small">
              <i class="fa-solid fa-arrow-rotate-left"></i>
            </span>
          </button>
        </div>
        <div class="level-item" v-if="isCollapsable">
          <button class="button toggle is-rounded" @click="collapse">
            <span class="icon is-small" v-bind:class="{ collapsed: isCollapsed }">
              <i class="fa-solid fa-chevron-up"></i>
            </span>
          </button>
        </div>
      </div>
    </nav>
    <transition name="fade" mode="out-in">
      <div class="control" v-if="!isCollapsed && isFetchingRef && items.length === 0" key="loading">
        <nav class="level">
          <div class="level-item">
            <span class="icon">
              <i class="fas fa-spinner updating"></i>
            </span>
          </div>
        </nav>
      </div>
      <div class="control" v-else-if="!isCollapsed" key="default">
        <label v-for="(item, index) in [...Array(pageLength).keys()].map(
          (x) => pageIndex * pageLength + x < items.length ? items[pageIndex * pageLength + x] : null
        ).filter(x => x !== null)" v-bind:key="item">
          <input type="checkbox" v-bind:disabled="!isEnabled" @change="select($event, index)"
            v-bind:checked="item.checked" />
          <span class="custom"></span>
          <span class="is-size-7 has-text-weight-bold" v-text="item.name"></span>
        </label>
      </div>
    </transition>
    <transition name="fade">
      <div class="control" v-show="!isCollapsed && (pageIndexRef > 0 || isContinuous)">
        <nav class="level is-mobile">
          <div class="level-left">
            <div class="level-item">
              <button class="button is-primary" v-bind:disabled="
                !isEnabled || pageIndexRef === 0 || isFetchingRef
              " @click="previous($event)">
                <span class="icon is-small">
                  <i class="fa-solid fa-chevron-left"></i>
                </span>
              </button>
            </div>
          </div>
          <div class="level-right">
            <div class="level-item">
              <button class="button is-primary" v-bind:disabled="!isEnabled || !isContinuous || isFetchingRef" @click="next($event)">
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
  padding: 0.5em 0em;

  .level {
    margin: 0;
    padding: 0em 0.75em;
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

    >.level-right>.level-item {
      margin: 0px 0px 0px 12px;

      button {
        background: transparent !important;
      }

      button.is-rounded {
        border-radius: 9999px !important;
        padding: 12px !important;
        box-shadow: none !important;

        >span.icon {
          margin: 0 !important;
          width: 1rem !important;
          height: 1rem !important;
        }
      }

      button.toggle {
        >span {
          transform: rotate(180deg);
        }

        >span.collapsed {
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
      padding: 0.25em 0.75em;
      width: 100%;
      background-color: transparent;
      transition: background-color 0.5s;
    }

    label:hover {
      background-color: hsla(0, 0%, 93%, 0.75);
    }

    label>span {
      user-select: none;
    }

    label>span:not(:first-of-type) {
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

    label input[type="checkbox"]+.custom:before,
    label input[type="radio"]+.custom:before {
      font-weight: 900;
      font-family: "Font Awesome 6 Free";
      content: "\f00c";
      color: transparent;
      text-shadow: none;
      transition: 0.5s;
    }

    label input[type="checkbox"]:checked+.custom:before,
    label input[type="radio"]:checked+.custom:before {
      color: var(--accent-color);
      transition: 0.5s;
    }
  }

  .control:last-child {
    padding: 0;
  }
}
</style>
