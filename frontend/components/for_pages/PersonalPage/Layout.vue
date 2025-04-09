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
            <div class="group_button_layout">
                <router-link class="custom-nav-link column" v-for="nav in buttonLeftPanel"  :to="nav.url" active-class="active-nav-link">
                    <q-btn
                        flat
                        :key="nav.name"
                        class="q-pa-md row items-start full-width"
                    >
                        <q-icon :name="nav.icon" class="q-ml-lg"/>
                        <span class="q-ml-md">{{ nav.name }}</span>
                    </q-btn>
                </router-link>
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
                    'icon': 'home_outline',
                    'url': '/personal/home'
                },
                {
                    'name': 'Библиотека',
                    'icon': 'language',
                    'url': '/personal/library'
                },
                {
                    'name': 'Тренинги',
                    'icon': 'list_alt',
                    'url': '/personal/traning'
                },
                {
                    'name': 'Поддержка',
                    'icon': 'info',
                    'url': '/personal/help'
                }
            ]
        }
    },
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

.custom-nav-link {
    color: #808080;
    text-decoration: none;
}

.active-nav-link {
    background-color: #FAFAFC;
    color: #5064F7;
    border-left: 5px solid #5064F7;
}
</style>

