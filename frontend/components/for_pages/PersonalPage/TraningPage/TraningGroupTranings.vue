<template>
    <div class="row q-gutter-md q-ma-xl">
        <q-card class="my-card" flat bordered v-for="f in 20">
            <q-card-section>
                <div class="text-overline text-orange-9">Какая-то надпись</div>
                <div class="text-h5 q-mt-sm q-mb-xs">Название</div>
                <div class="text-caption text-grey">
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </div>
            </q-card-section>
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

.my-card:hover {
    background-color: rgba(0, 0, 0, 0.095);
    transition: all 0.1s ease-out;
    transform: scale(1.02);
    cursor: pointer;
}
</style>