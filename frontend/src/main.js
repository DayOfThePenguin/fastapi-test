import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import AtomGraph from './graph/atom-graph'

Vue.config.productionTip = false

new Vue({
  vuetify,
  methods: {
    showDialog: function() {
      
      var elem = this.$els.toggleDialog;
      console.log(elem);
    }
  },
  mounted() {
    // eslint-disable-next-line no-unused-vars
    const ag = new AtomGraph
    ag.setHome()
    // showDialog();
  },
  render: h => h(App)
}).$mount('#app')
