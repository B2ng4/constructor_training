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
                        <q-btn label="Войти" class="q-mt-lg full-width" color="primary"/>
                        <vkButton></vkButton>
                </div>
            </template>
        </BaseCard> 
    </div>
</template>

<script>
import BaseCard from '../../BaseComponents/BaseCard.vue';
import vkButton from './vkButton.vue';
export default {
    name: 'Form',
    components: {BaseCard, vkButton},
    data() {
        return {
            email: '',
            password: ''
        }
    },
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