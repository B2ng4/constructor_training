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
            <div class="group_button_layout column">
                <q-btn
                    flat 
                    v-for="nav in buttonLeftPanel"
                    :key="nav.name"
                    class="q-pa-md row items-start"
                >
                    <q-icon :name="nav.icon" class="q-ml-lg"/>
                    <span class="q-ml-md">{{ nav.name }}</span>
                </q-btn>
            </div>
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
    components: {UserCard},
    data() {
        return {
            buttonLeftPanel: [
                {
                    'name': 'Главная',
                    'icon': 'home_outline'
                },
                {
                    'name': 'Библиотека',
                    'icon': 'language'
                },
                {
                    'name': 'Тренинги',
                    'icon': 'list_alt'
                },
                {
                    'name': 'Поддержка',
                    'icon': 'info'
                }
            ]
        }
    }
}
</script>

<style scoped>
.q-header {
    background-color: white;
}

.group_button_layout {
    margin-top: 25%;
    color: #808080;
}
</style>

