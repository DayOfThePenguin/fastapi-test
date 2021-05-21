<template>
  <v-container class="align-content-space-around">
    <v-row justify="center" cols="12">
      <v-col xs="12" sm="10" md="8" lg="6" xl="5">
        <v-img
          class="my-5"
          :src="require('../assets/wikimap.svg')"
          min-height="150"
        >
        </v-img>
      </v-col>
    </v-row>
    <v-form action="/search" method="post">
      <v-row justify="center" cols="12">
        <v-col xs="12" sm="10" md="8" lg="6" xl="5">
          <v-text-field
            name="title_query"
            color="primary"
            clearable
            rounded
            filled
            label="Search Wikipedia"
            prepend-inner-icon="mdi-magnify"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row align="center" justify="space-around" class="mt-3" cols="12">
        <v-btn type="submit" color="primary"> Search </v-btn>
      </v-row>
    </v-form>
    <v-row class="pa-3">
      <v-col cols="8">
        <v-divider></v-divider>
      </v-col>
    </v-row>
  </v-container>
</template>