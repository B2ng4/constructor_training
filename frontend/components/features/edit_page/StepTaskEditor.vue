<template>
	<div v-if="store.selectedStep" class="step-task-editor glass-panel">
		<header class="step-task-editor__bar">
			<div class="step-task-editor__bar-row">
				<div class="step-task-editor__title">
					<q-icon
						name="auto_awesome"
						size="20px"
						class="step-task-editor__icon magic-stream-text"
						v-if="isImproving || isGeneratingTTS"
					/>
					<q-icon name="assignment" size="18px" class="step-task-editor__icon" v-else />
					<span class="step-task-editor__label">Задание</span>
				</div>

				<q-space />

				<div class="step-task-editor__actions">
					<q-btn
						flat
						round
						dense
						color="primary"
						icon="auto_awesome"
						:loading="isImproving || isGeneratingTTS"
					>
					<q-tooltip>AI Лаборатория</q-tooltip>
					<q-menu transition-show="jump-down" transition-hide="jump-up" class="glass-panel overflow-hidden" style="border-radius: 12px">
						<q-list style="min-width: 220px" class="q-py-sm">
							<q-item clickable v-ripple @click="improveWithAI('simplify')">
								<q-item-section avatar><q-icon name="child_care" size="18px" /></q-item-section>
								<q-item-section>Упростить</q-item-section>
							</q-item>
							<q-item clickable v-ripple @click="improveWithAI('technical')">
								<q-item-section avatar><q-icon name="terminal" size="18px" /></q-item-section>
								<q-item-section>Технический стиль</q-item-section>
							</q-item>
							<q-item clickable v-ripple @click="improveWithAI('shorten')">
								<q-item-section avatar><q-icon name="compress" size="18px" /></q-item-section>
								<q-item-section>Сократить</q-item-section>
							</q-item>
							<q-separator />
							<q-item clickable v-ripple @click="generateTTS">
								<q-item-section avatar><q-icon name="record_voice_over" size="18px" /></q-item-section>
								<q-item-section>Озвучить AI</q-item-section>
							</q-item>
						</q-list>
					</q-menu>
					</q-btn>
				</div>
			</div>

			<q-tabs
				v-model="tab"
				dense
				class="step-task-editor__tabs text-grey-7"
				active-color="primary"
				indicator-color="primary"
				narrow-indicator
				no-caps
				stretch
			>
				<q-tab name="edit" label="Редактор" />
				<q-tab name="preview" label="Превью" />
				<q-tab name="hint" label="Подсказка" />
			</q-tabs>
		</header>

		<div class="step-task-editor__content-area">
				<div
					v-show="tab === 'edit'"
					class="step-task-editor__pane step-task-editor__pane--grow"
					:class="{ 'magic-border-glow': isImproving || isGeneratingTTS }"
				>
				<rich-task-editor
					:class="{ 'is-improving': isImproving }"
					:model-value="selectedStep?.annotation ?? ''"
					@update:model-value="onAnnotationInput"
				/>
			</div>
			<div
				v-show="tab === 'preview'"
				class="step-task-editor__pane step-task-editor__preview task-html-body"
				:class="{ 'magic-border-glow': isImproving || isGeneratingTTS }"
				v-html="previewHtml"
				@click="onPreviewClick"
			></div>
			<div v-show="tab === 'hint'" class="step-task-editor__pane step-task-editor__pane--grow">
				<p class="text-caption text-grey-7 q-mb-sm q-mt-none">
					Показывается ученику при включённых подсказках, если он ошибся или застрял.
				</p>
				<q-input
					:model-value="selectedStep?.hint ?? ''"
					type="textarea"
					autogrow
					outlined
					dense
					placeholder="Например: нажмите кнопку «Войти» в правом верхнем углу"
					@update:model-value="onHintInput"
				/>
			</div>
		</div>

		<!-- Кастомный Аудио-плеер -->
		<div v-if="selectedStep?.audio_url" class="premium-audio-player">
			<q-btn
				flat
				round
				dense
				:icon="isAudioPlaying ? 'pause' : 'play_arrow'"
				color="indigo"
				class="audio-play-btn"
				@click="toggleAudio"
			/>
			<div class="audio-progress-wrap">
				<div class="audio-progress-bar">
					<div class="audio-progress-fill" :style="{ width: audioProgress + '%' }" />
				</div>
			</div>
			<span class="audio-time">{{ formatAudioTime }}</span>
			<audio
				ref="audioRef"
				:src="selectedStep.audio_url"
				@timeupdate="onAudioTimeUpdate"
				@ended="onAudioEnded"
				style="display: none"
			/>
		</div>
	</div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import { TrainingStepApi, TrainingApi } from "@api";
