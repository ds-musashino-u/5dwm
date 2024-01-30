<script>
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup
import { ref, onMounted } from "vue";
import Sidebar from "./components/Sidebar.vue";
import Menu from "./components/Menu.vue";
import Search from "./components/Search.vue";
import Data from "./components/Data.vue";
import Uploader from "./components/Uploader.vue";
import { Auth0Config } from "./presenters/auth0-config.mjs";
import { createAuth0Client } from "@auth0/auth0-spa-js";
import { jwtDecode } from "jwt-decode";

export default {
  components: {
    Sidebar,
    Menu,
    Search,
    Data,
    Uploader,
  },
  data() {
    return {
      isRevealed: false,
      updatedTime: 0,
      contentIndex: 0,
      contents: [
        {
          icon: "fa-solid fa-magnifying-glass",
          name: "Search",
          component: "Search",
        },
        {
          icon: "fa-solid fa-database",
          name: "My Data",
          component: "Data",
        },
        {
          icon: "fa-solid fa-cloud-arrow-up",
          name: "Upload",
          component: "Uploader",
        },
      ],
    };
  },
  methods: {
    reveal() {
      this.isRevealed = !this.isRevealed;
    },
    select(data) {
      this.contentIndex = parseInt(data.index);
      this.isRevealed = false;
    },
    updated() {
      this.updatedTime = Math.floor(new Date() / 1000);
    }
  },
  setup(props) {
    const auth0 = ref(null);
    const user = ref(null);
    const isSigningIn = ref(false);
    const isSigningOut = ref(false);
    const isAdmin = ref(false);

    onMounted(async () => {
      const callbackUrl = new URL(window.location.origin);

      callbackUrl.pathname = "/callback/";

      try {
        isSigningIn.value = true;
        auth0.value = await createAuth0Client({
          domain: Auth0Config.DOMAIN,
          clientId: Auth0Config.CLIENT_ID,
          audience: Auth0Config.AUDIENCE,
          authorizationParams: {
            redirect_uri: callbackUrl.toString()
          },
          cacheLocation: 'localstorage'
        });

        if (await auth0.value.isAuthenticated()) {
          const accessToken = await auth0.value.getTokenSilently({
            authorizationParams: {
              audience: Auth0Config.AUDIENCE
            }
          });

          const decoded = jwtDecode(accessToken);

          if ("permissions" in decoded && decoded["permissions"].some(x => x.endsWith(":all"))) {
            isAdmin.value = true;
          }

          user.value = await auth0.value.getUser();

          console.log(jwtDecode(accessToken));
          console.log(await auth0.value.getIdTokenClaims());
          console.log(user.value);
        } else {
          let code = null;
          let state = null;
          let error = null;

          for (const [key, value] of new URLSearchParams(
            window.location.search
          ).entries()) {
            if (key === "code") {
              code = value;
            } else if (key === "state") {
              state = value;
            } else if (key === "error") {
              error = value;
            }
          }

          if (code !== null && state !== null || error !== null) {
            await auth0.value.handleRedirectCallback();

            let accessToken;

            try {
              accessToken = await auth0.value.getTokenSilently({
                authorizationParams: {
                  audience: Auth0Config.AUDIENCE
                }
              });
            } catch (error) {
              console.error(error);

              accessToken = await auth0.value.getTokenWithPopup({
                authorizationParams: {
                  audience: Auth0Config.AUDIENCE
                }
              });
            }

            const decoded = jwtDecode(accessToken);

            if ("permissions" in decoded && decoded["permissions"].some(x => x.endsWith(":all"))) {
              isAdmin.value = true;
            }

            user.value = await auth0.value.getUser();
            console.log(user.value);
          }

          window.history.replaceState({}, document.title, "/");
        }
      } catch (error) {
        console.error(error);
      } finally {
        isSigningIn.value = false;
      }
    });

    const signIn = async (forcePopup) => {
      if (forcePopup) {
        try {
          isSigningIn.value = true;

          const accessToken = await auth0.value.getTokenWithPopup({
            authorizationParams: {
              audience: Auth0Config.AUDIENCE
            }
          });

          const decoded = jwtDecode(accessToken);

          if ("permissions" in decoded && decoded["permissions"].some(x => x.endsWith(":all"))) {
            isAdmin.value = true;
          }

          user.value = await auth0.value.getUser();
        } catch (error) {
          console.error(error);
        } finally {
          isSigningIn.value = false;
        }
      } else {
        const callbackUrl = new URL(window.location.origin);

        callbackUrl.pathname = "/callback/";

        try {
          isSigningIn.value = true;

          await auth0.value.loginWithRedirect({
            authorizationParams: {
              redirect_uri: callbackUrl.toString()
            }
          });
        } catch (error) {
          console.error(error);
        } finally {
          isSigningIn.value = false;
        }
      }
      /*if (window.navigator.userAgent.indexOf("Safari") > -1 && !/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        try {
          isSigningIn.value = true;

          await auth0.value.loginWithPopup();
          const accessToken = await auth0.value.getTokenWithPopup({
            authorizationParams: {
              audience: Auth0Config.AUDIENCE
            }
          });

          const decoded = jwtDecode(accessToken);

          if ("permissions" in decoded && decoded["permissions"].some(x => x.endsWith(":all"))) {
            isAdmin.value = true;
          }

          user.value = await auth0.value.getUser();
        } catch (error) {
          console.error(error);
        } finally {
          isSigningIn.value = false;
        }
      } else {
        const callbackUrl = new URL(window.location.origin);

        callbackUrl.pathname = "/callback/";

        try {
          isSigningIn.value = true;

          await auth0.value.loginWithRedirect({
            authorizationParams: {
              redirect_uri: callbackUrl.toString()
            }
          });
        } catch (error) {
          console.error(error);
        } finally {
          isSigningIn.value = false;
        }
      }*/
    };
    const signOut = async () => {
      try {
        isSigningOut.value = true;
        await auth0.value.logout({
          logoutParams: {
            returnTo: window.location.origin
          }
        });
        user.value = null;
      } catch (error) {
        console.error(error);
      } finally {
        isSigningOut.value = false;
      }
    };

    return { auth0, user, isSigningIn, isSigningOut, isAdmin, signIn, signOut };
  },
  mounted() { },
};
</script>

