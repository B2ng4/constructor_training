<template>
	<div
		v-if="store.selectedStep"
		class="step-title-card absolute cursor-pointer"
	>
		<q-tooltip anchor="top middle" :offset="[0, 8]">
			Нажмите, чтобы изменить название шага
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
				placeholder="Название шага"
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

const displayName = computed(() => selectedStep.value?.meta?.name || "Шаг без названия");
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
		await persistName("Шаг без названия");
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
	top: 16px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 1;
	background: rgba(255, 255, 255, 0.85);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	padding: 8px 16px;
	border-radius: 12px;
	box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(255, 255, 255, 0.6);
	transition: box-shadow 0.2s ease;
}

.step-title-card:hover {
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.step-title-text {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 14px;
	font-weight: 500;
	color: #1a1a2e;
}

.step-title-icon {
	color: #9ca3af;
}
</style>
