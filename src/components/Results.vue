<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref } from "vue";

const props = defineProps({
  isCollapsed: { type: Boolean, required: false, default: false },
  isFetching: { type: Boolean, required: false, default: false },
  items: { type: Array, required: false, default: null },
  count: { type: Number, required: false, default: 0 },
  pageIndex: { type: Number, required: false, default: 0 },
  pageLength: { type: Number, required: false, default: 10 },
});
const emit = defineEmits(["select", "next", "previous", "load", "unload"]);
const isForwardingRef = ref(true);
const select = (event, item) => {
  emit("select", item);
};
const next = (event) => {
  isForwardingRef.value = true;

  emit("next", props.pageIndex + 1);
};
const previous = (event) => {
  isForwardingRef.value = false;

  emit("previous", props.pageIndex - 1);
};
const load = (event, item) => {
  emit("load", item);
};
const unload = (event, item) => {
  emit("unload", item);
};

</script>

<template>
  <div class="panel-block">
    <nav class="level is-mobile">
      <div class="level-left">
        <div class="level-item">
          <h3
            class="panel-heading is-uppercase is-size-7 has-text-weight-bold"
            v-text="String(count) + ' Items'"
            v-if="count > 0 || count === 0"
          ></h3>
          <h3
            class="panel-heading is-uppercase is-size-7 has-text-weight-bold"
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
            v-bind:key="index"
          >
            <div class="media-content">
              <div class="stack">
                <button
                  class="button image is-64x64"
                  type="button"
                  @click="select($event, item)"
                >
                  <picture
                    class="image"
                    v-if="
                      item.media.type.startsWith('image') &&
                      item.media.url.startsWith('https://')
                    "
                  >
                    <img
                      v-bind:src="item.media.url"
                      v-bind:alt="String(index)"
                    />
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
                <button class="button toggle" type="button" v-bind:disabled="item.loading" v-if="item.media.type.startsWith('kml') || item.media.type.startsWith('kmz')" @click="item.loaded ? unload($event, item) : load($event, item)">
                  <transition name="fade" mode="out-in">
                    <span class="icon" v-if="item.loaded" key="on">
                      <i class="fa-solid fa-toggle-on"></i>
                    </span>
                    <span class="icon" v-else key="off">
                      <i class="fa-solid fa-toggle-off"></i>
                    </span>
                  </transition>
                </button>
              </div>
            </div>
          </article>
        </transition-group>
      </div>
    </transition>
    <transition name="fade">
      <div class="control" v-show="!isCollapsed && count > pageLength">
        <nav class="level">
          <div class="level-left">
            <div class="level-item">
              <button
                class="button is-primary"
                v-bind:disabled="pageIndex === 0 || isFetching"
                @click="previous($event)"
              >
                <transition name="fade" mode="out-in">
                  <span
                    class="icon is-small"
                    v-if="!isForwardingRef && isFetching"
                    key="fetching"
                  >
                    <i class="fas fa-spinner updating"></i>
                  </span>
                  <span class="icon is-small" v-else key="fetched">
                    <i class="fa-solid fa-chevron-left"></i>
                  </span>
                </transition>
              </button>
            </div>
          </div>
          <div class="level-item">
            <span class="is-size-6 has-text-weight-bold"
              >{{ pageIndex + 1 }}/{{ ~~Math.ceil(count / pageLength) }}</span
            >
          </div>
          <div class="level-right">
            <div class="level-item">
              <button
                class="button is-primary"
                v-bind:disabled="
                  pageIndex + 1 === ~~Math.ceil(count / pageLength) ||
                  isFetching
                "
                @click="next($event)"
              >
                <transition name="fade" mode="out-in">
                  <span
                    class="icon is-small"
                    v-if="isForwardingRef && isFetching"
                    key="fetching"
                  >
                    <i class="fas fa-spinner updating"></i>
                  </span>
                  <span class="icon is-small" v-else key="fetched">
                    <i class="fa-solid fa-chevron-right"></i>
                  </span>
                </transition>
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

    .button.is-primary {
      border-radius: 8px;
      box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
        0 0px 0 1px rgb(10 10 10 / 2%) !important;
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
          border-radius: 8px;
          width: 100%;
          background: #ffffff;
          overflow: hidden;

          .stack {
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1;

            button:not(.toggle) {
              z-index: 1;
              position: absolute;
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

            button.toggle {
              position: absolute;
              z-index: 1;
              bottom: 0;
              left: 50%;
              width: fit-content !important;
              height: fit-content !important;
              padding: 8px !important;
              box-shadow: none !important;
              line-height: 1.5rem !important;
              background: transparent !important;
              transform: translate3d(-50%, 0, 0);
              
              > span.icon {
                margin: 0 !important;
                width: 1.5rem !important;
                height: 1.5rem !important;
                font-size: 1.5rem !important;
                line-height: 1.5rem !important;
              }
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
  }

  .control:last-child {
    padding: 0;
  }
}
</style>
