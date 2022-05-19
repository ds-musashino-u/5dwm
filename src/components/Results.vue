<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, reactive, toRef, watch } from "vue";

const props = defineProps({
  isCollapsed: { type: Boolean, required: false, default: false },
  items: { type: Array, required: false, default: null },
  count: { type: Number, required: false, default: 0 },
  pageIndex: { type: Number, required: false, default: 0 },
  pageLength: { type: Number, required: false, default: 10 },
});
const emit = defineEmits(["select", "next", "previous"]);
const pageIndexRef = ref(0);
const nextResult = reactive([]);
const hasNextRef = ref(false);
const isFetchingRef = ref(false);
const cachedItems = {};
const select = (event, item) => {
  emit("select", item);
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
</script>

<template>
  <div class="panel-block">
    <nav class="level is-mobile">
      <div class="level-left">
        <div class="level-item">
          <h3
            class="panel-heading is-uppercase has-text-weight-bold"
            v-text="String(count) + ' Items'"
            v-if="count > 0 || count === 0"
          ></h3>
          <h3
            class="panel-heading is-uppercase has-text-weight-bold"
            v-text="String(count) + ' Item'"
            v-else
          ></h3>
        </div>
      </div>
      <div class="level-right">
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
      <div class="control" v-if="!isCollapsed && items === null" key="loading">
        <nav class="level">
          <div class="level-item">
            <span class="icon">
              <i class="fas fa-spinner updating"></i>
            </span>
          </div>
        </nav>
      </div>
      <div class="control" v-else-if="!isCollapsed" key="loaded">
        <transition-group name="gallery-list" class="gallery" tag="div" v-cloak>
          <article
            class="media gallery-list-item"
            v-for="(item, index) in items"
            v-bind:key="item"
          >
            <div class="media-content">
              <button
                class="button image is-64x64"
                type="button"
                @click="select($event, item)"
              >
                <picture
                  class="image"
                  v-if="item.media.type.startsWith('image')"
                >
                  <img v-bind:src="item.media.url" v-bind:alt="String(index)" />
                </picture>
                <span
                  class="icon is-small"
                  v-if="item.media.type.startsWith('image')"
                >
                  <i class="fa-solid fa-file-image"></i>
                </span>
                <span
                  class="icon is-small"
                  v-else-if="item.media.type.startsWith('video')"
                >
                  <i class="fa-solid fa-file-video"></i>
                </span>
                <span
                  class="icon is-small"
                  v-else-if="item.media.type.startsWith('audio')"
                >
                  <i class="fa-solid fa-file-audio"></i>
                </span>
                <span
                  class="icon is-small"
                  v-else-if="item.media.type.startsWith('text')"
                >
                  <i class="fa-solid fa-file-lines"></i>
                </span>
                <span class="icon is-small" v-else>
                  <i class="fa-solid fa-file"></i>
                </span>
              </button>
            </div>
          </article>
        </transition-group>
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
                  pageIndexRef === 0 || isFetchingRef
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
      button.is-rounded {
        border-radius: 9999px !important;
        padding: 12px !important;
        box-shadow: none !important;

        > span {
          transform: rotate(180deg);
        }

        > span.icon {
          margin: 0 !important;
          width: 1rem !important;
          height: 1rem !important;
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
    width: 400px;

    .level {
      padding: 0.5em 0.75em;
      width: 100%;
    }

    .gallery {
      display: flex;
      margin: -2px -2px -2px -2px;
      flex-direction: row;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      width: calc(100% + 4px);

      .media {
        display: inline-block;
        margin: 2px 2px 2px 2px;
        border: 0px none transparent !important;
        padding: 0;
        width: calc(25% - 4px);

        .media-content {
          width: 100%;

          button {
            z-index: 1;
            position: relative;
            margin: 0 !important;
            padding: 0 !important;
            width: 100%;
            aspect-ratio: 1 / 1;
            border-radius: 8px;
            box-shadow: none !important;
            overflow: hidden;
            background: transparent !important;

            picture {
              margin: 0;
              padding: 0;
              width: 100%;
              height: 100%;

              img {
                object-fit: cover;
                width: 100%;
                height: 100%;
              }
            }

            .icon {
              position: absolute;
              top: 50%;
              left: 50%;
              margin: 0 !important;
              width: 1rem !important;
              height: 1rem !important;
              transform: translate(-50%, -50%);
            }
          }
        }

        figure {
          margin: 0;
          padding: 0;

          .image {
            overflow: hidden;

            img {
              object-fit: cover;
              width: 100%;
              height: 100%;
            }
          }
        }
      }
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
