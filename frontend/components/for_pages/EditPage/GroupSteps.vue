<template>
	<q-btn-dropdown
		class="absolute q-ma-lg wide-dropdown"
		style="z-index: 1"
		dropdown-icon="menu"
		color="primary"
	>
		<div class="q-pa-xs step-group column">
			<GroupStepsTreeSteps />
			<q-btn
				class="q-mt-md"
				@click="modal = !modal"
				label="Добавить шаг"
			></q-btn>
		</div>
	</q-btn-dropdown>
	<ModalCreateStep :step-count="steps.length" v-model="modal" />
</template>

<script setup>
import { computed, ref } from "vue";
import { useTrainingData } from "@store/editTraining.js";
import GroupStepsTreeSteps from "@components/for_pages/EditPage/GroupStepsTreeSteps.vue";
import ModalCreateStep from "@components/for_pages/EditPage/ModalCreateStep.vue";

const store = useTrainingData();
const modal = ref(false);

const steps = computed({
	get: () => store.steps,
	set: (value) => store.setSteps(value),
});
</script>

<style scoped>
.step-group {
	width: 100%;
	min-width: auto;
}
</style>
