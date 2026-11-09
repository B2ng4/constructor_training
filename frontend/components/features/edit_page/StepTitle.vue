<template>
	<div
		v-if="store.selectedStep"
		class="step-title-card cursor-pointer"
	>
		<q-tooltip anchor="top middle" :offset="[0, 8]">
			Краткое имя для списка шагов (не полное задание)
		</q-tooltip>
		<div class="step-title-text">
			<q-icon name="edit_note" size="18px" class="step-title-icon" />
			<span :class="{ 'text-grey-6': !selectedStep?.meta?.name }">
				{{ displayName }}
			</span>
		</div>
		<q-popup-edit
			v-model="metaName"
			auto-save
			@save="(value) => saveNewName(value)"
			v-slot="scope"
		>
			<q-input
				v-model="scope.value"
				dense
				autofocus
				counter
				:maxlength="100"
				placeholder="Краткое название шага"
				@keyup.enter="scope.set"
				@blur="scope.set"
			/>
		</q-popup-edit>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import { TrainingStepApi } from "@api";
import { useQuasar } from "quasar";

const api = new TrainingStepApi();
const store = useTrainingData();
const { selectedStep, trainingData } = storeToRefs(store);
const $q = useQuasar();

function stepDisplayName(step) {
	if (!step) return "";
	const n = (step.meta?.name ?? "").trim();
	if (n && n !== "Шаг без названия") return n;
	return `Шаг ${step.step_number ?? ""}`.trim();
}

const displayName = computed(() => stepDisplayName(selectedStep.value));
const metaName = computed({
	get: () => selectedStep.value?.meta?.name ?? "",
	set: (v) => {
		if (!selectedStep.value) return;
		if (!selectedStep.value.meta) selectedStep.value.meta = {};
		selectedStep.value.meta.name = v ?? "";
	},
});

const saveNewName = async (value) => {
	if (!trainingData.value?.uuid || !selectedStep.value?.id) return;
	const nameToSave = (value ?? selectedStep.value?.meta?.name ?? "").trim();
	if (!nameToSave && value === "") {
		await persistName(`Шаг ${selectedStep.value.step_number}`);
		return;
	}
	await persistName(nameToSave);
};

const persistName = async (nameToSave) => {
	try {
		await api.editStep(trainingData.value.uuid, selectedStep.value.id, {
			meta: { ...(selectedStep.value?.meta || {}), name: nameToSave },
		});
		if (!selectedStep.value.meta) selectedStep.value.meta = {};
		selectedStep.value.meta.name = nameToSave;
		$q.notify({
			color: "positive",
			message: "Название сохранено",
			position: "bottom-right",
			timeout: 1500,
		});
	} catch {
		$q.notify({
			color: "negative",
			message: "Не удалось сохранить",
			position: "top",
		});
	}
};
</script>

<style scoped>
.step-title-card {
	position: relative;
	z-index: 100;
	padding: 8px 18px;
	border-radius: 100px;
	transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	cursor: pointer;
}

.step-title-card:hover {
	transform: translateY(-2px) scale(1.02);
	box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(168, 85, 247, 0.2);
}

.step-title-text {
	display: flex;
	align-items: center;
	gap: 10px;
	font-size: 14px;
	font-weight: 600;
	color: #0f172a;
	letter-spacing: -0.01em;
}

.step-title-icon {
	color: #a855f7;
	opacity: 0.8;
}
</style>