import { useQuasar } from "quasar";
import { renderAnnotationToSafeHtml } from "@utils/renderAnnotationHtml.js";
import { renderMarkdownToSafeHtml } from "@utils/renderMarkdown.js";
import RichTaskEditor from "./RichTaskEditor.vue";
import { trainingEvents } from "@utils/eventBus.js";
import { useEditorSaveStatus } from "@composables/useEditorSaveStatus.js";

const api = new TrainingStepApi();
const tApi = new TrainingApi();
const store = useTrainingData();
const { selectedStep, trainingData, steps } = storeToRefs(store);
const $q = useQuasar();
const { markDirty, markSaving, markSaved, markError } = useEditorSaveStatus();

const tab = ref("edit");
const saveTimer = ref(null);
const hintSaveTimer = ref(null);
const isImproving = ref(false);
const isGeneratingTTS = ref(false);

// Audio State
const audioRef = ref(null);
const isAudioPlaying = ref(false);
const audioProgress = ref(0);
const audioCurrentTime = ref(0);

const formatAudioTime = computed(() => {
	const min = Math.floor(audioCurrentTime.value / 60);
	const sec = Math.floor(audioCurrentTime.value % 60);
	return `${min}:${sec.toString().padStart(2, "0")}`;
});

function onAudioTimeUpdate() {
	if (!audioRef.value) return;
	audioCurrentTime.value = audioRef.value.currentTime;
	audioProgress.value = (audioRef.value.currentTime / audioRef.value.duration) * 100;
}

function onAudioEnded() {
	isAudioPlaying.value = false;
	audioProgress.value = 0;
}

function toggleAudio() {
	if (!audioRef.value) return;
	if (isAudioPlaying.value) {
		audioRef.value.pause();
	} else {
		audioRef.value.play();
	}
	isAudioPlaying.value = !isAudioPlaying.value;
}

const previewHtml = computed(() =>
	renderAnnotationToSafeHtml(selectedStep.value?.annotation)
);

function onAnnotationInput(v) {
	if (!selectedStep.value) return;
	selectedStep.value.annotation = v ?? "";
	markDirty();
	scheduleSave();
}

function onHintInput(v) {
	if (!selectedStep.value) return;
	selectedStep.value.hint = v ?? "";
	markDirty();
	scheduleHintSave();
}

const improveWithAI = async (variant = "general") => {
	if (!selectedStep.value?.annotation) return;
	isImproving.value = true;
	
	const originalText = selectedStep.value.annotation;
	let accumulatedMarkdown = "";
	
	const prompts = {
		simplify: "Упрости этот текст, чтобы он был понятен пятилетнему ребенку, но сохрани суть задачи.",
		technical: "Перепиши этот текст в строго профессиональном, техническом стиле.",
		shorten: "Максимально сократи текст, оставив только самое важное действие.",
		general: "Улучши этот текст, сделай его более вовлекающим и понятным."
	};

	try {
		await tApi.streamRewriteTaskText(originalText, (chunk) => {
			accumulatedMarkdown += chunk;
			selectedStep.value.annotation = renderMarkdownToSafeHtml(accumulatedMarkdown);
		}, prompts[variant]);
		scheduleSave();
		$q.notify({
			color: "positive",
			message: "Текст обновлен с помощью AI",
			position: "bottom-right",
			icon: "auto_awesome"
		});
	} catch {
		$q.notify({ color: "negative", message: "Ошибка AI", position: "top" });
		selectedStep.value.annotation = originalText;
	} finally {
		isImproving.value = false;
	}
};

