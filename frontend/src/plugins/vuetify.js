import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';
import '@mdi/font/css/materialdesignicons.css'

// import colors from 'vuetify/lib/util/colors';
import { preset } from 'vue-cli-plugin-vuetify-preset-rally/preset'

Vue.use(Vuetify);

export default new Vuetify({
  preset,
  icons: {
    iconfont: 'mdiSvg',
  },
});