<template>
	<Tree :data="steps" item-key="id" nesting-key="steps" v-slot="{ item }">
		<div
			@click="store.selectStep(item)"
			class="tree-item-content cursor-pointer"
			:class="{active: item.id === store.selectedStep.id}"
		>
			<span>{{ item.meta.name }}</span>
		</div>
	</Tree>
</template>

<script setup>
import { Tree } from "@components/vue_dnd_kit_components/Tree";
import { watch } from "vue";
import { useTrainingData } from "@store/editTraining.js";

const store = useTrainingData();
const steps = store.steps;

watch(steps, (value) => {
	console.log(value);
});
</script>

<style scoped>
.active {
	background-color: rgba(202, 202, 202, 0.29);
}
</style>
