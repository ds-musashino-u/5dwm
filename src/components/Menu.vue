<script setup>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref } from "vue";

const props = defineProps({
  logoUrl: { type: String, required: false, default: null },
  title: { type: String, required: false, default: null },
  subtitle: { type: String, required: false, default: null },
  isLoading: { type: Boolean, required: false, default: false },
  isAdmin: { type: Boolean, required: false, default: false },
  user: { type: Object, required: false, default: null },
  items: Array,
});
const emit = defineEmits(["reveal", "select", "signIn", "signOut"]);
const select = (event) => {
  emit("select", event.target.dataset);
};
const signIn = (event, forcePopup) => {
  emit("signIn", forcePopup);
};
const signOut = (event) => {
  emit("signOut");
};
</script>

<template>
  <div id="menu" ref="menu">
    <div class="columns is-centered">
      <div class="column is-half-tablet">
        <div class="control" v-cloak>
          <transition name="fade" mode="out-in">
            <nav class="level" v-if="user === null" key="signin">
              <div class="level-item">
                <div class="block">
                  <nav class="panel">
                    <div class="panel-heading" v-if="
                      logoUrl !== null || title !== null || subtitle !== null
                    ">
                      <img v-bind:src="logoUrl" alt="Logo" v-if="logoUrl !== null" />
                      <h1 class="
                              is-primary is-uppercase is-size-4
                              has-text-weight-bold
                            " v-if="title !== null">
                        {{ title }}
                      </h1>
                      <h2 class="is-size-7 has-text-weight-bold" v-if="subtitle !== null">
                        {{ subtitle }}
                      </h2>
                    </div>
                    <div class="panel-block">
                      <div class="control">
                        <button class="
                                button
                                is-rounded
                                is-outlined
                                is-fullwidth
                                is-size-7
                                is-primary
                              " type="button" v-bind:disabled="isLoading" @click="signIn($event, false)">
                          <transition name="fade" mode="out-in">
                            <span class="icon" v-if="isLoading" key="loading">
                              <i class="fas fa-spinner updating"></i>
                            </span>
                            <span class="icon" v-else key="loaded">
                              <i class="fa-solid fa-arrow-right-to-bracket"></i>
                            </span>
                          </transition>
                          <span class="is-uppercase has-text-weight-bold">Sign In</span>
                        </button>
                      </div>
                    </div>
                    <div class="panel-block">
                      <div class="control">
                        <button class="
                                button
                                is-rounded
                                is-outlined
                                is-fullwidth
                                is-size-7
                              " type="button" v-bind:disabled="isLoading" @click="signIn($event, true)">
                          <transition name="fade" mode="out-in">
                            <span class="icon" v-if="isLoading" key="loading">
                              <i class="fas fa-spinner updating"></i>
                            </span>
                            <span class="icon" v-else key="loaded">
                              <i class="fa-solid fa-arrow-right-to-bracket"></i>
                            </span>
                          </transition>
                          <span class="is-uppercase has-text-weight-bold">Sign In with Popup</span>
                        </button>
                      </div>
                    </div>
                  </nav>
                </div>
              </div>
            </nav>
            <nav class="level" v-else key="main">
              <div class="level-item">
                <div class="block">
                  <nav class="panel">
                    <div class="panel-heading" v-if="
                      logoUrl !== null || title !== null || subtitle !== null
                    ">
                      <img v-bind:src="logoUrl" alt="Logo" v-if="logoUrl !== null" />
                      <h1 class="
                              is-primary is-uppercase is-size-4
                              has-text-weight-bold
                            " v-if="title !== null">
                        {{ title }}
                      </h1>
                      <h2 class="is-size-7 has-text-weight-bold" v-if="subtitle !== null">
                        {{ subtitle }}
                      </h2>
                    </div>
                    <div class="panel-block">
                      <div class="block" v-if="'picture' in user">
                        <div class="is-superellips">
                          <figure>
                            <picture class="image is-64x64">
                              <img v-bind:src="user.picture" width="64" height="64" v-bind:alt="user.name" />
                            </picture>
                          </figure>
                        </div>
                      </div>
                      <div class="block">
                        <h2 class="is-size-5 has-text-weight-bold" v-if="'nickname' in user">
                          {{ user.nickname }}
                        </h2>
                        <h3 class="is-size-7 has-text-weight-bold">
                          {{ user.name }}
                        </h3>
                      </div>
                      <div class="block" v-if="isAdmin">
                        <span class="icon-text">
                          <span class="icon">
                            <i class="fa-solid fa-id-badge"></i>
                          </span>
                          <span class="is-uppercase is-size-7 has-text-weight-bold">Admin</span>
                          <a href="https://manage.auth0.com/dashboard/jp/5dwm/" target="_blank">
                            <span class="icon">
                              <i class="fa-solid fa-users-gear fa-xs"></i>
                            </span>
                          </a>
                        </span>
                      </div>
                    </div>
                    <div class="panel-block is-hidden-tablet" v-for="(item, index) in items" v-bind:key="item">
                      <div class="control">
                        <button class="
                                button
                                is-rounded
                                is-outlined
                                is-fullwidth
                                is-size-7
                                is-primary
                              " type="button" v-bind:disabled="isLoading" v-bind:data-index="index"
                          v-bind:data-name="item.name" @click="select">
                          <span class="icon">
                            <i v-bind:class="item.icon"></i>
                          </span>
                          <span class="is-uppercase has-text-weight-bold">{{
                            item.name
                          }}</span>
                        </button>
                      </div>
                    </div>
                    <div class="panel-block">
                      <div class="control">
                        <button class="
                                button
                                is-rounded is-outlined is-fullwidth is-size-7
                              " type="button" v-bind:disabled="isLoading" @click="signOut">
                          <transition name="fade" mode="out-in">
                            <span class="icon" v-if="isLoading" key="loading">
                              <i class="fas fa-spinner updating"></i>
                            </span>
                            <span class="icon" v-else key="loaded">
                              <i class="fa-solid fa-arrow-right-from-bracket"></i>
                            </span>
                          </transition>
                          <span class="is-uppercase has-text-weight-bold">Sign Out</span>
                        </button>
                      </div>
                    </div>
                  </nav>
                </div>
              </div>
            </nav>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
