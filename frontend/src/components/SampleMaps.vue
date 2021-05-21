<template>
  <v-container>
    <v-row class="pa-2" justify="space-around">
      <v-card flat tile class="red lighten-1 white--text text-center">
        <v-card-title>Sample Maps</v-card-title>
        <v-card-text>
          <v-simple-table color="primary">
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-left">Name</th>
                  <th class="text-left">Pages in Map</th>
                </tr>
              </thead>
              <tbody>
                {% for map in maps %}
                <tr>
                  <td>
                    <a href="maps/{{ url_for_wikimap(map) }}">{{
                      map.title
                    }}</a>
                  </td>
                  <td>{{ map.pages_per_level ** map.levels }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
      </v-card>
    </v-row>
    <v-row justify="center" class="pa"> </v-row>
  </v-container>
</template>