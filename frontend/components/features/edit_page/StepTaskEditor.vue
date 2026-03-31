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
			@click="onPreviewClick"
		></div>
	</div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import { TrainingStepApi } from "@api";
import { useQuasar } from "quasar";
import { renderAnnotationToSafeHtml } from "@utils/renderAnnotationHtml.js";
import RichTaskEditor from "./RichTaskEditor.vue";

const api = new TrainingStepApi();
const store = useTrainingData();
const { selectedStep, trainingData, steps } = storeToRefs(store);
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

async function copyCodeFromEvent(e) {
	const btn = e?.target?.closest?.(".task-code-copy-btn");
	if (!btn) return false;
	const wrap = btn.closest(".task-code-wrap");
	const codeEl = wrap?.querySelector?.("pre code");
	const text = codeEl?.textContent ?? "";
	if (!text.trim()) return true;
	try {
		if (navigator?.clipboard?.writeText) {
			await navigator.clipboard.writeText(text);
		} else {
			const ta = document.createElement("textarea");
			ta.value = text;
			ta.style.position = "fixed";
			ta.style.left = "-9999px";
			document.body.appendChild(ta);
			ta.select();
			document.execCommand("copy");
			ta.remove();
		}
		$q.notify({ color: "positive", message: "Код скопирован", position: "top", timeout: 900 });
	} catch {
		$q.notify({ color: "negative", message: "Не удалось скопировать код", position: "top" });
	}
	return true;
}

function onPreviewClick(e) {
	void copyCodeFromEvent(e);
}

watch(
	() => selectedStep.value?.id,
	async (newId, oldId) => {
		tab.value = "edit";
		if (saveTimer.value) {
			clearTimeout(saveTimer.value);
			saveTimer.value = null;
		}
		if (oldId != null && newId !== oldId) {
			await persistAnnotationForStepId(oldId);
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
	await persistAnnotationForStepId(selectedStep.value.id);
}

/** Сохранить текст задания для шага по id (объект шага в массиве store, не только selected) */
async function persistAnnotationForStepId(stepId) {
	if (!trainingData.value?.uuid || !stepId) return;
	const step = steps.value?.find((s) => s.id === stepId);
	if (!step) return;
	const text = (step.annotation ?? "").trim();
	try {
		await api.editStep(trainingData.value.uuid, stepId, {
			annotation: text || null,
		});
		step.annotation = text || null;
	} catch {
		$q.notify({
			color: "negative",
			message: "Не удалось сохранить задание",
			position: "top",
		});
	}
}

onBeforeUnmount(() => {
	if (saveTimer.value) {
		clearTimeout(saveTimer.value);
		saveTimer.value = null;
	}
	if (selectedStep.value?.id) {
		void persistAnnotationForStepId(selectedStep.value.id);
	}
});
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
	font-size: 15px;
	font-weight: 700;
	color: #0f172a;
	letter-spacing: -0.01em;
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
	font-size: 18px;
	line-height: 1.65;
	color: #0f172a;
	letter-spacing: 0.01em;
}

.task-html-body :deep(p) {
	margin: 0 0 0.7em;
}

.task-html-body :deep(ul),
.task-html-body :deep(ol) {
	margin: 0.45em 0 0.7em;
	padding-left: 1.4em;
}

.task-html-body :deep(h2) {
	font-size: 1.35em;
	font-weight: 700;
	margin: 0.55em 0 0.35em;
	color: #0f172a;
}

.task-html-body :deep(h3) {
	font-size: 1.2em;
	font-weight: 700;
	margin: 0.45em 0 0.3em;
	color: #0f172a;
}

.task-html-body :deep(.task-code-wrap) {
	margin: 0.6em 0 0.9em;
	border: 1px solid rgba(15, 23, 42, 0.15);
	border-radius: 10px;
	overflow: hidden;
	background: #0f172a;
}

.task-html-body :deep(.task-code-head) {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 6px 10px;
	background: rgba(2, 6, 23, 0.9);
	border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}

.task-html-body :deep(.task-code-lang) {
	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
	font-size: 12px;
	line-height: 1.2;
	color: #cbd5e1;
	text-transform: lowercase;
	letter-spacing: 0.03em;
}

.task-html-body :deep(.task-code-copy-btn) {
	border: 0;
	background: transparent;
	color: #e2e8f0;
	cursor: pointer;
	font-family: "Material Symbols Outlined", "Material Icons", sans-serif;
	font-size: 18px;
	line-height: 1;
	padding: 2px 4px;
	border-radius: 4px;
}

.task-html-body :deep(.task-code-copy-btn:hover) {
	background: rgba(148, 163, 184, 0.25);
}
</style>
