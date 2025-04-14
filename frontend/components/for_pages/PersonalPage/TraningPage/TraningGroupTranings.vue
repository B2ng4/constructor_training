<template>
    <div class="row q-gutter-md q-ma-xl">
        <q-card class="my-card shadow-5" flat bordered>
            <q-img
                src="https://cdn.quasar.dev/img/parallax2.jpg"
            />
            <q-card-section>
                <div class="text-overline text-orange-9">Какая-то надпись</div>
                <div class="text-h5 q-mt-sm q-mb-xs">Название</div>
                <div class="text-caption text-grey">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </div>
            </q-card-section>
            <q-card-actions>
                <q-btn flat color="primary" label="Редактировать" />
                <q-btn flat color="negative" label="Удалить" />
                <q-space />
            </q-card-actions>
        </q-card>
    </div>
</template>

<script>
export default {
    
}
</script>

<style scoped>
.my-card {
    width: 100%;
    max-width: 350px;
    border-radius: 5%;
}
</style>