<template>
  <div class="wrap">
    <div class="frame">
      <Sidebar :user="user" :items="contents" :index="contentIndex" :is-revealed="isRevealed" @reveal="reveal" @select="select" />
      <div class="wrap">
        <div class="content">
          <transition name="fade">
            <keep-alive>
              <component :is="contents[contentIndex].component"
                v-bind="{ auth0: auth0, user: user, text: contents[contentIndex].name, updatedTime: updatedTime, isAdmin: isAdmin }"
                v-on="{ updated: updated }" :key="contents[contentIndex].name"></component>
            </keep-alive>
          </transition>
        </div>
        <transition name="reveal">
          <Menu logo-url="/images/logo.png" subtitle="5dworldmap.com" v-bind:is-loading="isSigningIn || isSigningOut"
            v-bind:is-admin="isAdmin" v-bind:user="user" v-bind:items="contents" @select="select" @sign-in="signIn"
            @sign-out="signOut" v-if="user === null || isRevealed" />
        </transition>
      </div>
      <div class="left is-hidden-tablet" v-cloak>
        <transition name="fade" mode="out-in">
          <button class="button is-circle" type="button" @click="reveal" key="menu">
            <transition name="fade" mode="out-in">
              <span class="icon is-small" v-if="isRevealed" key="open">
                <i class="fa-solid fa-xmark"></i>
              </span>
              <span class="icon is-small" v-else key="close">
                <i class="fa-solid fa-bars"></i>
              </span>
            </transition>
          </button>
        </transition>
      </div>
    </div>  
  </div>
</template>

<style lang="scss"></style>
