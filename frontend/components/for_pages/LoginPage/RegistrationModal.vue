<template>
  <BaseModal :show="show" @close="handleClose">
    <template v-slot:header>
        <div class="row justify-center text-h5">Регистрация</div>
    </template>
    <template v-slot:body>
      <q-form
      @submit="onSubmit"
      class="q-gutter-md"
    >
      <div class="row">
        <q-input
          filled
          v-model="user.surname"
          label="Фамилия *"
          lazy-rules
          :rules="[ val => val && val.length > 0 || 'Введите данные']"
        />
        <q-input
          filled
          v-model="user.name"
          label="Имя *"
          class="q-ml-xl"
          lazy-rules
          :rules="[ val => val && val.length > 0 || 'Введите данные']"
        />
      </div>
      <q-input
        filled
        v-model="user.phone"
        label="Номер телефона *"
        lazy-rules
        :rules="[ val => val && val.length > 0 || 'Введите данные']"
      />
      <q-input
        filled
        v-model="user.email"
        label="Почта *"
        lazy-rules
        :rules="[ val => val && val.length > 0 || 'Введите данные']"
      />
      <q-input
        filled
        v-model="user.password"
        label="Пароль *"
        lazy-rules
        type="password"
        :rules="[ val => val && val.length > 0 || 'Введите данные']"
      />
      <div class="row justify-center">
        <q-btn type="sumbit" class="fit" color="primary" label="Регистрация" />
      </div>
    </q-form>
    </template>
  </BaseModal>
</template>

<script>
import axios from 'axios';
import BaseModal from '@components/BaseComponents/BaseModal.vue';
export default {
    name: 'RegistrationModal',
    components: {BaseModal},
    props: ['show'],
    data() {
      return {
        user: {
          surname: '',
          name: '',
          phone: '',
          email: '',
          password: '',
        }
      }
    },
    methods: {
        handleClose() {
            this.$emit('close');
        },
        async onSubmit() {
          axios.post(`${__BASE__URL__}/auth/register`, {
            email: this.user.email,
            phone_number: this.user.phone,
            first_name: this.user.name,
            last_name: this.user.surname,
            password: this.user.password,
          });
        }
    }
}
</script>

<style scoped>
</style>