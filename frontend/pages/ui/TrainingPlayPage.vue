<template>
	<div class="play-page">
		<!-- Модальное окно завершения -->
		<q-dialog v-model="showCompletionModal" persistent>
			<q-card class="completion-modal">
				<q-card-section class="completion-header">
					<div class="completion-icon">
						<q-icon name="celebration" size="56px" color="positive" />
					</div>
					<h2 class="completion-title">Тренинг пройден!</h2>
					<p class="completion-text">
						Поздравляем! Вы успешно завершили тренинг.
					</p>
					<p v-if="durationMinutes > 0" class="completion-time">
						Время: {{ timer.formatTime(timer.totalSecondsSpent.value) }}
					</p>
				</q-card-section>
				<q-card-actions align="center" class="completion-actions">
					<q-btn
						unelevated
						no-caps
						rounded
						color="primary"
						icon="check"
						label="Закрыть"
						@click="closeCompletionModal"
					/>
				</q-card-actions>
			</q-card>
		</q-dialog>

		<!-- Пустое состояние -->
		<div v-if="!trainingData || !steps.length" class="empty-state">
			<q-icon name="info" size="48px" color="grey-5" />
			<p>Нет шагов для прохождения</p>
			<q-btn
				flat
				no-caps
				label="Вернуться к описанию"
				icon="arrow_back"
				color="primary"
				@click="goToWelcome"
			/>
		</div>

		<!-- Прохождение -->
		<template v-else>
			<header
				class="play-top-bar"
				:class="{ 'play-top-bar--viewport-only': hasSideTaskPanel }"
			>
				<div class="play-top-bar__left">
					<q-btn
						flat
						no-caps
						rounded
						color="grey-8"
						icon="home"
						class="play-top-bar__home"
						@click="confirmExitToHome"
					>
						<span class="play-top-bar__home-label gt-xs">На главную</span>
						<q-tooltip>На главный экран</q-tooltip>
					</q-btn>
					<PassageStepList
						:steps="steps"
						:current-index="currentIndex"
						@select-step="passage.selectStep"
					/>
				</div>
				<div class="play-top-bar__spacer" aria-hidden="true" />
				<div
					v-if="durationMinutes > 0"
					class="timer-panel"
					:class="timerPanelClass"
				>
					<div class="timer-panel__row">
						<div class="timer-panel__icon-wrap">
							<q-icon
								:name="timer.timeRemaining.value > 0 ? 'schedule' : 'timer_off'"
								size="22px"
								class="timer-panel__icon"
							/>
						</div>
						<div class="timer-panel__main">
							<div class="timer-panel__caption">
								{{ timer.timeRemaining.value > 0 ? "Осталось времени" : "Лимит времени" }}
							</div>
							<div class="timer-panel__digits">
								{{ timerDisplayValue }}
							</div>
						</div>
					</div>
					<q-linear-progress
						v-if="timer.timeRemaining.value > 0"
						:value="timer.timerProgress.value"
						:color="timer.timeRemaining.value <= 60 ? 'warning' : 'primary'"
						rounded
						size="6px"
						class="timer-panel__bar"
						track-color="rgba(15, 23, 42, 0.08)"
					/>
					<q-linear-progress
						v-else
						:value="1"
						rounded
						size="6px"
						color="negative"
						class="timer-panel__bar timer-panel__bar--over"
						track-color="rgba(239, 68, 68, 0.15)"
					/>
				</div>
			</header>

			<!-- Шаг без скриншота -->
			<div
				v-if="selectedStep && !selectedStep.image_url"
				class="no-image-state"
			>
				<q-icon name="image_not_supported" size="64px" color="grey-4" />
				<p>У этого шага нет изображения</p>
				<q-btn
					unelevated
					no-caps
					rounded
					color="primary"
					:label="hasNextStep ? 'Следующий шаг' : 'Завершить'"
					icon="arrow_forward"
					@click="goNext"
				/>
			</div>

			<!-- Скрин слева, задание справа — как окно программы -->
			<template v-else>
				<div class="play-layout">
					<div class="play-layout__viewport">
						<div class="flow-area">
							<PassageFlowComponent
								mode="passage"
								:selected-step="selectedStep"
								:show-hint-highlight="hintVisible"
								@action-complete="onActionComplete"
								@action-wrong="onActionWrong"
							/>
						</div>
						<PassageToolbar
							:has-previous-step="hasPreviousStep"
							:has-next-step="hasNextStep"
							:selected-step="selectedStep"
							:skip-steps="passage.skipSteps"
							:hints-enabled="hintsEnabled"
							:hints-available="hintsAvailable"
							@prev="passage.prevStep"
							@next="goNext"
							@toggle-hints="toggleHintsForCurrentStep"
						/>
					</div>
					<aside class="play-layout__task">
						<PassageTaskPanel :selected-step="selectedStep" />
					</aside>
				</div>
			</template>
		</template>
	</div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { usePassageData } from "@composables/usePassageData.js";