#menu>.columns>.column {
  padding: 0;

  >.control {
    padding: 16px;

    >.level:first-child {
      margin: -8px !important;

      >.level-item {
        margin: 0;
        padding: 8px !important;

        >.block {
          .panel {
            background: #ffffff !important;
            border-radius: 4px !important;
            box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
              0 0px 0 1px rgb(10 10 10 / 2%) !important;

            .panel-heading {
              display: flex;
              flex-direction: column;
              justify-content: center;
              align-items: center;
              margin: 0;
              border-bottom: 1px solid hsl(0deg, 0%, 93%);
              border-radius: 0;
              padding: 24px 24px 24px 24px;
              background: transparent;

              .block {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 12px 0px 0px 0px;
                padding: 0;
              }

              .block:first-of-type {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 24px 0px 0px 0px;
                padding: 0;
              }

              h1+h2 {
                margin: 6px 0px 0px 0px;
              }

              h2+h3 {
                margin: 6px 0px 0px 0px;
              }
            }

            .panel-tabs:not(:last-child),
            .panel-block:not(:last-child) {
              border-bottom: 1px solid hsl(0deg, 0%, 93%);
            }

            >.panel-block {
              display: flex;
              padding: 0.5em 0.75em;
              flex-direction: column;
              justify-content: center;
              align-items: center;

              .block>.icon-text span+a {
                margin-left: 0.5em
              }
            }

            >.panel-block:nth-of-type(2) {
              >.block:first-child {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 0;
                padding: 0;
              }

              >.block:not(:first-child) {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 6px 0px 0px 0px;
                padding: 0;
              }
            }

            .panel-block:first-child,
            .panel-block:last-child {
              border-radius: 0;
            }
          }

          button {
            border: 0px solid transparent !important;
            border-radius: 4px !important;
            box-shadow: 0 0.5em 1em -0.125em rgb(10 10 10 / 10%),
              0 0px 0 1px rgb(10 10 10 / 2%) !important;
          }
        }
      }
    }
  }
}
</style>
