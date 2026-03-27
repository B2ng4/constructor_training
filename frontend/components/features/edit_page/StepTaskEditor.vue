<template>
	<div v-if="store.selectedStep" class="step-task-editor">
		<div class="step-task-editor__bar">
			<q-icon name="assignment" size="18px" class="step-task-editor__icon" />
			<span class="step-task-editor__label">Задание</span>
			<q-space />
			<q-btn-toggle
				v-model="tab"
				flat
				dense
				no-caps
				toggle-color="primary"
				color="grey-7"
				:options="[
					{ label: 'Редактор', value: 'edit' },
					{ label: 'Просмотр', value: 'preview' },
				]"
			/>
		</div>
		<div v-show="tab === 'edit'" class="step-task-editor__pane step-task-editor__pane--grow">
			<rich-task-editor
				:model-value="selectedStep?.annotation ?? ''"
				@update:model-value="onAnnotationInput"
			/>
		</div>
		<div
			v-show="tab === 'preview'"
			class="step-task-editor__pane step-task-editor__preview task-html-body"
			v-html="previewHtml"
		/>
	</div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import { TrainingStepApi } from "@api";
import { useQuasar } from "quasar";
import { renderAnnotationToSafeHtml } from "@utils/renderAnnotationHtml.js";
import RichTaskEditor from "./RichTaskEditor.vue";

const api = new TrainingStepApi();
const store = useTrainingData();
const { selectedStep, trainingData } = storeToRefs(store);
const $q = useQuasar();

const tab = ref("edit");
const saveTimer = ref(null);

const previewHtml = computed(() =>
	renderAnnotationToSafeHtml(selectedStep.value?.annotation)
);

function onAnnotationInput(v) {
	if (!selectedStep.value) return;
	selectedStep.value.annotation = v ?? "";
	scheduleSave();
}

watch(
	() => selectedStep.value?.id,
	() => {
		tab.value = "edit";
		if (saveTimer.value) {
			clearTimeout(saveTimer.value);
			saveTimer.value = null;
		}
	}
);

function scheduleSave() {
	if (saveTimer.value) clearTimeout(saveTimer.value);
	saveTimer.value = setTimeout(() => {
		saveTimer.value = null;
		void persistAnnotation();
	}, 800);
}

async function persistAnnotation() {
	if (!trainingData.value?.uuid || !selectedStep.value?.id) return;
	const stepId = selectedStep.value.id;
	const text = (selectedStep.value.annotation ?? "").trim();
	try {
		await api.editStep(trainingData.value.uuid, stepId, {
			annotation: text || null,
		});
		if (selectedStep.value?.id === stepId) {
			selectedStep.value.annotation = text || null;
		}
	} catch {
		$q.notify({
			color: "negative",
			message: "Не удалось сохранить задание",
			position: "top",
		});
	}
}
</script>

<style scoped>
.step-task-editor {
	display: flex;
	flex-direction: column;
	min-height: 0;
	flex: 1;
	background: #fff;
	border-radius: 12px;
	border: 1px solid rgba(15, 23, 42, 0.08);
	overflow: hidden;
}

.step-task-editor__bar {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 12px;
	border-bottom: 1px solid rgba(0, 0, 0, 0.06);
	flex-shrink: 0;
}

.step-task-editor__icon {
	color: var(--q-primary);
	opacity: 0.85;
}

.step-task-editor__label {
	font-size: 13px;
	font-weight: 600;
	color: #0f172a;
}

.step-task-editor__pane {
	padding: 12px;
	overflow-y: auto;
	min-height: 0;
}

.step-task-editor__pane--grow {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.step-task-editor__pane--grow :deep(.rich-task-editor) {
	flex: 1;
	display: flex;
	flex-direction: column;
	min-height: 280px;
}

.step-task-editor__pane--grow :deep(.rich-task-editor__content) {
	flex: 1;
	max-height: none;
}

.step-task-editor__preview {
	font-size: 14px;
	line-height: 1.55;
	color: #334155;
}

.task-html-body :deep(p) {
	margin: 0 0 0.65em;
}

.task-html-body :deep(ul),
.task-html-body :deep(ol) {
	margin: 0.4em 0 0.65em;
	padding-left: 1.35em;
}

.task-html-body :deep(h2) {
	font-size: 1.2em;
	font-weight: 700;
	margin: 0.6em 0 0.35em;
}

.task-html-body :deep(h3) {
	font-size: 1.05em;
	font-weight: 700;
	margin: 0.5em 0 0.3em;
}
</style>
