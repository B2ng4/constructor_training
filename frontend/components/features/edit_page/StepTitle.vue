<template>
	<div class="cursor-pointer absolute q-ma-lg card shadow-2">
		<h6 class="q-ma-none">
			{{ store.selectedStep.meta.name }}
		</h6>
		<q-popup-edit
			v-model="store.selectedStep.meta.name"
			auto-save
			v-slot="scope"
		>
			<q-input
				v-model="scope.value"
				dense
				autofocus
				counter
				@keyup.enter="scope.set"
				@change="saveNewName"
			/>
		</q-popup-edit>
	</div>
</template>

<script setup>
import { useTrainingData } from "@store/editTraining.js";
import { TrainingStepApi } from "@api";
import { useQuasar } from "quasar";

const api = new TrainingStepApi();
const store = useTrainingData();
const $q = useQuasar();

const saveNewName = async () => {
	setTimeout(async () => {
		await api.editStep(store.trainingData.uuid, store.selectedStep.id, {
			meta: {
				name: store.selectedStep.meta.name,
			},
		});
		$q.notify({
			color: 'positive',
			message: 'Название изменено',
			position: 'bottom-right',
		});
	}, 2000);
};
</script>

<style scoped>
.card {
	background: #ffffff;
	padding: 10px;
	border-radius: 6px;
	z-index: 1;
	left: 50%;
	transform: translateX(-50%);
}
</style>
