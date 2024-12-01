<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, reactive, toRef, watch } from "vue";

const props = defineProps({
  isCollapsed: { type: Boolean, required: false, default: false },
  isExpandable: { type: Boolean, required: false, default: false },
  item: { type: Object, required: false, default: null },
  canBack: { type: Boolean, required: false, default: true },
  color: { type: String, required: false, default: window.getComputedStyle(document.documentElement).getPropertyValue("--accent-color") },
  error: { type: Object, required: false, default: null }
});
const emit = defineEmits(["load", "unload", "back", "colorChanged"]);
const inputColorRef = ref(props.color);
const selectedColorRef = ref(props.color);

const load = (event, item) => {
  emit("load", item);
};
const unload = (event, item) => {
  emit("unload", item);
};
const back = (event) => {
  emit("back");
};
const resetColor = (event) => {
  selectedColorRef.value = inputColorRef.value = window.getComputedStyle(document.documentElement).getPropertyValue("--accent-color");

  emit("colorChanged", props.item, selectedColorRef.value);
};
const colorChanged = (event) => {
  if (/^#(?:[0-9a-f]{3}){1,2}$/i.test(inputColorRef.value)) {
    selectedColorRef.value = inputColorRef.value;

    emit("colorChanged", props.item, selectedColorRef.value);
  }
};
</script>

