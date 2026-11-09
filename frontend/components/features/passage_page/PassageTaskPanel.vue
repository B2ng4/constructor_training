<template>
	<div v-if="selectedStep" class="passage-task-panel glass-panel">
		<header class="passage-task-panel__head">
			<q-icon name="assignment" size="18px" class="passage-task-panel__icon" />
			<span class="passage-task-panel__short">{{ shortTitle }}</span>
		</header>

		<div class="passage-task-panel__content-area">
			<div
				v-if="htmlContent"
				class="passage-task-panel__body task-html-body"
				v-html="htmlContent"
				@click="onTaskBodyClick"
			></div>
			<div v-else class="passage-task-panel__empty text-grey-6">
				Текст задания не заполнен. Отредактируйте шаг в конструкторе.
			</div>
		</div>

		<!-- Кастомный Аудио-плеер -->
		<div v-if="selectedStep?.audio_url" class="premium-audio-player">
			<q-btn
				flat
				round
				dense
				:icon="isPlaying ? 'pause' : 'play_arrow'"
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
				@play="isPlaying = true"
				@pause="isPlaying = false"
				style="display: none;"
			/>
		</div>
	</div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue";
import { useQuasar } from "quasar";
import { renderAnnotationToSafeHtml } from "@utils/renderAnnotationHtml.js";

const props = defineProps({
	selectedStep: { type: Object, default: null },
});
const $q = useQuasar();

const audioRef = ref(null);
const isPlaying = ref(false);
const audioProgress = ref(0);
const audioCurrentTime = ref(0);

// Глобальное состояние звука в сессии (по умолчанию ВКЛЮЧЕНО)
const isMuted = ref(sessionStorage.getItem("passage_muted") === "true");

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
	isPlaying.value = false;
	audioProgress.value = 0;
}

function toggleAudio() {
	if (!audioRef.value) return;
	if (isPlaying.value) {
		audioRef.value.pause();
	} else {
		audioRef.value.play();
	}
	isPlaying.value = !isPlaying.value;
}

// Автовоспроизведение при смене шага
watch(
	() => props.selectedStep?.id,
	async (newId) => {
		if (!newId) return;
		// Сброс состояния плеера
		isPlaying.value = false;
		audioProgress.value = 0;
		audioCurrentTime.value = 0;

		if (isMuted.value) return;

		await nextTick();
		if (audioRef.value && props.selectedStep?.audio_url) {
			audioRef.value.currentTime = 0;
			audioRef.value.play().catch(() => {
				// Блокировка автоплея — нормальное поведение браузера
			});
		}
	},
	{ immediate: true }
);

function toggleMute() {
	isMuted.value = !isMuted.value;
	sessionStorage.setItem("passage_muted", isMuted.value ? "true" : "false");
	if (isMuted.value && audioRef.value) {
		audioRef.value.pause();
	} else if (!isMuted.value && audioRef.value) {
		audioRef.value.play().catch(() => {});
	}
}

const shortTitle = computed(() => {
	const s = props.selectedStep;
	if (!s) return "";
	const n = (s.meta?.name ?? "").trim();
	if (n && n !== "Шаг без названия") return n;
	return `Шаг ${s.step_number ?? ""}`.trim();
});

const htmlContent = computed(() => {
	const raw = props.selectedStep?.annotation;
	return renderAnnotationToSafeHtml(raw);
});

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

function onTaskBodyClick(e) {
	void copyCodeFromEvent(e);
}
</script>

<style scoped>
.passage-task-panel {
	display: flex;
	flex-direction: column;
	min-height: 0;
	flex: 1;
	overflow: hidden;
	transition: all 0.4s var(--anim-ease-out);
}

.passage-task-panel__head {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 16px 20px;
	background: rgba(255, 255, 255, 0.4);
	backdrop-filter: blur(10px);
	border-bottom: 1px solid rgba(15, 23, 42, 0.06);
	flex-shrink: 0;
}

.passage-task-panel__icon {
	color: var(--q-primary);
	opacity: 0.9;
	flex-shrink: 0;
}

.passage-task-panel__short {
	font-size: 18px;
	font-weight: 700;
	color: #1e293b;
	letter-spacing: -0.01em;
}

.passage-task-panel__content-area {
	flex: 1;
	min-height: 0;
	display: flex;
	flex-direction: column;
	background: rgba(255, 255, 255, 0.2);
}

.passage-task-panel__body {
	padding: 24px 28px;
	overflow-y: auto;
	flex: 1;
	min-height: 0;
	font-family: var(--font-sans);
	font-size: 19px;
	line-height: 1.7;
	color: #1e293b;
	letter-spacing: -0.01em;
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

.passage-task-panel__empty {
	padding: 24px 28px;
	font-size: 16px;
	color: #64748b;
}

/* Premium Audio Player */
.premium-audio-player {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 12px 20px;
	background: rgba(255, 255, 255, 0.6);
	backdrop-filter: blur(16px);
	border-top: 1px solid rgba(15, 23, 42, 0.08);
	flex-shrink: 0;
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

@media (max-width: 1200px) {
	.passage-task-panel__body {
		font-size: 17px;
	}
}
</style>
