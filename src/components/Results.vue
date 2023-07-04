<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref } from "vue";

const props = defineProps({
  isCollapsable: { type: Boolean, required: false, default: false },
  isCollapsed: { type: Boolean, required: false, default: false },
  isFetching: { type: Boolean, required: false, default: false },
  items: { type: Array, required: false, default: null },
  count: { type: Number, required: false, default: 0 },
  pageIndex: { type: Number, required: false, default: 0 },
  pageLength: { type: Number, required: false, default: 10 },
  canBack: { type: Boolean, required: false, default: true },
  appearance: { type: Object, required: false, default: {} }
});
const emit = defineEmits(["select", "next", "previous", "load", "unload", "back"]);
const isForwardingRef = ref(true);
const select = (event, index, item) => {
  emit("select", index, item);
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
const back = (event) => {
  emit("back");
};
</script>

<template>
  <div class="panel-block">
    <div class="top">
      <nav class="panel">
        <div class="panel-block">
          <nav class="level is-mobile">
            <div class="level-left">
              <div class="level-item">
                <button class="button is-rounded" v-bind:disabled="!canBack" @click="back($event)">
                  <span class="icon is-small">
                    <i class="fa-solid fa-arrow-left"></i>
                  </span>
                </button>
              </div>
            </div>
          </nav>
        </div>
        <div class="panel-block">
          <nav class="level is-mobile">
            <div class="level-left">
              <div class="level-item">
                <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold" v-text="String(0) + ' Items'"
                  v-if="count === null"></h3>
                <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold" v-text="String(count) + ' Items'"
                  v-else-if="count > 0 || count === 0"></h3>
                <h3 class="panel-heading is-uppercase is-size-7 has-text-weight-bold" v-text="String(count) + ' Item'"
                  v-else></h3>
              </div>
            </div>
            <div class="level-right" :class="{ 'is-invisible': !isCollapsable }">
              <div class="level-item">
                <button class="button toggle is-rounded" @click="collapse">
                  <span class="icon is-small" v-bind:class="{ collapsed: isCollapsed }">
                    <i class="fa-solid fa-chevron-up"></i>
                  </span>
                </button>
              </div>
            </div>
          </nav>
        </div>
      </nav>
    </div>
    <div class="wrap">
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
            <article class="media gallery-list-item" v-for="(item, index) in items" v-bind:key="index">
              <div class="media-content">
                <div class="stack">
                  <button class="button image is-64x64" type="button"
                    @click="select($event, pageIndex * pageLength + index, item)">
                    <picture class="image" v-if="item.media.type.startsWith('image') &&
                      item.media.url.startsWith('https://')
                      ">
                      <img v-bind:src="item.media.url" v-bind:alt="String(index)" />
                    </picture>
                    <span class="icon" v-if="'data' in item.media && item.media.data !== null">
                      <i class="fa-solid fa-table fa-lg"></i>
                    </span>
                    <span class="icon" v-else-if="item.media.type.startsWith('image')">
                      <i class="fa-solid fa-file-image fa-lg"></i>
                    </span>
                    <span class="icon" v-else-if="item.media.type.startsWith('video')">
                      <i class="fa-solid fa-file-video fa-lg"></i>
                    </span>
                    <span class="icon" v-else-if="item.media.type.startsWith('audio')">
                      <i class="fa-solid fa-file-audio fa-lg"></i>
                    </span>
                    <span class="icon" v-else-if="item.media.type.startsWith('text')">
                      <i class="fa-solid fa-file-lines fa-lg"></i>
                    </span>
                    <span class="icon" v-else>
                      <i class="fa-solid fa-file fa-lg"></i>
                    </span>
                  </button>
                  <div class="heading" :style="{ backgroundColor: appearance[item.media.id] }" v-if="item.media.id in appearance">
                    <span class="badge is-size-7 has-text-weight-bold">{{ pageIndex * pageLength + index + 1 }}</span>
                    <button class="button toggle is-hidden" type="button" v-bind:disabled="item.loading"
                      v-if="item.media.type.startsWith('kml') || item.media.type.startsWith('kmz') || 'data' in item.media && item.media.data !== null"
                      @click="item.loaded ? unload($event, item) : load($event, item)">
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
                  <div class="heading" v-else>
                    <span class="badge is-size-7 has-text-weight-bold">{{ pageIndex * pageLength + index + 1 }}</span>
                    <button class="button toggle is-hidden" type="button" v-bind:disabled="item.loading"
                      v-if="item.media.type.startsWith('kml') || item.media.type.startsWith('kmz') || 'data' in item.media && item.media.data !== null"
                      @click="item.loaded ? unload($event, item) : load($event, item)">
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
              </div>
            </article>
          </transition-group>
        </div>
      </transition>
    </div>
    <div class="bottom">
      <transition name="fade">
        <div class="control" v-show="!isCollapsed && count > pageLength">
          <nav class="level is-mobile">
            <div class="level-left">
              <div class="level-item">
                <button class="button is-primary" v-bind:disabled="pageIndex === 0 || isFetching"
                  @click="previous($event)">
                  <transition name="fade" mode="out-in">
                    <span class="icon is-small" v-if="!isForwardingRef && isFetching" key="fetching">
                      <i class="fas fa-spinner updating"></i>
                    </span>
                    <span class="icon is-small" v-else key="fetched">
                      <i class="fa-solid fa-chevron-left"></i>
                    </span>
                  </transition>
                </button>
              </div>
            </div>
            <transition name="fade">
              <div class="level-item" v-if="~~Math.ceil(count / pageLength) > 0">
                <span class="is-size-7 has-text-weight-bold">{{ pageIndex + 1 }}/{{ ~~Math.ceil(count / pageLength)
                }}</span>
              </div>
            </transition>
            <div class="level-right">
              <div class="level-item">
                <button class="button is-primary"
                  v-bind:disabled="count === 0 || pageIndex + 1 === ~~Math.ceil(count / pageLength) || isFetching"
                  @click="next($event)">
                  <transition name="fade" mode="out-in">
                    <span class="icon is-small" v-if="isForwardingRef && isFetching" key="fetching">
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
  </div>
</template>

<style lang="scss" scoped>
.panel-block {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-end;
  padding: 0;
  width: 100%;
  height: 100%;
  max-height: 100%;

  .level {
    margin: 0;
    padding: 0em 0.75em;
    width: 100%;
    flex-shrink: 0;
    height: fit-content;

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
      border-radius: 4px;
      box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
        0 0px 0 1px rgb(10 10 10 / 2%) !important;
    }

    >.level-right>.level-item {
      button.is-rounded {
        border-radius: 9999px !important;
        padding: 12px !important;
        box-shadow: none !important;

        >span {
          transform: rotate(180deg);
        }

        >span.icon {
          margin: 0 !important;
          width: 1rem !important;
          height: 1rem !important;
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
    padding: 0em 0.75em;
    width: 400px;
    height: fit-content;

    .level {
      padding: 0.5em 0.75em;
      width: 100%;
    }

    .gallery {
      display: flex;
      flex-shrink: 0;
      margin: -2px -2px -2px -2px;
      flex-direction: row;
      flex-wrap: wrap;
      justify-content: start;
      align-items: flex-start;
      width: calc(100% + 4px);

      .media {
        display: inline-block;
        margin: 2px 2px 2px 2px;
        border: 0px none transparent !important;
        padding: 0;
        width: calc(25% - 4px);

        .media-content {
          border-radius: 0px;
          width: 100%;
          background: hsl(0deg, 0%, 93%);
          overflow: hidden;

          .stack {
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1;

            button:not(.toggle) {
              z-index: 1;
              margin: 0 !important;
              padding: 0 !important;
              width: 100%;
              aspect-ratio: 1 / 1;
              border-radius: 0px;
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

              .badge {
                position: absolute;
                top: 0%;
                left: 0%;
                margin: 0 !important;
                border-radius: 0px 0px 0px 0px;
                padding: 8px 12px 8px 12px;
                background: var(--accent-color);
                color: #ffffff;
              }
            }

            .heading {
              z-index: 1;
              position: absolute;
              display: flex;
              flex-direction: row;
              justify-content: flex-start;
              align-items: center;
              top: 0%;
              left: 0%;
              margin: 0;
              padding: 0;
              background: var(--accent-color);

              .badge {
                position: relative !important;
                margin: 0 !important;
                border-radius: 0px 0px 0px 0px;
                padding: 4px 8px 4px 8px;
                color: #ffffff;
              }
            }

            button.toggle {
              position: relative;
              z-index: 1;
              top: 0%;
              left: 0%;
              margin: 0 !important;
              padding: 2px 8px 2px 8px !important;
              width: fit-content !important;
              height: fit-content !important;
              box-shadow: none !important;
              line-height: 1.5rem !important;
              background: transparent !important;

              >span.icon {
                margin: 0 !important;
                width: 1.5rem !important;
                height: 1.5rem !important;
                font-size: 1.5rem !important;
                line-height: 1.5rem !important;

                >i {
                  color: #ffffff !important;
                }
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

  .control:last-child:not(:first-child) {
    flex-shrink: 0;
    border-top: 1px solid hsl(0deg, 0%, 93%);
  }

  .wrap {
    flex-basis: auto;
    width: fit-content;
    height: 100%;
    max-height: 100%;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .top {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;

    .panel {
      border-radius: 0;
      width: fit-content;
      box-shadow: none !important;

      >.panel-block {
        height: fit-content;
      }

      >.panel-block:not(:last-child) {
        border-bottom: 1px solid hsl(0deg, 0%, 93%);
        width: 400px;

        >.level {
          padding: 0.5em 0.75em;
        }
      }
    }
  }

  .bottom {
    border-top: 1px solid hsl(0deg, 0%, 93%);

    .control {
      padding: 0;

      >.level {
        padding: 0.5em 0.75em;
      }
    }
  }

  .top,
  .bottom {
    flex-shrink: 0;
    width: fit-content;
    height: fit-content;
    min-height: fit-content;
    overflow-x: hidden;
    overflow-y: hidden;
    box-sizing: border-box;

    button {
      border-radius: 4px;
      box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
        0 0px 0 1px rgb(10 10 10 / 2%) !important;
    }
  }
}</style>
