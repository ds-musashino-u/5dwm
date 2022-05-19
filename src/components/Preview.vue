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
            ><span class="icon is-small"
              ><i class="fa-solid fa-link"></i></span
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
                  <img v-bind:src="item.url" v-bind:alt="String(index)" />
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
          <span class="is-size-6 is-uppercase has-text-weight-bold has-text-grey"
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
