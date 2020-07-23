<template>
  <div>
    <Header></Header>
    <Bodys></Bodys>
    <Footer></Footer>
  </div>
</template>

<script>
  import Header from "./common/Header"
  import Footer from "./common/Footer"
  import Bodys from "./common/Bodys"

  export default {
    name: "Index",
    components: {
      Header: Header,
      Footer: Footer,
      Bodys: Bodys,
    }
  }
</script>

<style scoped>

</style>
