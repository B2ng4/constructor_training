<template>
    <q-header 
        bordered 
        style="height: 10%;" 
        class="row items-center group-buttons text-black"
    >
        <span class="q-mx-md">Фильтры: </span>
        <q-select color="secondary" class="width-15" dense />
        <span class="q-mx-xl">Сортировка: </span>
        <q-select color="secondary" class="width-15" dense />
        <q-btn 
            color="secondary" 
            text-color="white" 
            class="q-ml-auto q-mr-xl" 
            label="Создать" 
            @click="showModal = true"
        />
    </q-header>
    <TraningModal v-model="showModal"></TraningModal>
</template>

<script>
import TraningModal from './TraningModal.vue';
export default {
    components: { TraningModal },
    data() {
        return {
            showModal: false
        }
    }
}
</script>

<style scoped>
.group-buttons {
    background-color: white;
    margin-top: 5%;
}

.width-15 {
    width: 15%;
}
</style>