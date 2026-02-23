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
				<PassageStepHint :selected-step="selectedStep" />

				<div class="flow-area">
					<PassageFlowComponent
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
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { usePassageData } from "@composables/usePassageData.js";
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
	$q.notify({
		color: "negative",
		message: "Неверно, попробуйте ещё раз",
		position: "top",
	});
}

function goNext() {
	if (passage.hasNextStep.value) {
		passage.nextStep();
	} else {
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

.completion-actions {
	padding: 0 32px 28px;
}
</style>
