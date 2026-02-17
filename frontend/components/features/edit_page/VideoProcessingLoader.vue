<template>
	<div class="video-processing-overlay">
		<div class="processing-card">
			<div class="processing-animation">
				<q-spinner-cube size="60px" color="primary" />
			</div>
			
			<div class="processing-title">{{ currentStep.title }}</div>
			<div class="processing-description">{{ currentStep.description }}</div>
			
			<div class="processing-steps">
				<div
					v-for="(step, index) in steps"
					:key="index"
					class="step-indicator"
					:class="{
						'step-indicator--completed': index < currentStepIndex,
						'step-indicator--active': index === currentStepIndex
					}"
				>
					<q-icon
						:name="step.icon"
						size="16px"
						:color="index <= currentStepIndex ? 'primary' : 'grey-5'"
					/>
					<span class="step-label">{{ step.label }}</span>
					<q-icon
						v-if="index < currentStepIndex"
						name="check_circle"
						size="16px"
						color="positive"
						class="step-check"
					/>
				</div>
			</div>
			
			<q-linear-progress
				:value="progress"
				color="primary"
				class="processing-progress"
				rounded
			/>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';

const steps = [
	{ icon: 'upload', label: 'Загрузка видео', title: 'Загружаем видео...', description: 'Отправляем файл на сервер' },
	{ icon: 'auto_fix_high', label: 'AI-анализ', title: 'AI модель анализирует видео', description: 'Определяем действия пользователя и ключевые моменты' },
	{ icon: 'cut', label: 'Извлечение кадров', title: 'Извлекаем кадры', description: 'Создаём скриншоты в нужные моменты времени' },
	{ icon: 'psychology', label: 'Генерация описаний', title: 'Генерируем описания шагов', description: 'AI создаёт подробные инструкции для каждого шага' },
	{ icon: 'check_circle', label: 'Завершение', title: 'Почти готово!', description: 'Формируем финальные шаги тренинга' }
];

const currentStepIndex = ref(0);
const progress = ref(0);
let interval = null;

const currentStep = computed(() => steps[currentStepIndex.value] || steps[0]);

onMounted(() => {
	// Симулируем прогресс
	interval = setInterval(() => {
		if (currentStepIndex.value < steps.length - 1) {
			progress.value += 0.01;
			
			// Переход к следующему шагу
			if (progress.value >= (currentStepIndex.value + 1) / steps.length) {
				currentStepIndex.value++;
			}
		} else {
			progress.value = Math.min(progress.value + 0.005, 0.98);
		}
	}, 150);
});

onUnmounted(() => {
	if (interval) clearInterval(interval);
});
</script>

<style scoped>
.video-processing-overlay {
	position: absolute;
	inset: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(255, 255, 255, 0.98);
	backdrop-filter: blur(4px);
	z-index: 9999;
	padding: 20px;
}

.processing-card {
	background: white;
	border-radius: 20px;
	padding: 40px 50px;
	max-width: 500px;
	width: 100%;
	box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
	display: flex;
	flex-direction: column;
	align-items: center;
	text-align: center;
}

.processing-animation {
	margin-bottom: 24px;
}

.processing-title {
	font-size: 20px;
	font-weight: 600;
	color: #1a1a1a;
	margin-bottom: 8px;
}

.processing-description {
	font-size: 14px;
	color: #6b7280;
	margin-bottom: 32px;
	line-height: 1.5;
}

.processing-steps {
	width: 100%;
	display: flex;
	flex-direction: column;
	gap: 12px;
	margin-bottom: 24px;
}

.step-indicator {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 10px 16px;
	border-radius: 10px;
	background: #f9fafb;
	transition: all 0.3s ease;
	position: relative;
}

.step-indicator--active {
	background: rgba(80, 100, 247, 0.08);
	border: 1px solid rgba(80, 100, 247, 0.2);
}

.step-indicator--completed {
	background: rgba(34, 197, 94, 0.05);
	border: 1px solid rgba(34, 197, 94, 0.1);
}

.step-label {
	flex: 1;
	text-align: left;
	font-size: 13px;
	font-weight: 500;
	color: #374151;
}

.step-check {
	position: absolute;
	right: 12px;
}

.processing-progress {
	width: 100%;
	height: 8px;
	margin-top: 8px;
}
</style>