const generateTTS = async () => {
	if (!selectedStep.value?.annotation?.trim()) return;
	if (!trainingData.value?.uuid || !selectedStep.value?.id) return;
	isGeneratingTTS.value = true;
	try {
		const response = await tApi.generateStepTTS(
			trainingData.value.uuid,
			selectedStep.value.id
		);
		if (response.data?.audio_url) {
			selectedStep.value.audio_url = response.data.audio_url;
			// Синхронизируем в массиве шагов
			const stepInList = steps.value?.find(s => s.id === selectedStep.value.id);
			if (stepInList) stepInList.audio_url = response.data.audio_url;
		}
		$q.notify({
			color: "positive",
			message: "Озвучка сгенерирована!",
			position: "bottom-right",
			icon: "headphones"
		});
	} catch {
		$q.notify({
			color: "negative",
			message: "Ошибка при генерации озвучки",
			position: "top"
		});
	} finally {
		isGeneratingTTS.value = false;
	}
};

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
		if (hintSaveTimer.value) {
			clearTimeout(hintSaveTimer.value);
			hintSaveTimer.value = null;
		}
		if (oldId != null && newId !== oldId) {
			await persistAnnotationForStepId(oldId);
			await persistHintForStepId(oldId);
		}
		// Reset Audio
		isAudioPlaying.value = false;
		audioProgress.value = 0;
		audioCurrentTime.value = 0;
	}
);

function scheduleSave() {
	if (saveTimer.value) clearTimeout(saveTimer.value);
	saveTimer.value = setTimeout(() => {
		saveTimer.value = null;
		void persistAnnotation();
	}, 800);
}

