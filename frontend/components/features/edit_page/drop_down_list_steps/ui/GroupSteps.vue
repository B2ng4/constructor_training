<template>
	<q-btn-dropdown
		class="absolute q-ma-lg steps-dropdown"
		style="z-index: 1"
		dropdown-icon="menu"
		color="primary"
		content-class="steps-dropdown-content"
	>
		<div class="step-group column">
			<div class="step-group-header q-px-md q-pt-sm q-pb-xs" v-if="stepsArray.length > 0">
				<span class="text-caption text-grey-7 text-weight-medium">
					Шаги тренинга ({{ stepsArray.length }})
				</span>
			</div>
			<div class="step-group-list q-px-xs" v-if="stepsArray.length > 0">
				<GroupStepsTreeSteps class="q-mb-sm"/>
			</div>
			<q-separator v-if="stepsArray.length > 0" class="q-mx-sm" />
			<div class="q-pa-sm">
				<q-btn
					unelevated
					no-caps
					icon="add"
					color="primary"
					class="full-width"
					@click="modal = !modal"
					label="Добавить шаг"
				>
					<q-tooltip anchor="bottom middle" :offset="[0, 8]">
						Загрузить скриншоты или видео для новых шагов
					</q-tooltip>
				</q-btn>
			</div>
		</div>
	</q-btn-dropdown>
	<ModalCreateStep v-model="modal" />
</template>

<script setup>
import { computed, ref } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import { GroupStepsTreeSteps } from "@components/features/edit_page/drop_down_list_steps";
import ModalCreateStep from "@components/features/edit_page/ModalCreateStep.vue";

const store = useTrainingData();
const { steps } = storeToRefs(store);
const modal = ref(false);

const stepsArray = computed(() => (Array.isArray(steps.value) ? steps.value : []));
</script>

<style scoped>
.step-group {
	width: 100%;
	min-width: 280px;
}

.step-group-list {
	max-height: 400px;
	overflow-y: auto;
}
</style>

<style>
.steps-dropdown-content {
	border-radius: 12px !important;
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.14) !important;
	overflow: hidden;
}
</style>
