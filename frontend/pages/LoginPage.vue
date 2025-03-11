<template>
  <div class="row">
		<Layout/>
    <Form/>
  </div>
</template>
  
  <script>
  import Layout from '../components/for_pages/LoginPage/Layout.vue';
  import Form from '../components/for_pages/LoginPage/Form.vue';
  export default {
    name: "LoginPage",
    components: { Layout, Form },
  }
  </script>
  
  <style scoped>
  </style>