<template>
  <div class="panel-block">
    <div class="top">
      <div class="panel">
        <div class="panel-block">
          <nav class="level is-mobile">
            <div class="level-left">
              <div class="level-item">
                <button class="button is-rounded is-primary" v-bind:disabled="!canBack" @click="back($event)">
                  <span class="icon is-small">
                    <i class="fa-solid fa-arrow-left"></i>
                  </span>
                </button>
              </div>
            </div>
          </nav>
        </div>
      </div>
    </div>
    <div class="wrap">
      <div class="panel">
        <div class="panel-block">
          <nav class="level is-mobile">
            <div class="level-left">
              <div class="level-item">
                <span class="icon is-small" v-if="'data' in item.media && item.media.data !== null">
                  <i class="fa-solid fa-table"></i>
                </span>
                <span class="icon is-small" v-else-if="item.media.type.startsWith('image')">
                  <i class="fa-solid fa-file-image"></i>
                </span>
                <span class="icon is-small" v-else-if="item.media.type.startsWith('video')">
                  <i class="fa-solid fa-file-video"></i>
                </span>
                <span class="icon is-small" v-else-if="item.media.type.startsWith('audio')">
                  <i class="fa-solid fa-file-audio"></i>
                </span>
                <span class="icon is-small" v-else-if="item.media.type.startsWith('text')">
                  <i class="fa-solid fa-file-lines"></i>
                </span>
                <span class="icon is-small" v-else>
                  <i class="fa-solid fa-file"></i>
                </span>
              </div>
              <div class="level-item" v-if="'index' in item && item.index !== null">
                <span class="icon is-small">
                  <span class="is-size-7 is-uppercase has-text-weight-bold">{{ item.index + 1 }}</span>
                </span>
              </div>
              <div class="level-item" v-if="item.media.type.startsWith('kml') || item.media.type.startsWith('kmz') || 'data' in item.media && item.media.data !== null">
                <span class="icon is-small has-text-dark">
                  <i class="fa-solid fa-chart-simple"></i>
                </span>
                <transition name="fade" mode="out-in">
                  <div class="control" v-if="'data' in item.media && item.media.data !== null && item.media.data.length === 0" key="loading">
                    <span class="icon">
                      <i class="fas fa-spinner updating"></i>
                    </span>
                  </div>
                  <div class="control" v-else key ="loaded">
                    <div class="tabs is-toggle">
                      <ul :style="{ pointerEvents: item.loading ? 'none' : 'auto' }">
                        <li :class="{ 'is-active': !item.loaded }" >
                          <a @click="item.loaded ? unload($event, item) : load($event, item)">
                            <span class="is-size-7 is-uppercase has-text-weight-bold">Off</span>
                          </a>
                        </li>
                        <li :class="{ 'is-active': item.loaded }">
                          <a @click="item.loaded ? unload($event, item) : load($event, item)">
                            <span class="is-size-7 is-uppercase has-text-weight-bold">On</span>
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>
                </transition>
              </div>
              <div class="level-item" v-if="'data' in item.media && item.media.data !== null">
                <button class="button is-flat" type="button" v-bind:disabled="item.media.data.length === 0" @click="resetColor($event)">
                  <span class="icon is-small has-text-dark">
                    <i class="fa-solid fa-palette"></i>
                  </span>
                </button>
              </div>
              <div class="level-item" v-if="'data' in item.media && item.media.data !== null">
                <input class="input is-outlined is-size-7 has-text-weight-bold" type="color" v-bind:disabled="item.media.data.length === 0" v-model="inputColorRef"
                    @input="colorChanged($event, item)" />
              </div>
              
            </div>
            <div class="level-right">
              <div class="level-item">
                <a class="button is-rounded" target="_blank" v-bind:href="item.media.url"><span class="icon is-small"><i
                      class="fa-solid fa-link"></i></span></a>
              </div>
              <div class="level-item" v-if="isExpandable">
                <button class="button toggle is-rounded" @click="isCollapsed = !isCollapsed">
                  <span class="icon is-small" v-bind:class="{ collapsed: isCollapsed }">
                    <i class="fa-solid fa-chevron-up"></i>
                  </span>
                </button>
              </div>
            </div>
          </nav>
          <transition name="fade" mode="out-in">
            <div class="level is-mobile has-background-danger" v-if="props.error !== null">
              <div class="level-left">
                <div class="level-item">
                  <span class="icon is-small has-text-white">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                  </span>
                </div>
                <div class="level-item" v-if="'url' in props.error && props.error.url !== null">
                  <a :href="props.error.url" target="_blank" class="is-size-7 is-uppercase is-underlined has-text-weight-bold has-text-white" :title="props.error.message">{{ props.error.message }}</a>
                </div>
                <div class="level-item" v-else>
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-white">{{ props.error.message }}</span>
                </div>
              </div>
            </div>
          </transition>
          <transition name="fade" mode="out-in">
            <div class="control" v-if="!isCollapsed &&
              item.media.type.startsWith('image') &&
              item.media.url.startsWith('https://')
              " key="collapse">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <picture class="image">
                        <img v-bind:src="'thumbnailUrl' in item.media && item.media.thumbnailUrl !== null ? item.media.thumbnailUrl : item.media.url" v-bind:alt="item.media.id" />
                      </picture>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
          </transition>
          <transition name="fade" mode="out-in">
            <div class="control" v-if="!isCollapsed &&
              item.media.type.startsWith('video') &&
              item.media.url.startsWith('https://')
              " key="collapse">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <video controls :src="item.media.url"></video>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
          </transition>
          <transition name="fade" mode="out-in">
            <div class="control" v-if="!isCollapsed &&
              item.media.type.startsWith('audio') &&
              item.media.url.startsWith('https://')
              " key="collapse">
              <nav class="level">
                <div class="level-item">
                  <article class="media">
                    <div class="media-content">
                      <audio controls :src="item.media.url"></audio>
                    </div>
                  </article>
                </div>
              </nav>
            </div>
          </transition>
        </div>
        <div class="panel-block">
          <div class="level">
            <div class="level-left">
              <div class="level-item">
                <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">ID</span>
              </div>
            </div>
            <div class="level-right">
              <div class="level-item">
                <span class="is-size-7 has-text-weight-bold" v-text="item.media.id"></span>
              </div>
            </div>
          </div>
        </div>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && item.hasScore" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Score</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.score"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && item.media.location !== null" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Longitude</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="String(item.media.location.longitude)"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && item.media.location !== null" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Latitude</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="String(item.media.location.latitude)"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed &&
            item.media.location !== null &&
            item.media.location.hasAddress
            " key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Address</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <p class="is-size-7 has-text-weight-bold has-text-right" v-text="item.media.location.address"></p>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Time</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.createdAt.toLocaleString()"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && item.media.collection !== null" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Collection</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.collection"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed && item.media.categories.length > 0" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Categories</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item" v-for="category in item.media.categories" v-bind:key="category">
                  <span class="is-size-7 has-text-weight-bold" v-text="category"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Type</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.type"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed" key="collapse">
            <div class="level">
              <div class="level-left">
                <div class="level-item">
                  <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">User</span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="is-size-7 has-text-weight-bold" v-text="item.media.username"></span>
                </div>
              </div>
            </div>
          </div>
        </transition>
        <transition name="fade" mode="out-in">
          <div class="panel-block" v-if="!isCollapsed &&
            item.media.description !== null &&
            item.media.description.length > 0
            " key="collapse">
            <div class="content">
              <span class="is-size-7 is-uppercase has-text-weight-bold has-text-grey">Description</span>
              <p class="is-size-7 has-text-weight-bold" v-text="item.media.description"></p>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.panel-block {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 0;
  width: fit-content;
  height: 100%;
  max-height: 100%;

  .wrap {
    flex-basis: auto;
    width: fit-content;
    height: 100%;
    max-height: 100%;
    overflow-x: hidden;
    overflow-y: auto;

    .panel {
      border-radius: 0;
      width: fit-content;
      box-shadow: none !important;

      >.panel-block:nth-of-type(1)>nav.level:first-child {
        background: hsl(0, 0%, 96%);
      }

      >.panel-block {
        width: 320px;
        height: fit-content;

        .level>.level-right>.level-item .button {
          background: transparent !important;
        }

        input[type="color"] {
          appearance: none;
          margin: 0 !important;
          border: 2px solid var(--accent-color) !important;
          border-radius: 290486px !important;
          padding: 0;
          width: 1.0rem !important;
          aspect-ratio: 1;
          box-shadow: none;
          overflow: hidden;
          block-size: auto;
        }

        input[type="color"]::-webkit-color-swatch-wrapper {
          padding: 0;
        }

        input[type="color"]::-webkit-color-swatch {
          border: none;
        }
      }
    }
  }

  .top {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    border-bottom: 1px solid hsl(0deg, 0%, 93%);

    .panel {
      border-radius: 0;
      width: fit-content;
      box-shadow: none !important;

      >.panel-block:nth-of-type(1)>nav.level:first-child {
        background: hsl(0, 0%, 96%);
      }
    }

    .panel-block {
      border-radius: 0;
      width: 320px;
      box-shadow: none !important;

      >.level {
        padding: 0.5em 0.75em;
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

  .panel-block:not(:first-child)>.level {
    padding: 0.5em 0.75em;
  }

  .panel-block {
    flex-direction: column;
    align-items: flex-start;
    padding: 0;

    .level {
      margin: 0;
      padding: 0em 0.75em;
      width: 100%;
      flex-direction: row;

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

      >.level-left>.level-item> {
        button.is-flat {
          width: fit-content !important;
          height: fit-content !important;
          padding: 0px !important;
          box-shadow: none !important;
          line-height: 1.0rem !important;
          background: transparent !important;

          >span.icon {
            margin: 0 !important;
            width: 1.0rem !important;
            height: 1.0rem !important;
            font-size: 1.0rem !important;
            line-height: 1.0rem !important;
          }
        }

        .control {
          width: fit-content;

          >.tabs.is-toggle {
            ul {
              margin: 0;

              >li>a {
                padding: 0.25em 0.5em;
                transition: 0.5s;
              }

              >li:not(.is-active)>a {
                background: #ffffff;
              }
            }
          }
        }

        span.icon+.control {
          margin-left: 0.75rem;
        }

        button.toggle {
          width: fit-content !important;
          height: fit-content !important;
          padding: 8px !important;
          box-shadow: none !important;
          line-height: 1.5rem !important;
          background: transparent !important;

          >span.icon {
            margin: 0 !important;
            width: 1.5rem !important;
            height: 1.5rem !important;
            font-size: 1.5rem !important;
            line-height: 1.5rem !important;
          }
        }
      }

      >.level-right {
        margin: 0;

        >.level-item {
          .button.is-rounded {
            border-radius: 9999px !important;
            padding: 12px !important;
            box-shadow: none !important;

            >span.icon {
              margin: 0 !important;
              width: 1rem !important;
              height: 1rem !important;
            }
          }

          .button.toggle {
            >span {
              transform: rotate(180deg);
            }

            >span.collapsed {
              transition: transform 0.5s ease;
              transform: rotate(0deg);
            }
          }

          .control {
            justify-content: flex-end;

            >input {
              width: auto;
            }

            >span+input {
              margin: 0px 0px 0px 4px;
            }
          }
        }
      }
    }

    :not(nav).level {
      align-items: flex-start;

      >.level-left {
        margin: 0;
        flex-direction: column;
        align-items: flex-start;

        .level-item:not(:last-child) {
          margin: 0px 0px 0.5em 0px;
        }
      }

      >.level-right {
        margin: 0;
        width: 50%;
        flex-direction: column;

        >.level-item {
          width: 100%;
          justify-content: flex-end;
        }

        .level-item:not(:last-child) {
          margin: 0px 0px 0.5em 0px;
        }
      }
    }

    .level.has-background-danger>.level-left {
      flex-direction: row;
      padding: 0.5em 0em;

      >.level-item:not(:last-child) {
        margin: 0px 0.5em 0px 0px;
      }

      a,
      a:focus,
      a:link,
      a:visited,
      a:active {
        color: #ffffff !important;
        transition: .5s;
      }

      a:hover {
        opacity: 0.5;
        color: #ffffff !important;
        transition: .5s;
      }
    }

    .control {
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      align-items: center;
      padding: 0 !important;
      width: 320px;

      .level {
        padding: 0;
        width: 100%;

        >.level-item>.media {
          display: inline-block;
          margin: 0;
          border: 0px none transparent !important;
          padding: 0;
          width: 100%;

          .media-content {
            display: flex;
            width: 100%;

            picture {
              margin: 0;
              padding: 0;
              width: 100%;
              height: 100%;

              img {
                object-fit: contain;
                width: 320px;
              }
            }

            video, audio {
              margin: 0;
              padding: 0;
              width: 100%;
            }
          }
        }
      }
    }

    .control:last-child {
      padding: 12px 0px 0px 0px;
    }

    .content {
      margin: 0;
      padding: 0.5em 0.75em;
      width: 100%;

      span+p,
      p {
        margin: 0.5em 0px 0px 0px;
        overflow-wrap: break-word;
      }
    }
  }

  .panel-block:not(:last-child) {
    border-bottom: 1px solid hsl(0deg, 0%, 93%);
  }
}
</style>
