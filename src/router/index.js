import Vue from 'vue';
import Router from 'vue-router';
import Home from '@/components/Home.vue';
import My from '@/components/My.vue';
Vue.use(Router);
const routes = [
    { path: '/', component: Home },
    { path: '/login', component: My }
  ]
  
export default new Router({ routes })
