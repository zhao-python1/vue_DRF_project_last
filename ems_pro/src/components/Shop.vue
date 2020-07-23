<!--<template>-->
    <!--<div class="cart">-->
        <!--<Header></Header>-->
        <!--<div class="cart_info">-->
            <!--<div class="cart_title">-->
                <!--<span class="text">我的购物车</span>-->
                <!--<span class="total">共4门课程</span>-->
            <!--</div>-->
            <!--<div class="cart_table">-->
                <!--<div class="cart_head_row">-->
                    <!--<span class="doing_row"></span>-->
                    <!--<span class="course_row">课程</span>-->
                    <!--<span class="expire_row">有效期</span>-->
                    <!--<span class="price_row">单价</span>-->
                    <!--<span class="do_more">操作</span>-->
                <!--</div>-->
                <!--<div class="cart_course_list">-->
                  <!--<ShopItme v-for="(course, index) in cart_list" :key="index" :course="course"></ShopItme>-->
                <!--</div>-->
                <!--<div class="cart_footer_row">-->
                    <!--<span class="cart_select"><label> <el-checkbox></el-checkbox><span>全选</span></label></span>-->
                    <!--<span class="cart_delete"><i class="el-icon-delete"></i> <span>删除</span></span>-->
                    <!--<span class="goto_pay">去结算</span>-->
                    <!--<span class="cart_total">总计：¥0.0</span>-->
                <!--</div>-->
            <!--</div>-->
        <!--</div>-->
        <!--<Footer></Footer>-->
    <!--</div>-->
<!--</template>-->

<!--<script>-->

    <!--import ShopItme from "./common/ShopItme";-->
    <!--import Header from "./common/Header";-->
    <!--import Footer from "./common/Footer";-->

    <!--export default {-->
        <!--name: "Shop",-->
        <!--created() {-->
            <!--this.get_cart()-->
        <!--},-->
        <!--data(){-->
            <!--return{-->
                <!--cart_list: [],-->
            <!--}-->
        <!--},-->
        <!--methods: {-->

            <!--// 检查用户是否已经登录-->
            <!--user_login() {-->
                <!--let token = localStorage.user_token || sessionStorage.user_token;-->
                <!--if (!token) {-->
                    <!--let self = this;-->
                    <!--this.$confirm("对不起，请登录后再添加购物车！", {-->
                        <!--callback() {-->
                            <!--self.$router.push("/login/");-->
                        <!--}-->
                    <!--});-->
                    <!--return false-->
                <!--}-->
                <!--return token;-->
            <!--},-->

            <!--// 获取购物车-->
            <!--get_cart() {-->
                <!--// 获取购物车判断用户是否已经登录-->
                <!--let token = this.user_login();-->
                <!--this.$axios.get(`${this.$settings.HOST}shop/shopping/`, {-->
                    <!--headers: {-->
                        <!--// 提交token必须在请求头声明token  jwt必须有空格-->
                        <!--"Authorization": "jwt " + token,-->
                    <!--}-->
                <!--}).then(response=>{-->
                    <!--this.cart_list = response.data;-->
                    <!--this.$store.commit("add_shop", this.cart_list.length);-->
                <!--}).catch(error=>{-->
                    <!--console.log(error.response);-->
                <!--})-->
            <!--},-->
        <!--},-->
        <!--components: {-->
            <!--ShopItme, Header, Footer-->
        <!--}-->
    <!--}-->
<!--</script>-->










<template>
  <div class="cart">
    <Header></Header>
    <div class="cart_info">
      <div class="cart_title">
        <span class="text">我的购物车</span>
        <span class="total">共4门课程</span>
      </div>
      <div class="cart_table">
        <div class="cart_head_row">
          <span class="doing_row"></span>
          <span class="course_row">课程</span>
          <span class="expire_row">有效期</span>
          <span class="price_row">单价</span>
          <span class="do_more">操作</span>
        </div>
        <div class="cart_course_list">
          <ShopItem v-for="(course,index) in cart_list" :key="index"
                    :course="course" @delete_cart="del_cart(index)" @change_select="cart_total_price"></ShopItem>
          <!--<ShopItem></ShopItem>-->
          <!--<ShopItem></ShopItem>-->
          <!--<ShopItem></ShopItem>-->
        </div>
        <div class="cart_footer_row">
          <span class="cart_select"><label><el-checkbox></el-checkbox><span>全选</span></label></span>
          <span class="cart_delete"><i class="el-icon-delete"></i> <span>删除</span></span>
          <router-link class="goto_pay" to="/settlement">去结算</router-link>
          <!--<span class="cart_total">总计：¥0.00</span>-->
          <span class="cart_total">总计：¥{{total_price}}</span>
        </div>
      </div>
    </div>
    <Footer></Footer>
  </div>