function scheduleHintSave() {
	if (hintSaveTimer.value) clearTimeout(hintSaveTimer.value);
	hintSaveTimer.value = setTimeout(() => {
		hintSaveTimer.value = null;
		void persistHint();
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
	markSaving();
	try {
		await api.editStep(trainingData.value.uuid, stepId, {
			annotation: text || null,
		});
		step.annotation = text || null;
		markSaved();
	} catch {
		markError("annotation");
		$q.notify({
			color: "negative",
			message: "Не удалось сохранить задание",
			position: "top",
		});
	}
}

async function persistHintForStepId(stepId) {
	if (!trainingData.value?.uuid || !stepId) return;
	const step = steps.value?.find((s) => s.id === stepId);
	if (!step) return;
	const text = (step.hint ?? "").trim();
	markSaving();
	try {
		await api.editStep(trainingData.value.uuid, stepId, {
			hint: text || null,
		});
		step.hint = text || null;
		markSaved();
	} catch {
		markError("hint");
		$q.notify({
			color: "negative",
			message: "Не удалось сохранить подсказку",
			position: "top",
		});
	}
}

async function persistHint() {
	if (!trainingData.value?.uuid || !selectedStep.value?.id) return;
	await persistHintForStepId(selectedStep.value.id);
}

onBeforeUnmount(() => {
	if (saveTimer.value) {
		clearTimeout(saveTimer.value);
		saveTimer.value = null;
	}
	if (hintSaveTimer.value) {
		clearTimeout(hintSaveTimer.value);
		hintSaveTimer.value = null;
	}
	if (selectedStep.value?.id) {
		void persistAnnotationForStepId(selectedStep.value.id);
		void persistHintForStepId(selectedStep.value.id);
	}
});

trainingEvents.forceSave.on(() => {
	if (selectedStep.value?.id) {
		void persistAnnotationForStepId(selectedStep.value.id);
		void persistHintForStepId(selectedStep.value.id);
	}
});

// Слушаем события из других компонентов (например, из Floating AI Bar)
trainingEvents.improveText.on(() => {
	improveWithAI();
});

trainingEvents.generateTTS.on(() => {
	generateTTS();
});
</script>

<style scoped>
.step-task-editor {
	display: flex;
	flex-direction: column;
	min-height: 0;
	flex: 1;
	overflow: hidden;
	transition: all 0.4s var(--anim-ease-out);
}

.step-task-editor__bar {
	display: flex;
	flex-direction: column;
	padding: 12px 16px 0;
	background: rgba(255, 255, 255, 0.4);
	backdrop-filter: blur(10px);
	border-bottom: 1px solid rgba(15, 23, 42, 0.06);
	flex-shrink: 0;
}

.step-task-editor__bar-row {
	display: flex;
	align-items: center;
	gap: 12px;
	width: 100%;
}

.step-task-editor__tabs {
	width: 100%;
	margin-top: 4px;
}

.step-task-editor__tabs :deep(.q-tab) {
	flex: 1;
	min-width: 0;
}

.step-task-editor__title {
	display: flex;
	align-items: center;
	gap: 8px;
}

.step-task-editor__label {
	font-size: 15px;
	font-weight: 700;
	color: #1e293b;
	letter-spacing: -0.01em;
}

.step-task-editor__content-area {
	flex: 1;
	min-height: 0;
	display: flex;
	flex-direction: column;
	background: rgba(255, 255, 255, 0.2);
}

.step-task-editor__pane {
	padding: 16px;
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
	background: transparent;
	border: none;
}

/* Premium Audio Player */
.premium-audio-player {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 12px 16px;
	background: rgba(255, 255, 255, 0.6);
	backdrop-filter: blur(20px);
	border-top: 1px solid rgba(15, 23, 42, 0.08);
	flex-shrink: 0;
	z-index: 5;
}

.audio-progress-wrap {
	flex: 1;
	height: 6px;
	background: rgba(15, 23, 42, 0.08);
	border-radius: 10px;
	position: relative;
	overflow: hidden;
}

.audio-progress-bar {
	width: 100%;
	height: 100%;
}

.audio-progress-fill {
	height: 100%;
	background: var(--q-primary);
	border-radius: 10px;
	transition: width 0.15s linear;
}

.audio-time {
	font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
	font-size: 12px;
	font-weight: 600;
	color: #64748b;
	min-width: 38px;
	text-align: right;
}

.step-task-editor__preview {
	font-size: 18px;
	line-height: 1.65;
	color: #1e293b;
}

.task-html-body :deep(h2) {
	font-size: 1.5em;
	font-weight: 800;
	color: #0f172a;
	margin-top: 1.2em;
	margin-bottom: 0.6em;
}

.task-html-body :deep(.task-code-wrap) {
	margin: 1.2em 0;
	background: #0f172a;
	border-radius: 12px;
	overflow: hidden;
	box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.task-html-body :deep(.task-code-head) {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 8px 16px;
	background: rgba(2, 6, 23, 0.9);
	border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.task-html-body :deep(.task-code-lang) {
	font-family: ui-monospace, monospace;
	font-size: 12px;
	color: #94a3b8;
	text-transform: lowercase;
}

.task-html-body :deep(.task-code-copy-btn) {
	border: 0;
	background: transparent;
	color: #e2e8f0;
	cursor: pointer;
	font-family: "Material Symbols Outlined", "Material Icons", sans-serif;
	font-size: 20px;
	padding: 4px;
	border-radius: 4px;
	transition: all 0.2s ease;
}

.task-html-body :deep(.task-code-copy-btn:hover) {
	background: rgba(148, 163, 184, 0.2);
	color: #fff;
}
</style>
