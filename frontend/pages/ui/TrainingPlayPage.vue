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
			<!-- Таймер -->
			<div v-if="durationMinutes > 0" class="timer-clock">
				<div class="timer-clock__face" :class="{ 'timer-clock__face--over': timer.timeRemaining.value <= 0 }">
					<q-icon name="schedule" size="22px" class="timer-clock__icon" />
					<div class="timer-clock__time">
						{{ timer.formatTime(timer.timeRemaining.value > 0 ? timer.timeRemaining.value : timer.totalSecondsSpent.value) }}
					</div>
					<div class="timer-clock__label">{{ timer.timeRemaining.value > 0 ? "осталось" : "время" }}</div>
					<svg class="timer-clock__ring" viewBox="0 0 36 36">
						<path
							class="timer-clock__ring-bg"
							d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
						/>
						<path
							class="timer-clock__ring-fill"
							:stroke-dasharray="`${(1 - timer.timerProgress.value) * 100}, 100`"
							d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
						/>
					</svg>
				</div>
			</div>

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

			<!-- Основная область: скриншот + интерактив -->
			<template v-else>
				<PassageStepList
					:steps="steps"
					:current-index="currentIndex"
					class="step-list-absolute"
					@select-step="passage.selectStep"
				/>
				<PassageStepTitle :selected-step="selectedStep" />
				<PassageStepHint
					:selected-step="selectedStep"
					:force-show="showHintAfterWrong"
				/>

				<div class="flow-area">
					<PassageFlowComponent
						mode="passage"
						:selected-step="selectedStep"
						@action-complete="onActionComplete"
						@action-wrong="onActionWrong"
					/>
				</div>

				<PassageToolbar
					:has-previous-step="hasPreviousStep"
					:has-next-step="hasNextStep"
					:selected-step="selectedStep"
					:skip-steps="passage.skipSteps"
					@prev="passage.prevStep"
					@next="goNext"
				/>
			</template>
		</template>
	</div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { usePassageData } from "@composables/usePassageData.js";
import { usePassageTimer } from "@composables/usePassageTimer.js";
import {
	PassageFlowComponent,
	PassageStepList,
	PassageStepTitle,
	PassageStepHint,
	PassageToolbar,
} from "@components/features/passage_page";

const props = defineProps({
	trainingData: { type: Object, default: null },
});

const route = useRoute();
const router = useRouter();
const $q = useQuasar();

const passage = usePassageData(computed(() => props.trainingData));

const steps = computed(() => passage.steps.value);
const currentIndex = computed(() => passage.currentIndex.value);
const selectedStep = computed(() => passage.selectedStep.value);
const hasPreviousStep = computed(() => passage.hasPreviousStep.value);
const hasNextStep = computed(() => passage.hasNextStep.value);

const showCompletionModal = ref(false);
const wrongAttempts = ref(0);
const showHintAfterWrong = computed(() => wrongAttempts.value >= 3);

watch(
	() => selectedStep.value?.id,
	() => {
		wrongAttempts.value = 0;
	}
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

function onActionComplete() {
	$q.notify({
		color: "positive",
		message: "Верно!",
		position: "top",
		timeout: 800,
	});
	goNext();
}

function onActionWrong() {
	wrongAttempts.value += 1;
	const count = wrongAttempts.value;
	if (count >= 3) {
		$q.notify({
			color: "info",
			message: "Показана подсказка",
			position: "top",
			icon: "lightbulb",
		});
	} else {
		$q.notify({
			color: "negative",
			message: `Неверно. Попробуйте ещё раз${count === 2 ? " (после следующей ошибки будет подсказка)" : ""}`,
			position: "top",
		});
	}
}

function goNext() {
	if (passage.hasNextStep.value) {
		passage.nextStep();
	} else {
		timer.stop();
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
</script>

<style scoped>
.play-page {
	position: relative;
	width: 100%;
	height: 100%;
	min-height: 0;
	overflow: hidden;
	background: #f0f1f5;
}

/* ——— Часы (таймер) ——— */
.timer-clock {
	position: absolute;
	top: 16px;
	right: 16px;
	z-index: 15;
}

.timer-clock__face {
	position: relative;
	width: 72px;
	height: 72px;
	border-radius: 50%;
	background: #fff;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(0, 0, 0, 0.06);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.timer-clock__face--over {
	background: rgba(239, 68, 68, 0.08);
	border-color: rgba(239, 68, 68, 0.2);
}

.timer-clock__icon {
	color: var(--q-primary);
	opacity: 0.9;
	margin-bottom: 2px;
}

.timer-clock__face--over .timer-clock__icon {
	color: #ef4444;
}

.timer-clock__time {
	font-size: 13px;
	font-weight: 700;
	color: #1a1a2e;
	line-height: 1.2;
}

.timer-clock__face--over .timer-clock__time {
	color: #b91c1c;
}

.timer-clock__label {
	font-size: 9px;
	font-weight: 600;
	text-transform: uppercase;
	letter-spacing: 0.02em;
	color: #64748b;
}

.timer-clock__face--over .timer-clock__label {
	color: #dc2626;
}

.timer-clock__ring {
	position: absolute;
	top: 50%;
	left: 50%;
	width: 100%;
	height: 100%;
	transform: translate(-50%, -50%) rotate(-90deg);
	pointer-events: none;
}

.timer-clock__ring-bg {
	fill: none;
	stroke: rgba(0, 0, 0, 0.06);
	stroke-width: 2;
}

.timer-clock__ring-fill {
	fill: none;
	stroke: var(--q-primary);
	stroke-width: 2;
	stroke-linecap: round;
	transition: stroke-dasharray 0.3s ease;
}

.timer-clock__face--over .timer-clock__ring-fill {
	stroke: #ef4444;
}

.step-list-absolute {
	position: absolute;
	top: 16px;
	left: 16px;
	z-index: 10;
}

.flow-area {
	position: absolute;
	inset: 0;
	z-index: 1;
	overflow: hidden;
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
