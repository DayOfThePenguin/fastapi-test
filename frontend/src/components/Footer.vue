<template>
  <v-footer dark padless color="secondary">
    <v-row no-gutters justify="center">
      <v-card flat tile color="secondary" class="text-center">
        <v-card-text>
          <v-btn href="/docs" class="mx-2" elevation="5" color="primary">
            API Documentation
          </v-btn>
          <v-btn
            href="https://github.com/DayOfThePenguin/r3th.ink"
            class="mx-2"
            elevation="5"
            color="quinary"
          >
            GitHub
          </v-btn>
          <v-btn
            href="https://github.com/DayOfThePenguin/r3th.ink/issues"
            class="mx-2"
            elevation="5"
            color="primary"
          >
            Bugs/Feature Requests
          </v-btn>
        </v-card-text>
        <v-card-text class="white--text pt-0"> </v-card-text>
        <v-divider></v-divider>
        <v-card-text>
          <v-col class="py-4 text-center white--text" cols="12">
            &copy; {{ new Date().getFullYear() }} —
            <strong>Colin Dablain</strong>
          </v-col>
        </v-card-text>
      </v-card>
    </v-row>
  </v-footer>
</template>

<script>
export default {
  name: "Footer",
};
</script>
