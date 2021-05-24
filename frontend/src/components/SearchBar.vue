<template>
  <v-container class="align-content-space-around" pt-10>
    <v-form action="/search" method="post">
      <v-row justify="center" cols="12">
        <v-col cols="12">
          <v-text-field name="title_query" color="primary" clearable rounded filled label="Search Wikipedia"
            prepend-inner-icon="mdi-magnify">
          </v-text-field>
        </v-col>
      </v-row>
      <v-row align="center" justify="space-around" class="mt-4" cols="12">
        <v-btn type="submit" color="primary"> Search </v-btn>
      </v-row>
    </v-form>
  </v-container>
</template>
<script>
  export default {
    name: "SearchBar",
  }
</script>