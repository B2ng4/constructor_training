<template>
	<div class="row justify-center items-center full-height">
		<Layout/>
	  <div class="col-6 flex justify-center items-center content-center">
		<Form/>
	  </div>
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