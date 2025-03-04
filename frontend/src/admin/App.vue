<template>
  <h1>App</h1>
  <router-link to="/login">
    <button>login</button>
  </router-link>
	<router-view />
  </template>
  
  <script>
  export default {
	name: "App",
  };
  </script>
  