import { usePassageTimer } from "@composables/usePassageTimer.js";
import {
	PassageFlowComponent,
	PassageStepList,
	PassageTaskPanel,
	PassageToolbar,
} from "@components/features/passage_page";
import { TrainingApi } from "@api";
import { isInputTextType } from "@utils/actionTypes.js";

const props = defineProps({
	trainingData: { type: Object, default: null },
});

const route = useRoute();
const router = useRouter();
const $q = useQuasar();
const trainingApi = new TrainingApi();

const passage = usePassageData(computed(() => props.trainingData));

const steps = computed(() => passage.steps.value);
const currentIndex = computed(() => passage.currentIndex.value);
const selectedStep = computed(() => passage.selectedStep.value);
const hasPreviousStep = computed(() => passage.hasPreviousStep.value);
const hasNextStep = computed(() => passage.hasNextStep.value);

const showCompletionModal = ref(false);
const wrongAttempts = ref(0);
const totalWrongSession = ref(0);
const playStartedAtMs = ref(0);
/** Подсказки по шагам: включение хранится отдельно для каждого шага */
const hintsEnabledByStep = ref({});
const hintsAvailable = computed(() => props.trainingData?.hints_enabled !== false);
const hintsEnabled = computed({
	get: () => {
		const id = selectedStep.value?.id;
		if (!id) return false;
		return !!hintsEnabledByStep.value[id];
	},
	set: (val) => {
		const id = selectedStep.value?.id;
		if (!id) return;
		hintsEnabledByStep.value = {
			...hintsEnabledByStep.value,
			[id]: !!val,
		};
	},
});
const hintVisible = computed(() => {
	if (!hintsAvailable.value || !hintsEnabled.value) return false;
	if (isInputTextType(selectedStep.value?.action_type)) return true;
	return wrongAttempts.value > 0;
});

/** Колонка с заданием слева от скрина — верхнюю панель только над скрином */
const hasSideTaskPanel = computed(() => !!selectedStep.value?.image_url);

onMounted(() => {
	playStartedAtMs.value = Date.now();
});

watch(
	() => selectedStep.value?.id,
	() => {
		wrongAttempts.value = 0;
	}
);

watch(
	() => hintsAvailable.value,
	(v) => {
		if (!v) hintsEnabledByStep.value = {};
	},
	{ immediate: true }
);

const durationMinutes = computed(() => props.trainingData?.duration_minutes ?? 0);

const timer = usePassageTimer(durationMinutes, () => {
	$q.notify({
		color: "warning",
		message: "Время вышло",
		position: "top",
		icon: "schedule",
	});
});

const timerDisplayValue = computed(() =>
	timer.formatTime(
		timer.timeRemaining.value > 0
			? timer.timeRemaining.value
			: timer.totalSecondsSpent.value
	)
);

const timerPanelClass = computed(() => ({
	"timer-panel--over": durationMinutes.value > 0 && timer.timeRemaining.value <= 0,
	"timer-panel--urgent":
		durationMinutes.value > 0 &&
		timer.timeRemaining.value > 0 &&
		timer.timeRemaining.value <= 60,
}));

function onActionComplete() {
	if (isInputTextType(selectedStep.value?.action_type)) {
		$q.notify({
			color: "positive",
			message: "Правильно!",
			position: "top",
			timeout: 900,
		});
	}
	goNext();
}

function onActionWrong() {
	wrongAttempts.value += 1;
	totalWrongSession.value += 1;
	$q.notify({
		color: "negative",
		message: !hintsAvailable.value
			? "Неверно. Попробуйте ещё раз."
			: hintsEnabled.value
			? "Неверно. Включены подсказки — смотрите выделение на скрине или поле ввода."
			: "Неверно. Попробуйте ещё раз. Можно включить подсказки кнопкой снизу.",
		position: "top",
	});
}

