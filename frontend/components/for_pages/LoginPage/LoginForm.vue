<template>
    <div class="container">
        <BaseCard class="card text-blue-grey-8 shadow-24" width="400px">
            <template v-slot:title>
                <div class="text-white column content-center items-center">
                    <h5 class="q-mb-xs">Добро пожаловать</h5>
                    <div>Вход</div>
                    <div>Нет аккаунта? <router-link class="text-white" to="/registration">Регистрация</router-link></div>
                </div>
            </template>
            <template v-slot:body>
                <div class="column justify-center items-center content-center">
                    <q-input
                        filled
                        label-color="white"
                        color="white"
                        v-model="email"
                        label="Логин *"
                        lazy-rules
                        class="full-width"
                        input-style='color: white'
                    />
                    <q-input
                        filled
                        type="password"
                        label-color="white"
                        color="white"
                        v-model="password"
                        label="Пароль *"
                        lazy-rules
                        class="full-width q-mt-lg"
                        input-style='color: white'
                    />
                        <q-btn 
                            outline 
                            rounded
                            class="q-mt-lg full-width" 
                            color="white" 
                            @click="login()"
                            >
                            <q-spinner-bars
                                v-if="loader === true"
                                color="white"
                                size="2em"
                             />
                             <span v-else>Войти</span>
                        </q-btn>
                </div>
            </template>
        </BaseCard> 
    </div>
</template>

<script>
import axios from 'axios';
import BaseCard from '@components/BaseComponents/BaseCard.vue';
export default {
    name: 'LoginForm',
    components: {BaseCard},
    data() {
        return {
            email: '',
            password: '',
            loader: false,
        }
    },
    methods: {
        async login() {
            this.loader = true;
            let form = new FormData();
            form.set('username', this.email);
            form.set('password', this.password);
            axios.post(`${__BASE__URL__}/auth/login`, form)
                .then((response) => {
                    localStorage.setItem('tokenAuth', response.data.access_token);
                    this.$router.push('/personal');
                })
                .catch(() => {
                    this.$q.notify({ position: 'top', type: 'negative', message: 'Произошла ошибка!' });
                })
                .finally(() => {
                    this.loader = false;
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

.my-card {
    background-color: #6274F8;
    border-radius: 5%;
}

.my-card :deep(.text-h6) {
	position: absolute;
	top: 10px;
	left: 50%;
	transform: translateX(-50%);
}
</style>