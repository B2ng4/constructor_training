<template>
    <q-btn rounded color="white text-black" style="width: auto;">
        <q-icon class="q-mr-xs" name="person" />
        {{ first_name }}
        <q-menu fit>
            <q-list style="min-width: 100px">
                <q-item clickable>
                    <q-item-section>Перейти в профиль</q-item-section>
                </q-item>
            </q-list>
        </q-menu>
    </q-btn>
</template>

<script>
import { useUserStore } from '../../../../store/userData';
export default {
    name: 'UserCard',
    data() {
        return {
            first_name: ''
        }
    },
    mounted() {
        this.first_name = useUserStore().getName;
    }
}
</script>

<style scoped>

</style>