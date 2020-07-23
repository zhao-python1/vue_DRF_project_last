// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store/index'

//配置axios
import axios from 'axios'

Vue.prototype.$axios = axios;

// 导入Element UI的组件
import ElementUI from 'element-ui'
// 导入样式
import "element-ui/lib/theme-chalk/index.css"

//导入极验
import "../static/js/gt.js"

// 全局注册element组件
Vue.use(ElementUI)

//全局css样式
// import "../static/css/global.css";

import settings from "./settings";

Vue.prototype.$settings = settings;
Vue.config.productionTip = false

//全局css、
import '../static/css/global.css'

// video的配置
require('video.js/dist/video-js.css');
require('vue-video-player/src/custom-theme.css');
import VideoPlayer from 'vue-video-player'

Vue.use(VideoPlayer);



/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: {App},
  template: '<App/>'
})
