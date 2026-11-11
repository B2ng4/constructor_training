<template>
	<q-dialog
		:model-value="modelValue"
		maximized
		transition-show="fade"
		transition-hide="fade"
		@update:model-value="emit('update:modelValue', $event)"
	>
		<q-card class="editor-passage-preview column">
			<!-- Верхняя панель как в прохождении: шаги слева, 💡 и закрытие справа -->
			<header class="preview-top-bar">
				<div class="preview-top-bar__left">
					<span class="preview-step-pill">
						Шаг {{ selectedStep?.step_number ?? "—" }} / {{ stepsCount }}
					</span>
				</div>
				<div class="preview-top-bar__spacer"></div>
				<div class="preview-top-bar__right">
					<q-btn
						flat
						round
						dense
						:icon="hintsEnabled ? 'lightbulb' : 'lightbulb_outline'"
						:text-color="hintsEnabled ? 'amber-9' : 'grey-7'"
						class="preview-hint-btn"
						@click="hintsEnabled = !hintsEnabled"
					>
						<q-tooltip>
							{{
								hintsEnabled
									? "Подсказки включены: подсветка области и текст подсказки"
									: "Включить подсказки"
							}}
						</q-tooltip>
					</q-btn>
					<q-btn flat round dense icon="close" v-close-popup>
						<q-tooltip>Закрыть превью (Esc)</q-tooltip>
					</q-btn>
				</div>
			</header>

			<div class="preview-main">
				<aside class="preview-task">
					<PassageTaskPanel :selected-step="selectedStep" />
				</aside>

				<div class="preview-viewport">
					<PassageFlowComponent
						v-if="selectedStep"
						:key="selectedStep.id"
						:selected-step="selectedStep"
						mode="passage"
						:show-hint-highlight="hintsEnabled"
					/>

					<!-- Всплывающая текстовая подсказка, как у ученика -->
					<transition name="hint-pop">
						<div
							v-if="hintsEnabled && hintText"
							class="preview-hint-bubble"
							role="note"
						>
							<q-icon name="lightbulb" size="18px" color="amber-9" />
							<span>{{ hintText }}</span>
						</div>
					</transition>

					<PassageToolbar
						:has-previous-step="hasPrevious"
						:has-next-step="hasNext"
						:selected-step="selectedStep"
						:skip-steps="!!trainingData?.skip_steps"
						:hints-enabled="hintsEnabled"
						:hints-available="hintsAvailable"
						@prev="store.goToPreviousStep()"
						@next="store.goToNextStep()"
						@toggle-hints="hintsEnabled = !hintsEnabled"
					/>
				</div>
			</div>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import {
	PassageFlowComponent,
	PassageTaskPanel,
	PassageToolbar,
} from "@components/features/passage_page";

defineProps({
	modelValue: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue"]);

const store = useTrainingData();
const { selectedStep, trainingData } = storeToRefs(store);
const hintsEnabled = ref(false);

const hintsAvailable = computed(() => trainingData.value?.hints_enabled !== false);
const hintText = computed(() => (selectedStep.value?.hint ?? "").trim());

const stepsList = computed(() => store.sortedSteps());
const stepsCount = computed(() => stepsList.value.length);

const currentIndex = computed(() => {
	if (!selectedStep.value) return -1;
	return stepsList.value.findIndex((s) => s.id === selectedStep.value.id);
});

const hasPrevious = computed(() => currentIndex.value > 0);
const hasNext = computed(
	() => currentIndex.value >= 0 && currentIndex.value < stepsList.value.length - 1,
);

watch(
	() => selectedStep.value?.id,
	() => {
		hintsEnabled.value = false;
	},
);
</script>

<style scoped>
.editor-passage-preview {
	width: 100%;
	height: 100%;
	background: #e8eaef;
	position: relative;
}

/* Верхняя панель — плавает как в прохождении */
.preview-top-bar {
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
.preview-top-bar__left {
	display: flex;
	align-items: center;
	gap: 10px;
	padding-left: calc(min(440px, 40vw) + 24px);
	pointer-events: auto;
}
.preview-top-bar__spacer {
	flex: 1;
	pointer-events: none;
}
.preview-top-bar__right {
	display: flex;
	align-items: center;
	gap: 12px;
	pointer-events: auto;
}
.preview-step-pill {
	font-size: 13px;
	font-weight: 600;
	color: #334155;
	background: rgba(255, 255, 255, 0.92);
	border: 1px solid rgba(15, 23, 42, 0.06);
	border-radius: 999px;
	padding: 8px 16px;
	box-shadow: 0 2px 14px rgba(15, 23, 42, 0.08);
}
.preview-hint-btn {
	background: rgba(255, 255, 255, 0.9) !important;
	border: 1px solid rgba(255, 255, 255, 0.6);
	width: 44px;
	height: 44px;
}

/* Основная зона: панель задания слева + viewport — как .play-layout__main */
.preview-main {
	display: flex;
	flex: 1;
	min-height: 0;
	width: 100%;
}
.preview-task {
	width: min(440px, 40vw);
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	min-height: 0;
	padding: 12px;
	margin: 12px 0 12px 12px;
	border-radius: 16px;
	background: rgba(255, 255, 255, 0.72);
	backdrop-filter: blur(16px);
	border: 1px solid rgba(255, 255, 255, 0.5);
	box-shadow: 0 8px 32px rgba(15, 23, 42, 0.08);
	overflow: hidden;
}
.preview-viewport {
	position: relative;
	flex: 1;
	min-width: 0;
	min-height: 0;
	display: flex;
	flex-direction: column;
	padding-top: 56px;
}

/* Всплывающая подсказка */
.preview-hint-bubble {
	position: absolute;
	bottom: 96px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 1200;
	display: flex;
	align-items: center;
	gap: 10px;
	max-width: min(520px, 80%);
	padding: 12px 20px;
	border-radius: 14px;
	background: rgba(255, 251, 235, 0.97);
	border: 1px solid rgba(245, 158, 11, 0.4);
	box-shadow: 0 12px 32px rgba(245, 158, 11, 0.18);
	font-size: 14px;
	font-weight: 500;
	color: #78350f;
}
.hint-pop-enter-active,
.hint-pop-leave-active {
	transition: all 0.25s ease;
}
.hint-pop-enter-from,
.hint-pop-leave-to {
	opacity: 0;
	transform: translateX(-50%) translateY(10px);
}

@media (max-width: 900px) {
	.preview-main {
		flex-direction: column;
	}
	.preview-viewport {
		order: -1;
	}
	.preview-task {
		width: auto;
		max-height: min(45vh, 400px);
		margin: 0 12px 12px;
	}
	.preview-top-bar__left {
		padding-left: 12px;
	}
}
</style>
