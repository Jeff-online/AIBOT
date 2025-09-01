import Vue from 'vue'
import App from './App.vue'
import 'element-ui/lib/theme-chalk/index.css';
import './styles/main.css';
import './styles/user-management.css';
import router from './router'
import axios from 'axios'

axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response.status === 401) {
      if (router.currentRoute.path !== '/login') {
        sessionStorage.clear();
        router.replace('/login');
      }
    }
    return Promise.reject(error)
  }
)

import { Button,Input } from 'element-ui';
Vue.use(Button).use(Input);

Vue.config.productionTip = false
new Vue({
  render: h => h(App),
  router
}).$mount('#app')

