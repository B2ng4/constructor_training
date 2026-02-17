<template>
	<div
		v-if="store.selectedStep"
		class="step-hint-card absolute cursor-pointer"
	>
		<q-tooltip anchor="bottom middle" :offset="[0, 8]">
			{{ selectedStep?.hint ? 'Редактировать подсказку' : 'Добавить подсказку для пользователя' }}
		</q-tooltip>
		<div class="step-hint-content">
			<q-icon 
				:name="selectedStep?.hint ? 'lightbulb' : 'lightbulb_outline'" 
				size="18px" 
				:class="['step-hint-icon', { 'has-hint': selectedStep?.hint }]" 
			/>
			<span :class="{ 'text-grey-5': !selectedStep?.hint }">
				{{ displayHint }}
			</span>
		</div>
		<q-popup-edit
			v-model="hintValue"
			auto-save
			@save="(value) => saveHint(value)"
			v-slot="scope"
		>
			<q-input
				v-model="scope.value"
				type="textarea"
				dense
				autofocus
				rows="3"
				counter
				:maxlength="200"
				placeholder="Например: Найдите кнопку в правом верхнем углу экрана"
				@keyup.ctrl.enter="scope.set"
			>
				<template v-slot:hint>
					Нажмите Ctrl+Enter для сохранения
				</template>
			</q-input>
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

const displayHint = computed(() => selectedStep.value?.hint || "Нет подсказки");

const hintValue = computed({
	get: () => selectedStep.value?.hint ?? "",
	set: (v) => {
		if (!selectedStep.value) return;
		selectedStep.value.hint = v ?? "";
	},
});

const saveHint = async (value) => {
	if (!trainingData.value?.uuid || !selectedStep.value?.id) return;
	const hintToSave = (value ?? selectedStep.value?.hint ?? "").trim();
	
	try {
		await api.editStep(trainingData.value.uuid, selectedStep.value.id, {
			hint: hintToSave || null,
		});
		selectedStep.value.hint = hintToSave || null;
		$q.notify({
			color: "positive",
			message: hintToSave ? "Подсказка сохранена" : "Подсказка удалена",
			position: "bottom-right",
			timeout: 1500,
		});
	} catch {
		$q.notify({
			color: "negative",
			message: "Не удалось сохранить подсказку",
			position: "top",
		});
	}
};
</script>

<style scoped>
.step-hint-card {
	top: 64px;
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
	transition: all 0.2s ease;
	max-width: 400px;
}

.step-hint-card:hover {
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
	background: rgba(255, 255, 255, 0.95);
}

.step-hint-content {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 13px;
	font-weight: 500;
	color: #1a1a2e;
}

.step-hint-icon {
	color: #9ca3af;
	transition: color 0.2s ease;
}

.step-hint-icon.has-hint {
	color: #f59e0b;
}
</style>
