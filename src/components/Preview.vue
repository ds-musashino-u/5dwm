<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, reactive, toRef, watch } from "vue";

const props = defineProps({
  isCollapsed: { type: Boolean, required: false, default: false },
  item: { type: Object, required: false, default: null },
});
</script>

<template>
  <div class="panel-block">
    <nav class="level is-mobile">
      <div class="level-left">
        <div class="level-item">
          <span class="icon is-small" v-if="item.type.startsWith('image')">
            <i class="fa-solid fa-file-image"></i>
          </span>
          <span class="icon is-small" v-else-if="item.type.startsWith('video')">
            <i class="fa-solid fa-file-video"></i>
          </span>
          <span class="icon is-small" v-else-if="item.type.startsWith('audio')">
            <i class="fa-solid fa-file-audio"></i>
          </span>
          <span class="icon is-small" v-else-if="item.type.startsWith('text')">
            <i class="fa-solid fa-file-lines"></i>
          </span>
          <span class="icon is-small" v-else>
            <i class="fa-solid fa-file"></i>
          </span>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <a class="button is-rounded" target="_blank" v-bind:href="item.url"
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
        v-if="!isCollapsed && item.type.startsWith('image')"
        key="image"
      >
        <nav class="level">
          <div class="level-item">
            <article class="media">
              <div class="media-content">
                <picture class="image">
                  <img v-bind:src="item.url" alt="Picture" />
                </picture>
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
            v-text="item.type"
          ></span>
        </div>
      </div>
    </div>
  </div>
  <div class="panel-block">
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
            v-text="item.username"
          ></span>
        </div>
      </div>
    </div>
  </div>
  <div class="panel-block" v-if="item.location !== null">
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
            v-text="String(item.location.longitude)"
          ></span>
        </div>
      </div>
    </div>
  </div>
  <div class="panel-block" v-if="item.location !== null">
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
            v-text="String(item.location.latitude)"
          ></span>
        </div>
      </div>
    </div>
  </div>
  <div
    class="panel-block"
    v-if="item.location !== null && item.location.hasAddress"
  >
    <div class="level">
      <div class="level-left">
        <div class="level-item">
          <span
            class="is-size-6 is-uppercase has-text-weight-bold has-text-grey has-text-right"
            >Address</span
          >
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <p
            class="is-size-6 has-text-weight-bold"
            v-text="item.location.address"
          ></p>
        </div>
      </div>
    </div>
  </div>
  <div class="panel-block">
    <div class="level">
      <div class="level-left">
        <div class="level-item">
          <span
            class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
            >Created</span
          >
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <span
            class="is-size-6 has-text-weight-bold"
            v-text="item.createdAt.toLocaleString()"
          ></span>
        </div>
      </div>
    </div>
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
    
    > .level-right {
      margin: 0;
      width: 50%;

      > .level-item {
        width: 100%;
        justify-content: flex-end;
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
              width: 100%;
              height: 100%;
            }
          }
        }
      }
    }
  }

  .control:last-child {
    padding: 12px 0px 0px 0px;
  }
}
</style>
