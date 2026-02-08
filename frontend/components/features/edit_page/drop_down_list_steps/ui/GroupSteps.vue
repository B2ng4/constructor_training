<template>
	<q-btn-dropdown
		class="absolute q-ma-lg wide-dropdown"
		style="z-index: 1"
		dropdown-icon="menu"
		color="primary"
	>
		<div class="q-pa-xs step-group column">
			<GroupStepsTreeSteps v-if="steps.length > 0" class="q-mb-md"/>
			<q-btn unelevated no-caps @click="modal = !modal" label="Добавить шаг" />
		</div>
	</q-btn-dropdown>
	<ModalCreateStep v-model="modal" />
</template>

<script setup>
import { computed, ref } from "vue";
import { useTrainingData } from "@store/editTraining.js";
import { GroupStepsTreeSteps } from "@components/features/edit_page/drop_down_list_steps";
import ModalCreateStep from "@components/features/edit_page/ModalCreateStep.vue";

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
