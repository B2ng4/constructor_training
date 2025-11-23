<template>
	<div
		class="cursor-pointer absolute q-ma-lg"
		style="z-index: 1; left: 50%; transform: translateX(-50%)"
	>
		<h4 class="q-ma-none">
			{{ store.selectedStep.meta.name }}
		</h4>
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
			/>
		</q-popup-edit>
	</div>
</template>

<script setup>
import { useTrainingData } from "@store/editTraining.js";
import { TrainingApi } from "@api/TrainingApi.js";
import {watch} from "vue";
import {useRoute} from "vue-router";

const api = new TrainingApi();
const store = useTrainingData();
const route = useRoute();

watch(store.selectedStep, (n) => {
	if (n) {
		setTimeout(() => {
			console.log(n);
		}, 3000)
	}
})
</script>

<style scoped></style>
