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
			<div class="play-layout premium-bg-container">
				<header
					class="play-top-bar"
					:class="{ 'play-top-bar--viewport-only': hasSideTaskPanel }"
				>
					<div class="play-top-bar__left">
						<q-btn
							flat
							no-caps
							rounded
							color="grey-9"
							icon="home"
							class="play-top-bar__home glass-panel"
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
					<div class="play-top-bar__spacer"></div>
					<div class="play-top-bar__right">
						<q-btn
							v-if="hintsAvailable"
							flat
							round
							dense
							:icon="hintsEnabled ? 'lightbulb' : 'lightbulb_outline'"
							:text-color="hintsEnabled ? 'amber-9' : 'grey-7'"
							class="hint-btn glass-panel"
							:class="{ 'hint-btn--pulse': hintPulseActive }"
							@click="toggleHintsForCurrentStep"
						>
							<q-tooltip>
								{{
									hintsEnabled
										? "Подсказки включены: после ошибки подсветим область"
										: "Включить подсказки после ошибки"
								}}
							</q-tooltip>
						</q-btn>

						<div
							v-if="durationMinutes > 0"
							class="timer-panel glass-panel-dark"
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
						</div>
					</div>
				</header>

				<div class="play-layout__main">
					<aside class="play-layout__task glass-panel">
						<PassageTaskPanel :selected-step="selectedStep" />
					</aside>
					<div class="play-layout__viewport">
						<transition name="step-fade" mode="out-in">
							<div :key="selectedStep?.id" class="flow-area">
								<PassageFlowComponent
									ref="flowComponentRef"
									mode="passage"
									:selected-step="selectedStep"
									:show-hint-highlight="hintVisible"
									@action-complete="onActionComplete"
									@action-wrong="onActionWrong"
								/>
							</div>
						</transition>
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
				</div>
			</div>
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
const flowComponentRef = ref(null);
const hintPulseActive = ref(false);
let hintPulseTimer = null;
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
		position: "bottom-right",
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
			position: "bottom-right",
			timeout: 900,
		});
	}
	goNext();
}

function onActionWrong() {
	wrongAttempts.value += 1;
	totalWrongSession.value += 1;
	const branchResult = passage.advance("error", {
		wrong_attempts: wrongAttempts.value,
		score: Math.max(0, 100 - totalWrongSession.value * 10),
	});
	if (branchResult.completed) {
		finishPassage();
		return;
	}
	if (!branchResult.blocked && branchResult.step) {
		$q.notify({
			color: "warning",
			message: "Открыта дополнительная ветка сценария",
			position: "bottom-right",
		});
		return;
	}
	if (flowComponentRef.value) {
		flowComponentRef.value.triggerWrongFeedback();
	}
	
	if (hintsAvailable.value && !hintsEnabled.value) {
		hintPulseActive.value = true;
		if (hintPulseTimer) clearTimeout(hintPulseTimer);
		hintPulseTimer = setTimeout(() => { hintPulseActive.value = false; }, 2400);
	}

	$q.notify({
		color: "negative",
		message: !hintsAvailable.value
			? "Неверно. Попробуйте ещё раз."
			: hintsEnabled.value
			? "Неверно. Включены подсказки — смотрите выделение на скрине или поле ввода."
			: "Неверно. Можно включить подсказки кнопкой 💡 (лампочка) на верхней панели справа.",
		position: "bottom-right",
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

function finishPassage() {
	timer.stop();
	reportPassageComplete();
	showCompletionModal.value = true;
}

function goNext() {
	const result = passage.advance("success", {
		wrong_attempts: wrongAttempts.value,
		score: Math.max(0, 100 - totalWrongSession.value * 10),
	});
	if (result.completed) {
		finishPassage();
		return;
	}
	if (result.blocked) {
		$q.notify({
			color: "warning",
			message: "Для этого шага не настроен переход по успешному действию",
			position: "bottom-right",
		});
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
	flex-direction: column;
	width: 100%;
	height: 100%;
	min-height: 0;
	position: relative;
}

.play-layout__main {
	display: flex;
	flex-direction: row;
	flex: 1;
	min-height: 0;
	width: 100%;
	align-items: stretch;
}

.play-layout__viewport {
	position: relative;
	flex: 1;
	min-width: 0;
	min-height: 0;
	display: flex;
	flex-direction: column;
}

.play-layout__task {
	width: min(440px, 40vw);
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	min-height: 0;
	z-index: 100;
	padding: 12px;
	gap: 12px;
	margin: 12px 0 12px 12px;
	border-radius: 16px;
	overflow: hidden;
}

@media (max-width: 900px) {
	.play-layout {
		flex-direction: column;
	}

	.play-layout__main {
		flex-direction: column;
	}

	.play-layout__viewport {
		order: -1;
	}

	.play-layout__task {
		width: auto;
		max-height: min(45vh, 400px);
		margin: 0 12px 12px;
	}

	.play-top-bar--viewport-only {
		left: 0;
		right: 0;
		padding-left: 12px;
	}
}

/* ——— Верхняя панель: домой + таймер ——— */
.play-top-bar {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	z-index: 150;
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 8px 12px;
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

.play-top-bar__right {
	display: flex;
	align-items: center;
	gap: 12px;
	pointer-events: auto;
}

.hint-btn {
	background: rgba(255, 255, 255, 0.9) !important;
	border: 1px solid rgba(255, 255, 255, 0.6);
	transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	width: 44px;
	height: 44px;
}

.hint-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 8px 24px rgba(245, 158, 11, 0.25);
}

.hint-btn--pulse {
	animation: hint-attention-pulse 1.2s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
	border-color: rgba(245, 158, 11, 0.7) !important;
	background: rgba(254, 243, 199, 0.95) !important;
	color: #d97706 !important;
	z-index: 200;
}

@keyframes hint-attention-pulse {
	0%, 100% { 
		transform: scale(1); 
		box-shadow: 0 4px 16px rgba(245, 158, 11, 0.3) !important; 
	}
	50% { 
		transform: scale(1.15); 
		box-shadow: 0 8px 32px rgba(245, 158, 11, 0.7) !important; 
	}
}

/*
 * Десктоп: задание слева — верхняя панель не заходит на панель задания.
 */
.play-top-bar--viewport-only {
	left: 0;
	right: 0;
	padding-left: calc(min(440px, 40vw) + 24px);
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
	gap: 8px;
}

.timer-panel__icon-wrap {
	flex-shrink: 0;
	width: 32px;
	height: 32px;
	border-radius: 8px;
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
	font-size: 18px;
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