</template>

<script>
  import ShopItem from "./common/ShopItme";
  import Header from "./common/Header"
  import Footer from "./common/Footer"

  export default {
    name: "Shop",
    data() {
      return {
        cart_list: [],
        total_price:0.00, //转成浮点型价格  购物车已勾选的商品的总价格
      }
    },
    methods: {

      //在进行购物车之前先判断是否登陆
      user_login() {
        let token = localStorage.user_token || sessionStorage.user_token;
        console.log(token);
        if (!token) {
          let self = this;
          this.$confirm("sorry！请先登录", {
            callback() {
              self.$router.push("/login/");
            }
          });
          return false
        }
        return token
      },
      //计算机商品的总价
      cart_total_price(){
        let total = 0;
        //首先先遍历一下购物车里的数据内容  下标和值
        this.cart_list.forEach((course,key)=>{
          //接着判断商品是否被选中， 选中计算到总价里 不选则不计算
          if (course.selected){
            //吧价格转成浮点型的价格
            total += parseFloat(course.real_price);
          }
          this.total_price = total;
          console.log(this.total_price);
        })
      },
      //删除购物车
      del_cart(index){
        //从购物车中删除指定商品
        this.cart_list.splice(index,1);
        //删除后重新更新购物车数量
        this.$store.commit("add_shop",this.cart_list.length);
        //删除新的商品以后还要重新计算新的价格
        this.cart_total_price();
      },


      //获取购物车的数据
      get_cart(){
        let token = this.user_login();
        this.$axios({
          url:this.$settings.HOST+'shop/shopping/',
          method:'get',
          headers:{
            "Authorization":"jwt "+token
          }
        }).then(res=>{
          this.cart_list = res.data;
          //想状态机提交动作或者状态
          this.$store.commit('add_shop',this.cart_list.length);
          //计算总价价格 计算的是已勾选的价格
          this.cart_total_price();
        }).catch(error=>{
          console.log(error.response)
        })
      }
    },
    components: {
      ShopItem,Header,Footer
    },
    created(){
      this.get_cart()
    }
  }
</script>

<style scoped>
  .cart_info {
    width: 1200px;
    margin: 0 auto 200px;
  }

  .cart_title {
    margin: 25px 0;
  }

  .cart_title .text {
    font-size: 18px;
    color: #666;
  }

  .cart_title .total {
    font-size: 12px;
    color: #d0d0d0;
  }

  .cart_table {
    width: 1170px;
  }

  .cart_table .cart_head_row {
    background: #F7F7F7;
    width: 100%;
    height: 80px;
    line-height: 80px;
    padding-right: 30px;
  }

  .cart_table .cart_head_row::after {
    content: "";
    display: block;
    clear: both;
  }

  .cart_table .cart_head_row .doing_row,
  .cart_table .cart_head_row .course_row,
  .cart_table .cart_head_row .expire_row,
  .cart_table .cart_head_row .price_row,
  .cart_table .cart_head_row .do_more {
    padding-left: 10px;
    height: 80px;
    float: left;
  }

  .cart_table .cart_head_row .doing_row {
    width: 78px;
  }

  .cart_table .cart_head_row .course_row {
    width: 530px;
  }

  .cart_table .cart_head_row .expire_row {
    width: 188px;
  }

  .cart_table .cart_head_row .price_row {
    width: 162px;
  }

  .cart_table .cart_head_row .do_more {
    width: 162px;
  }

  .cart_footer_row {
    padding-left: 30px;
    background: #F7F7F7;
    width: 100%;
    height: 80px;
    line-height: 80px;
  }

  .cart_footer_row .cart_select span {
    margin-left: -7px;
    font-size: 18px;
    color: #666;
  }

  .cart_footer_row .cart_delete {
    margin-left: 58px;
  }

  .cart_delete .el-icon-delete {
    font-size: 18px;
  }

  .cart_delete span {
    margin-left: 15px;
    cursor: pointer;
    font-size: 18px;
    color: #666;
  }

  .cart_total {
    float: right;
    margin-right: 62px;
    font-size: 18px;
    color: #666;
  }

  .goto_pay {
    float: right;
    width: 159px;
    height: 80px;
    outline: none;
    border: none;
    background: #ffc210;
    font-size: 18px;
    color: #fff;
    text-align: center;
    cursor: pointer;
  }
</style>
