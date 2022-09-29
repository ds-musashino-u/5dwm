<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, reactive, toRef, watch } from "vue";

const props = defineProps({
  isCollapsed: { type: Boolean, required: false, default: false },
  item: { type: Object, required: false, default: null },
});
const emit = defineEmits(["load", "unload"]);

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
        </div>
        <div class="level-item">
          <button
            class="button toggle"
            type="button"
            v-bind:disabled="item.loading"
            v-if="item.media.type.startsWith('kml') || item.media.type.startsWith('kmz')"
            @click="item.loaded ? unload($event, item) : load($event, item)"
          >
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
      <div class="level-right">
        <div class="level-item">
          <a
            class="button is-rounded"
            target="_blank"
            v-bind:href="item.media.url"
            ><span class="icon is-small"><i class="fa-solid fa-link"></i></span
          ></a>
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
        v-if="
          !isCollapsed &&
          item.media.type.startsWith('image') &&
          item.media.url.startsWith('https://')
        "
        key="collapse"
      >
        <nav class="level">
          <div class="level-item">
            <article class="media">
              <div class="media-content">
                <picture class="image">
                  <img v-bind:src="item.media.url" v-bind:alt="item.media.id" />
                </picture>
              </div>
            </article>
          </div>
        </nav>
      </div>
    </transition>
  </div>
  <transition name="fade" mode="out-in">
    <div
      class="panel-block"
      v-if="!isCollapsed && item.hasScore"
      key="collapse"
    >
      <div class="level">
        <div class="level-left">
          <div class="level-item">
            <span
              class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
              >Score</span
            >
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <span
              class="is-size-6 has-text-weight-bold"
              v-text="item.score"
            ></span>
          </div>
        </div>
      </div>
    </div>
  </transition>
  <transition name="fade" mode="out-in">
    <div
      class="panel-block"
      v-if="!isCollapsed && item.media.categories.length > 0"
      key="collapse"
    >
      <div class="level">
        <div class="level-left">
          <div class="level-item">
            <span
              class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
              >Categories</span
            >
          </div>
        </div>
        <div class="level-right">
          <div
            class="level-item"
            v-for="category in item.media.categories"
            v-bind:key="category"
          >
            <span
              class="is-size-6 has-text-weight-bold"
              v-text="category"
            ></span>
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
            <span
              class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
              >Type</span
            >
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <span
              class="is-size-6 has-text-weight-bold"
              v-text="item.media.type"
            ></span>
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
            <span
              class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
              >User</span
            >
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <span
              class="is-size-6 has-text-weight-bold"
              v-text="item.media.username"
            ></span>
          </div>
        </div>
      </div>
    </div>
  </transition>
  <transition name="fade" mode="out-in">
    <div
      class="panel-block"
      v-if="!isCollapsed && item.media.location !== null"
      key="collapse"
    >
      <div class="level">
        <div class="level-left">
          <div class="level-item">
            <span
              class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
              >Longitude</span
            >
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <span
              class="is-size-6 has-text-weight-bold"
              v-text="String(item.media.location.longitude)"
            ></span>
          </div>
        </div>
      </div>
    </div>
  </transition>
  <transition name="fade" mode="out-in">
    <div
      class="panel-block"
      v-if="!isCollapsed && item.media.location !== null"
      key="collapse"
    >
      <div class="level">
        <div class="level-left">
          <div class="level-item">
            <span
              class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
              >Latitude</span
            >
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <span
              class="is-size-6 has-text-weight-bold"
              v-text="String(item.media.location.latitude)"
            ></span>
          </div>
        </div>
      </div>
    </div>
  </transition>
  <transition name="fade" mode="out-in">
    <div
      class="panel-block"
      v-if="
        !isCollapsed &&
        item.media.location !== null &&
        item.media.location.hasAddress
      "
      key="collapse"
    >
      <div class="level">
        <div class="level-left">
          <div class="level-item">
            <span
              class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
              >Address</span
            >
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <p
              class="is-size-6 has-text-weight-bold has-text-right"
              v-text="item.media.location.address"
            ></p>
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
            <span
              class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
              >Time</span
            >
          </div>
        </div>
        <div class="level-right">
          <div class="level-item">
            <span
              class="is-size-6 has-text-weight-bold"
              v-text="item.media.createdAt.toLocaleString()"
            ></span>
          </div>
        </div>
      </div>
    </div>
  </transition>
  <transition name="fade" mode="out-in">
    <div
      class="panel-block"
      v-if="
        !isCollapsed &&
        item.media.description !== null &&
        item.media.description.length > 0
      "
      key="collapse"
    >
      <div class="content">
        <span class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
          >Description</span
        >
        <p
          class="is-size-6 has-text-weight-bold"
          v-text="item.media.description"
        ></p>
      </div>
    </div>
  </transition>
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

    > .level-left > .level-item > button.toggle {
      width: fit-content !important;
      height: fit-content !important;
      padding: 8px !important;
      box-shadow: none !important;
      line-height: 1.5rem !important;
      background: transparent !important;
      
      > span.icon {
        margin: 0 !important;
        width: 1.5rem !important;
        height: 1.5rem !important;
        font-size: 1.5rem !important;
        line-height: 1.5rem !important;
      }
    }

    > .level-right {
      margin: 0;

      > .level-item {
        .button.is-rounded {
          border-radius: 9999px !important;
          padding: 12px !important;
          box-shadow: none !important;

          > span.icon {
            margin: 0 !important;
            width: 1rem !important;
            height: 1rem !important;
          }
        }

        .button.toggle {
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
  }

  :not(nav).level {
    align-items: flex-start;

    > .level-left {
      margin: 0;
      flex-direction: column;
      align-items: flex-start;

      .level-item:not(:last-child) {
        margin: 0px 0px 0.5em 0px;
      }
    }

    > .level-right {
      margin: 0;
      width: 50%;
      flex-direction: column;

      > .level-item {
        width: 100%;
        justify-content: flex-end;
      }

      .level-item:not(:last-child) {
        margin: 0px 0px 0.5em 0px;
      }
    }
  }

  .control {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    padding: 0 !important;
    width: 400px;

    .level {
      padding: 0;
      width: 100%;

      > .level-item > .media {
        display: inline-block;
        margin: 0;
        border: 0px none transparent !important;
        padding: 0;
        width: 100%;

        .media-content {
          width: 100%;

          picture {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;

            img {
              object-fit: contain;
              width: 400px;
            }
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

    span + p,
    p {
      margin: 0.5em 0px 0px 0px;
      overflow-wrap: break-word;
    }
  }
}
</style>
