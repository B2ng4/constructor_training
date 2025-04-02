<template>
    <q-btn rounded color="white text-black" style="width: auto;">
        <q-icon class="q-mr-xs" name="person" />
        Имя юзера
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
export default {
    name: 'UserCard'
}
</script>

<style scoped>

</style>