function reportPassageComplete() {
	const token = route.params.accessToken;
	if (!token) return;
	const key = `passage_attempt_${token}`;
	const raw = sessionStorage.getItem(key);
	if (raw == null) return;
	const attemptId = parseInt(raw, 10);
	const durMin = durationMinutes.value;
	const durationSec =
		durMin > 0
			? Math.round(timer.totalSecondsSpent.value)
			: Math.max(0, Math.round((Date.now() - playStartedAtMs.value) / 1000));
	void trainingApi
		.completePassageAttempt(token, {
			attempt_id: attemptId,
			is_completed: true,
			duration_seconds: durationSec,
			wrong_attempts_total: totalWrongSession.value,
		})
		.then(() => {
			sessionStorage.removeItem(key);
		})
		.catch((e) => {
			console.warn("[passage] complete", e);
		});
}

function goNext() {
	if (passage.hasNextStep.value) {
		passage.nextStep();
	} else {
		timer.stop();
		reportPassageComplete();
		showCompletionModal.value = true;
	}
}

function closeCompletionModal() {
	showCompletionModal.value = false;
	router.push("/");
}

function goToWelcome() {
	router.push({
		name: "TrainingWelcome",
		params: { accessToken: route.params.accessToken },
	});
}

function confirmExitToHome() {
	$q.dialog({
		title: "Выйти из тренинга?",
		message: "Текущий прогресс не будет сохранён.",
		cancel: true,
		persistent: true,
		ok: {
			label: "На главную",
			color: "primary",
			flat: true,
		},
	}).onOk(() => {
		timer.stop();
		router.push("/");
	});
}

function toggleHintsForCurrentStep() {
	if (!hintsAvailable.value) {
		hintsEnabled.value = false;
		return;
	}
	hintsEnabled.value = !hintsEnabled.value;
}
</script>

<style scoped>
.play-page {
	position: relative;
	width: 100%;
	height: 100%;
	min-height: 0;
	overflow: hidden;
	background: #e8eaef;
}

.play-layout {
	display: flex;
	flex-direction: row-reverse;
	width: 100%;
	height: 100%;
	min-height: 0;
	align-items: stretch;
}

.play-layout__viewport {
	position: relative;
	flex: 1;
	min-width: 0;
	min-height: 0;
	display: flex;
	flex-direction: column;
	background: #f0f1f5;
}

.play-layout__task {
	width: min(420px, 38vw);
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	min-height: 0;
	background: #fafbfc;
	border-right: 1px solid rgba(15, 23, 42, 0.08);
}

@media (max-width: 900px) {
	.play-layout {
		flex-direction: column;
	}

	.play-layout__task {
		width: 100%;
		max-height: min(40vh, 320px);
		border-right: none;
		border-top: 1px solid rgba(15, 23, 42, 0.08);
	}

	.play-top-bar--viewport-only {
		left: 0;
		right: 0;
	}
}

/* ——— Верхняя панель: домой + таймер ——— */
.play-top-bar {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	z-index: 20;
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 10px 14px;
	min-height: 56px;
	pointer-events: none;
	box-sizing: border-box;
}

.play-top-bar__left {
	display: flex;
	align-items: center;
	gap: 10px;
	flex-shrink: 1;
	min-width: 0;
	pointer-events: auto;
}

.play-top-bar__spacer {
	flex: 1;
	min-width: 8px;
	pointer-events: none;
}

.play-top-bar > .timer-panel {
	pointer-events: auto;
	flex-shrink: 0;
}

/*
 * Десктоп: задание слева (row-reverse), панель не заходит на лист задания.
 * Совпадает с шириной .play-layout__task: min(420px, 38vw).
 */
.play-top-bar--viewport-only {
	left: min(420px, 38vw);
	right: 0;
}

.play-top-bar__home {
	background: rgba(255, 255, 255, 0.92) !important;
	backdrop-filter: blur(10px);
	box-shadow: 0 2px 14px rgba(15, 23, 42, 0.08);
	border: 1px solid rgba(15, 23, 42, 0.06);
}

.play-top-bar__home-label {
	margin-left: 4px;
	font-size: 14px;
	font-weight: 600;
}

.timer-panel {
	min-width: 0;
	max-width: min(280px, 52vw);
	padding: 10px 14px 12px;
	border-radius: 14px;
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: blur(12px);
	border: 1px solid rgba(15, 23, 42, 0.07);
	box-shadow:
		0 4px 24px rgba(15, 23, 42, 0.1),
		0 0 0 1px rgba(255, 255, 255, 0.6) inset;
	transition:
		border-color 0.25s ease,
		box-shadow 0.25s ease;
}

