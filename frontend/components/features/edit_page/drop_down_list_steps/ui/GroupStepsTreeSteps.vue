<template>
	<Tree :data="steps" item-key="id" nesting-key="steps" v-slot="{ item }">
		<div
			@click="store.selectStep(item)"
			class="tree-item-content cursor-pointer"
			:class="{ active: item.id === store.selectedStep.id }"
		>
			<span>{{ item.meta.name }}</span>
		</div>
	</Tree>
</template>

<script setup>
import { Tree } from "@components/vue_dnd_kit_components/tree";
import { watchDebounced } from "@vueuse/core";
import { useTrainingData } from "@store/editTraining.js";
import { TrainingStepApi } from "@api";
import { computed } from "vue";
import { useQuasar } from "quasar";


const $q = useQuasar();
const store = useTrainingData();
const steps = store.steps;
const api = new TrainingStepApi();

const changeSteps = computed(() => {
	return steps.map((el, index) => {
		return {
			id: el.id,
			step_number: index + 1
		};
	});
});

watchDebounced(
	steps,
	async () => {
		await api.reorderSteps(store.trainingData.uuid, { steps: changeSteps.value });
		$q.notify({
			color: 'positive',
			message: 'Порядок изменен',
			position: 'bottom-right',
		});
	},
	{ debounce: 500, maxWait: 1000 },
);
</script>

<style scoped>
.active {
	background-color: rgba(202, 202, 202, 0.29);
}
</style>
