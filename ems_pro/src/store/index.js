import Vue from 'vue'

import Vuex from 'vuex'

Vue.use(Vuex);

export default new Vuex.Store({
    state:{
        // 购物车数据
        cart_length: 0,
    },
    mutations:{
        // 监测提交购物车的动作
        add_shop(state, data){
            state.cart_length = data;
        }
    }
})
