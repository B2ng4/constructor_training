<template>
    <q-form
      @submit="onSubmit"
      @reset="onReset"
      class="q-gutter-md"
    >
        <div class="column justify-center items-center content-center">
            <q-input
                filled
                v-model="email"
                label="Логин *"
                lazy-rules
                :rules="[ val => val && val.length > 0 || 'Введите логин']"
            />
            <q-input
                filled
                type="password"
                v-model="password"
                label="Пароль *"
                lazy-rules
                :rules="[
                val => val !== null && val !== '' || 'Введите пароль',
                ]"
            />
                <q-btn label="Войти" type="submit" color="primary"/>
        </div>
    </q-form>
</template>

<script>
export default {
    name: 'Form',
    data() {
        return {
            email: '',
            password: ''
        }
    }
}
</script>

<style scoped>
</style>