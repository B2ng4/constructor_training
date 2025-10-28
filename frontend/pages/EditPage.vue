<template>
	<group-steps v-if="store.trainingData" />
	<vue-flow-component />
</template>

<script setup>
import VueFlowComponent from "@components/for_pages/EditPage/VueFlowComponent.vue";
import GroupSteps from "@components/for_pages/EditPage/GroupSteps.vue";
import { TrainingApi } from "@api/TrainingApi.js";
import { useRoute } from "vue-router";
import { onMounted } from "vue";
import { useTrainingData } from "@store/editTraining.js";

const trainingApi = new TrainingApi();
const route = useRoute();
const store = useTrainingData();

async function getTrainingData() {
	try {
		let response = await trainingApi.getTrainingByUuid(route.params.uuid);
		store.setTrainingData(response.data);
	} catch (e) {
		alert("Данные тренинга не найдены");
	}
}

onMounted(() => {
	getTrainingData();
});
</script>
