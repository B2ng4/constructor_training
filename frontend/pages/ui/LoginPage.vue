<template>
  <div class="row justify-center">
    <LoginForm/>
  </div>
</template>

<script>
import LoginForm from '@components/features/login_page/LoginForm.vue';
export default {
  name: "LoginPage",
  components: { LoginForm },
}
</script>