.timer-panel--urgent {
	border-color: rgba(245, 158, 11, 0.45);
	box-shadow:
		0 4px 20px rgba(245, 158, 11, 0.18),
		0 0 0 1px rgba(255, 255, 255, 0.5) inset;
	animation: timer-urgent-pulse 2s ease-in-out infinite;
}

.timer-panel--over {
	border-color: rgba(239, 68, 68, 0.35);
	background: rgba(254, 242, 242, 0.96);
	box-shadow:
		0 4px 22px rgba(239, 68, 68, 0.12),
		0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

@keyframes timer-urgent-pulse {
	0%,
	100% {
		box-shadow:
			0 4px 20px rgba(245, 158, 11, 0.18),
			0 0 0 1px rgba(255, 255, 255, 0.5) inset;
	}
	50% {
		box-shadow:
			0 6px 28px rgba(245, 158, 11, 0.28),
			0 0 0 1px rgba(255, 255, 255, 0.5) inset;
	}
}

.timer-panel__row {
	display: flex;
	align-items: center;
	gap: 12px;
	margin-bottom: 8px;
}

.timer-panel__icon-wrap {
	flex-shrink: 0;
	width: 40px;
	height: 40px;
	border-radius: 12px;
	display: flex;
	align-items: center;
	justify-content: center;
	background: linear-gradient(
		145deg,
		color-mix(in srgb, var(--q-primary) 22%, white),
		color-mix(in srgb, var(--q-primary) 10%, white)
	);
}

.timer-panel--urgent .timer-panel__icon-wrap {
	background: linear-gradient(
		145deg,
		rgba(245, 158, 11, 0.22),
		rgba(245, 158, 11, 0.08)
	);
}

.timer-panel--over .timer-panel__icon-wrap {
	background: linear-gradient(
		145deg,
		rgba(239, 68, 68, 0.2),
		rgba(239, 68, 68, 0.08)
	);
}

.timer-panel__icon {
	color: var(--q-primary);
}

.timer-panel--urgent .timer-panel__icon {
	color: #d97706;
}

.timer-panel--over .timer-panel__icon {
	color: #dc2626;
}

.timer-panel__main {
	min-width: 0;
	flex: 1;
}

.timer-panel__caption {
	font-size: 11px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.06em;
	color: #64748b;
	margin-bottom: 2px;
}

.timer-panel--over .timer-panel__caption {
	color: #b91c1c;
}

.timer-panel__digits {
	font-size: 26px;
	font-weight: 800;
	font-variant-numeric: tabular-nums;
	letter-spacing: 0.04em;
	line-height: 1.1;
	color: #0f172a;
}

.timer-panel--urgent .timer-panel__digits {
	color: #b45309;
}

.timer-panel--over .timer-panel__digits {
	color: #991b1b;
}

.timer-panel__bar {
	margin-top: 2px;
}

.timer-panel__bar--over {
	opacity: 0.85;
}

.flow-area {
	position: absolute;
	inset: 0;
	z-index: 1;
	overflow: hidden;
}

.play-layout__viewport .flow-area {
	top: 56px;
	bottom: 72px;
}

.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 16px;
	min-height: 60vh;
	color: #64748b;
}

.empty-state p {
	margin: 0;
	font-size: 15px;
}

.no-image-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 20px;
	min-height: 60vh;
	padding-top: 64px;
	box-sizing: border-box;
	color: #64748b;
}

.no-image-state p {
	margin: 0;
	font-size: 15px;
}

/* ——— Модальное окно завершения ——— */
.completion-modal {
	border-radius: 20px;
	min-width: 360px;
	overflow: hidden;
}

.completion-header {
	text-align: center;
	padding: 32px 32px 24px;
}

.completion-icon {
	width: 96px;
	height: 96px;
	border-radius: 50%;
	background: rgba(33, 186, 69, 0.12);
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 auto 20px;
}

.completion-title {
	font-size: 24px;
	font-weight: 700;
	color: #0f172a;
	margin: 0 0 12px 0;
}

.completion-text {
	font-size: 15px;
	color: #64748b;
	margin: 0;
	line-height: 1.5;
}

.completion-time {
	font-size: 14px;
	font-weight: 600;
	color: #334155;
	margin: 8px 0 0 0;
}

.completion-actions {
	padding: 0 32px 28px;
}
</style>
