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
import { createAuth0Client } from '@auth0/auth0-spa-js';
import jwt_decode from 'jwt-decode';

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
      contentIndex: 0,
      contents: [
        {
          icon: "fa-solid fa-magnifying-glass",
          name: "Search",
          component: "Search",
        },
        {
          icon: "fa-solid fa-database",
          name: "Data",
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
  },
  setup(props) {
    const auth0 = ref(null);
    const user = ref(null);
    const isSigningIn = ref(false);
    const isSigningOut = ref(false);
    const isAdmin = ref(false);

    onMounted(async () => {
      try {
        isSigningIn.value = true;
        auth0.value = await createAuth0Client({
          domain: Auth0Config.DOMAIN,
          clientId: Auth0Config.CLIENT_ID,
          authorizationParams: {
            redirect_uri: window.location.origin
          },
          cacheLocation: 'localstorage'
        });

        if (await auth0.value.isAuthenticated()) {
          const accessToken = await auth0.value.getTokenSilently({
            authorizationParams: {
              audience: Auth0Config.AUDIENCE
            }
          });

          const decoded = jwt_decode(accessToken);

          if ("permissions" in decoded && decoded["permissions"].some(x => x.endsWith(":all"))) {
            isAdmin.value = true;
          }

          user.value = await auth0.value.getUser();

          console.log(jwt_decode(accessToken));
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

            const accessToken = await auth0.value.getTokenSilently({
              authorizationParams: {
                audience: Auth0Config.AUDIENCE
              }
            });

            const decoded = jwt_decode(accessToken);

            if ("permissions" in decoded && decoded["permissions"].some(x => x.endsWith(":all"))) {
              isAdmin.value = true;
            }

            user.value = await auth0.value.getUser();
          }

          window.history.replaceState({}, document.title, "/");
        }
      } catch (error) {
        console.error(error);
      } finally {
        isSigningIn.value = false;
      }
    });

    const signIn = async (e) => {
      try {
        isSigningIn.value = true;
        await auth0.value.loginWithRedirect({
          authorizationParams: {
            redirect_uri: window.location.origin
          }
        });
      } catch (error) {
        console.error(error);
      } finally {
        isSigningIn.value = false;
      }
    };
    const signOut = async () => {
      try {
        isSigningOut.value = true;
        await auth0.value.logout();
        user.value = null;
      } catch (error) {
        console.error(error);
      } finally {
        isSigningOut.value = false;
      }
    };

    return { auth0, user, isSigningIn, isSigningOut, signIn, signOut };
  },
  mounted() { },
};
</script>

<template>
  <!--<img alt="Vue logo" src="./assets/logo.png" />-->
  <Sidebar :user="user" :items="contents" :index="contentIndex" @reveal="reveal" @select="select" />
  <div class="wrap">
    <div class="content">
      <keep-alive>
        <component :is="contents[contentIndex].component"
          v-bind="{ auth0: auth0, user: user, text: contents[contentIndex].name }"></component>
      </keep-alive>
    </div>
    <transition name="reveal">
      <Menu logo-url="/images/logo.png" subtitle="5dworldmap.com" v-bind:is-loading="isSigningIn || isSigningOut"
        v-bind:user="user" v-bind:items="contents" @select="select" @sign-in="signIn" @sign-out="signOut"
        v-if="user === null || isRevealed" />
    </transition>
  </div>
  <div class="left is-hidden-tablet" v-cloak>
    <transition name="fade" mode="out-in">
      <button class="button is-circle" type="button" @click="reveal" key="menu">
        <span class="icon is-small">
          <i class="fas fa-bars"></i>
        </span>
      </button>
    </transition>
  </div>
</template>

<style lang="scss">

</style>
