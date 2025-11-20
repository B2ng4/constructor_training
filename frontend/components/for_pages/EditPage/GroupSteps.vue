<template>
	<q-btn-dropdown
		class="absolute q-ma-lg wide-dropdown"
		style="z-index: 1"
		dropdown-icon="menu"
		color="secondary"
	>
		<div class="q-pa-xs step-group column">
			<GroupStepsTreeSteps :steps="steps"/>
			<q-btn class="q-mt-md" @click="addStep" label="Добавить шаг"></q-btn>
		</div>
	</q-btn-dropdown>
</template>

<script setup>
import { computed } from "vue";
import { useTrainingData } from "@store/editTraining.js";
import { TrainingApi } from "@api/TrainingApi.js";
import { useRoute } from "vue-router";
import GroupStepsTreeSteps from "@components/for_pages/EditPage/GroupStepsTreeSteps.vue";


const api = new TrainingApi();
const store = useTrainingData();
const route = useRoute();

const steps = computed({
	get: () => store.steps,
	set: (value) => store.setSteps(value),
});

async function addStep() {
	try {
		let payload = {
				step_number: steps.value.length + 1,
				meta: {name: 'Шаг без названия'}
		};
		await api.addStep(route.params.uuid, payload);
	} catch (e) {
		alert('Ошибка добавления нового шага');
	}
}
</script>

<style scoped>
.step-group {
	width: 100%;
	min-width: auto;
}
</style>
