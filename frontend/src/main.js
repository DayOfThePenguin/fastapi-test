import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import AtomGraph from './graph/atom-graph'

Vue.config.productionTip = false

new Vue({
  vuetify,
  methods: {},
  mounted() {},
  render: h => h(App)
}).$mount('#app')

const ag = new AtomGraph
ag.setHome()