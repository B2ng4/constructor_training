<template>
    <div class="container">
        <div class="left column justify-center items-center content-center">
            <img 
                src="@assets/img/signin-weave.svg" 
                class="absolute" 
                alt=""
            >
            <h3 class="text-blue-grey-1 text-weight-bolder">Конструктор Тренингов</h3>
            <h6 class="text-blue-grey-1">У вас нет аккаунта?</h6>
                <q-btn 
                    outline 
                    rounded
                    @click="show = true"
                    color="blue-grey-1" 
                    label="Регистрация" 
                    class="q-btn--large"
                />
        </div>
    </div>
    <RegistrationModal :show="show" @close="show = false"/>
</template>

<script>
import RegistrationModal from '@components/for_pages/loginPage/RegistrationModal.vue';
export default {
    name: 'Layout',
    components: {RegistrationModal},
    data() {
        return {
            show: false,
        }
    }
}
</script>

<style scoped>
.container {
    height: 100vh;
    width: 50%;
    display: flex; 
}

.left {
    background-color: #2781D9;
    height: 100%;
    width: 100%;
    box-sizing: border-box;
    border-radius: 0 20% 20% 0;
}

color-text {
    color: #F8F9FB;
}

h6 {
    margin-bottom: 2%;
    margin-top: 2%;
}

h3 {
    margin-bottom: 2%;
}

.q-btn--large {
    padding: 10px 20px;
    font-size: 16px;
}

.absolute {
    top: 0%;
    left: 0%;
    width: 40%;
}
</style>