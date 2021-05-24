<template>
  <v-app>
    <NavBar />
    <v-main>
      <WebView />
    </v-main>
  </v-app>
</template>

<script>
import NavBar from "./components/NavBar";
import WebView from "./components/WebView";

export default {
  name: "App",

  components: {
    NavBar,
    WebView,
  },

  data: () => ({
    //
  }),
};
</script>
