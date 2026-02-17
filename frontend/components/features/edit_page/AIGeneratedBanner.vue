<template>
	<transition name="banner-slide">
		<div v-if="showBanner && isAIGenerated" class="ai-banner">
			<div class="ai-banner-content">
				<q-icon name="auto_awesome" size="20px" class="ai-banner-icon" />
				<div class="ai-banner-text">
					<div class="ai-banner-title">Шаг создан с помощью AI</div>
					<div class="ai-banner-desc">
						Возможны неточности распознавания. Вы можете отредактировать описание и уточнить область действия.
					</div>
				</div>
			</div>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="close"
				color="primary"
				class="ai-banner-close"
				@click="dismissBanner"
			>
				<q-tooltip>Скрыть подсказку</q-tooltip>
			</q-btn>
		</div>
	</transition>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";

const store = useTrainingData();
const { selectedStep } = storeToRefs(store);

const showBanner = ref(true);
const dismissedSteps = ref(new Set());

// Определяем, создан ли шаг AI (по наличию annotation с вопросом "Как...")
const isAIGenerated = computed(() => {
	if (!selectedStep.value?.id) return false;
	
	// Если уже закрыли баннер для этого шага
	if (dismissedSteps.value.has(selectedStep.value.id)) return false;
	
	// Проверяем, что есть annotation и начинается с "Как"
	const annotation = selectedStep.value?.annotation;
	return annotation && annotation.trim().startsWith("Как");
});

// Сбрасываем показ баннера при смене шага
watch(() => selectedStep.value?.id, () => {
	showBanner.value = true;
});

function dismissBanner() {
	if (selectedStep.value?.id) {
		dismissedSteps.value.add(selectedStep.value.id);
		showBanner.value = false;
	}
}
</script>

<style scoped>
.ai-banner {
	position: absolute;
	top: 112px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 1;
	background: linear-gradient(135deg, rgba(139, 92, 246, 0.95) 0%, rgba(99, 102, 241, 0.95) 100%);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	padding: 12px 16px;
	border-radius: 14px;
	box-shadow: 0 4px 24px rgba(139, 92, 246, 0.4);
	border: 1px solid rgba(255, 255, 255, 0.2);
	max-width: 480px;
	display: flex;
	align-items: flex-start;
	gap: 12px;
}

.ai-banner-content {
	display: flex;
	align-items: flex-start;
	gap: 10px;
	flex: 1;
}

.ai-banner-icon {
	color: rgba(255, 255, 255, 0.95);
	flex-shrink: 0;
	margin-top: 2px;
}

.ai-banner-text {
	flex: 1;
	min-width: 0;
}

.ai-banner-title {
	font-size: 13px;
	font-weight: 600;
	color: white;
	margin-bottom: 4px;
	letter-spacing: 0.01em;
}

.ai-banner-desc {
	font-size: 12px;
	color: rgba(255, 255, 255, 0.9);
	line-height: 1.5;
}

.ai-banner-close {
	flex-shrink: 0;
	margin-top: -4px;
}

/* Анимация появления */
.banner-slide-enter-active,
.banner-slide-leave-active {
	transition: all 0.3s ease;
}

.banner-slide-enter-from {
	opacity: 0;
	transform: translateX(-50%) translateY(-10px);
}

.banner-slide-leave-to {
	opacity: 0;
	transform: translateX(-50%) translateY(-10px);
}

@media (max-width: 768px) {
	.ai-banner {
		max-width: calc(100vw - 32px);
		top: 100px;
	}
	
	.ai-banner-title {
		font-size: 12px;
	}
	
	.ai-banner-desc {
		font-size: 11px;
	}
}
</style>
