<template>
    <div class="container">
        <BaseCard class="card text-blue-grey-8" width="400px" title="Вход">
            <template v-slot:body>
                <div class="column justify-center items-center content-center">
                    <q-input
                        filled
                        v-model="email"
                        label="Логин *"
                        lazy-rules
                        class="full-width"
                        :rules="[ val => val && val.length > 0 || 'Введите логин']"
                    />
                    <q-input
                        filled
                        type="password"
                        v-model="password"
                        label="Пароль *"
                        lazy-rules
                        class="full-width q-mt-lg"
                        :rules="[
                        val => val !== null && val !== '' || 'Введите пароль',
                        ]"
                    />
                        <q-btn label="Войти" class="q-mt-lg full-width" color="primary" @click="login()"/>
                </div>
            </template>
        </BaseCard> 
    </div>
</template>

<script>
import axios from 'axios';
import BaseCard from '@components/BaseComponents/BaseCard.vue';
export default {
    name: 'Form',
    components: {BaseCard},
    data() {
        return {
            email: '',
            password: ''
        }
    },
    methods: {
        async login() {
            let form = new FormData();
            form.set('username', this.email);
            form.set('password', this.password);
            axios.post(`${__BASE__URL__}/auth/login`, form)
                .then((response) => {
                    localStorage.setItem('tokenAuth', response.data.access_token);
                    this.$router.push('/personal');
                })
                .catch(() => {
                });
        }
    }
}
</script>

<style scoped>
.container {
    height: 100vh;
    width: 50%;
    display: flex;
    justify-content: center; 
    align-items: center; 
}

.my-card :deep(.text-h6) {
	position: absolute;
	top: 10px;
	left: 50%;
	transform: translateX(-50%);
}
</style>