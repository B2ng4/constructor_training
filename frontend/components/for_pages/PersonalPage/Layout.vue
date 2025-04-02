<template>
    <q-layout view="lHh lpR fFf">
        <!-- Вверхняя часть -->
        <q-header bordered style="height: 10%;" class="row items-center">
            <q-toolbar>
                <UserCard class="q-ml-auto q-mr-xl"/>
            </q-toolbar>
        </q-header>
        <!-- Левая панель -->
        <q-drawer show-if-above side="left" bordered>
            
        </q-drawer>
        <!-- Контейнер в котором отрисовка страницы -->
        <q-page-container>
            <router-view />
        </q-page-container>
    </q-layout>
</template>

<script>
import UserCard from '@components/for_pages/PersonalPage/for_header/UserCard.vue';
export default {
    name: 'Layout',
    components: {UserCard}
}
</script>

<style scoped>
.q-header {
    background-color: white;
}
</style>

