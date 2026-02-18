<template>
  <div class="auth-page">
    <div class="auth-page__bg" />
    <LoginForm class="auth-page__form" />
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
}
.auth-page__bg {
  position: absolute;
  inset: 0;
  background: #f5f6fa;
}
.auth-page__form {
  position: relative;
  z-index: 1;
}
</style>

<script>
import LoginForm from '@components/features/login_page/LoginForm.vue';
export default {
  name: "LoginPage",
  components: { LoginForm },
}
</script>
