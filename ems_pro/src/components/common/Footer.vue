<template>

  <div class="footer">
    <ul>
      <li v-for="(nav,key) in nav_list" :key="key"><span>{{nav.title}}</span></li>
      <!--<li>联系我们</li>-->
      <!--<li>百知教育</li>-->
      <!--<li>帮助中心</li>-->
      <!--<li>意见反馈</li>-->
      <!--<li>新手指南</li>-->
    </ul>
  </div>
</template>

<script>
  export default {
    name: "Footer",
    // 获取导航条的数据
    data() {
      return {
        nav_list: [], // 导航条的数据
        // token:"",
      }
    },
    methods: {
      //h获取token确定登录状态
      // 获取导航栏的方法
      get_all_nav() {
        this.$axios({
          url: this.$settings.HOST + 'first/navs/',
          method: "get",
        }).then(res => {
          // 当前请求的返回值可以通过res接受到
          console.log(res.data);
          this.nav_list = res.data;
        }).catch(error => {
          console.log(error);
        })
      },
    },
    created() {
      // 获取导航数据
      this.get_all_nav();
      // this.get_token();
    }

  }
</script>

<style scoped>
  .footer {
    width: 100%;
    height: 128px;
    background: #25292e;
    color: #fff;
  }

  .footer ul {
    margin: 0 auto 16px;
    padding-top: 38px;
    width: 810px;
  }

  .footer ul li {
    float: left;
    width: 112px;
    margin: 0 10px;
    text-align: center;
    font-size: 14px;
  }

  .footer ul::after {
    content: "";
    display: block;
    clear: both;
  }

  .footer p {
    text-align: center;
    font-size: 12px;
  }
</style>
