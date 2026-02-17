<template>
	<div class="passage-page">
		<!-- Loading State -->
		<div v-if="loading" class="loading-container">
			<q-spinner-dots size="50px" color="primary" />
			<div class="loading-text">Загружаем тренинг...</div>
		</div>

		<!-- Error State -->
		<div v-else-if="error" class="error-container">
			<div class="error-card">
				<div class="error-icon">
					<q-icon name="error_outline" size="56px" />
				</div>
				<div class="error-title">Тренинг не найден</div>
				<div class="error-desc">{{ errorMessage }}</div>
				<q-btn
					outline
					no-caps
					rounded
					color="primary"
					label="На главную"
					icon="home"
					class="error-btn"
					@click="$router.push('/personal/home')"
				/>
			</div>
		</div>

		<!-- Welcome Screen -->
		<div v-else-if="trainingData" class="welcome-container">
			<div class="welcome-content">
				<!-- Hero Section -->
				<div class="hero-section">
					<div class="hero-badge">
						<q-icon name="school" size="20px" />
						<span>Интерактивный тренинг</span>
					</div>
					<h1 class="hero-title">{{ trainingData.title }}</h1>
					<p class="hero-description">{{ trainingData.description }}</p>

					<!-- Metrics -->
					<div class="metrics-row">
						<div class="metric-item">
							<q-icon name="layers" size="20px" />
							<span>{{ stepsCount }} {{ stepsLabel }}</span>
						</div>
						<div v-if="trainingData.duration_minutes" class="metric-item">
							<q-icon name="schedule" size="20px" />
							<span>{{ trainingData.duration_minutes }} мин</span>
						</div>
						<div v-if="trainingData.level" class="metric-item">
							<q-icon name="signal_cellular_alt" size="20px" />
							<span>{{ trainingData.level.label }}</span>
						</div>
					</div>

					<!-- Tags -->
					<div v-if="trainingData.tags?.length" class="tags-row">
						<q-chip
							v-for="tag in trainingData.tags"
							:key="tag.value"
							size="sm"
							class="tag-chip"
						>
							{{ tag.label }}
						</q-chip>
					</div>
				</div>

				<!-- Training Card -->
				<div class="training-card">
					<div class="card-header">
						<div class="card-icon">
							<q-icon name="play_circle" size="32px" />
						</div>
						<div class="card-header-text">
							<div class="card-title">Готовы начать?</div>
							<div class="card-subtitle">Следуйте инструкциям шаг за шагом</div>
						</div>
					</div>

					<div class="card-divider"></div>

					<div class="card-features">
						<div class="feature-item">
							<q-icon name="touch_app" size="18px" class="feature-icon" />
							<div class="feature-text">
								<div class="feature-label">Интерактивность</div>
								<div class="feature-desc">Выполняйте действия на реальных скриншотах</div>
							</div>
						</div>
						<div class="feature-item">
							<q-icon name="lightbulb" size="18px" class="feature-icon" />
							<div class="feature-text">
								<div class="feature-label">Подсказки</div>
								<div class="feature-desc">Получайте помощь, если не знаете, что делать</div>
							</div>
						</div>
						<div class="feature-item">
							<q-icon name="check_circle" size="18px" class="feature-icon" />
							<div class="feature-text">
								<div class="feature-label">Прогресс</div>
								<div class="feature-desc">Отслеживайте свой путь к завершению</div>
							</div>
						</div>
					</div>

					<q-btn
						unelevated
						no-caps
						rounded
						color="primary"
						icon="play_arrow"
						label="Начать тренинг"
						size="lg"
						class="start-btn"
						@click="startTraining"
					/>
				</div>

				<!-- Additional Info -->
				<div v-if="trainingData.skip_steps" class="info-note">
					<q-icon name="info" size="16px" />
					<span>Вы можете проходить шаги в любом порядке</span>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { TrainingApi } from "@api";
import { useQuasar } from "quasar";

const route = useRoute();
const router = useRouter();
const $q = useQuasar();
const trainingApi = new TrainingApi();

const loading = ref(true);
const error = ref(false);
const errorMessage = ref("");
const trainingData = ref(null);

const stepsCount = computed(() => trainingData.value?.steps?.length || 0);

const stepsLabel = computed(() => {
	const count = stepsCount.value;
	if (count === 1) return "шаг";
	if (count >= 2 && count <= 4) return "шага";
	return "шагов";
});

async function loadTraining() {
	try {
		loading.value = true;
		error.value = false;
		
		const accessToken = route.params.accessToken;
		const { data } = await trainingApi.getPublicTraining(accessToken);
		
		trainingData.value = data;
	} catch (e) {
		error.value = true;
		if (e?.response?.status === 404) {
			errorMessage.value = "Тренинг не найден или доступ к нему закрыт";
		} else {
			errorMessage.value = "Не удалось загрузить тренинг. Проверьте ссылку.";
		}
	} finally {
		loading.value = false;
	}
}

function startTraining() {
	// TODO: Implement training flow
	$q.notify({
		message: "Функционал прохождения в разработке",
		color: "info",
		position: "top",
		icon: "info"
	});
}

onMounted(() => {
	loadTraining();
});
</script>

<style scoped>
.passage-page {
	min-height: 100vh;
	background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
	padding: 40px 20px;
	display: flex;
	align-items: center;
	justify-content: center;
}

/* ——— Loading State ——— */
.loading-container {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 16px;
}

.loading-text {
	font-size: 16px;
	color: #64748b;
	font-weight: 500;
}

/* ——— Error State ——— */
.error-container {
	max-width: 480px;
	width: 100%;
}

.error-card {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 20px;
	padding: 48px 32px;
	text-align: center;
}

.error-icon {
	width: 96px;
	height: 96px;
	border-radius: 24px;
	background: rgba(239, 68, 68, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(239, 68, 68, 0.7);
	margin: 0 auto 24px;
}

.error-title {
	font-size: 24px;
	font-weight: 600;
	color: #0f172a;
	margin-bottom: 12px;
}

.error-desc {
	font-size: 15px;
	color: #64748b;
	margin-bottom: 28px;
	line-height: 1.6;
}

.error-btn {
	padding: 10px 24px;
	font-size: 14px;
	font-weight: 500;
}

/* ——— Welcome Container ——— */
.welcome-container {
	max-width: 720px;
	width: 100%;
}

.welcome-content {
	display: flex;
	flex-direction: column;
	gap: 24px;
}

/* ——— Hero Section ——— */
.hero-section {
	text-align: center;
}

.hero-badge {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	padding: 6px 14px;
	background: rgba(80, 100, 247, 0.1);
	border: 1px solid rgba(80, 100, 247, 0.2);
	border-radius: 20px;
	font-size: 13px;
	font-weight: 600;
	color: rgba(80, 100, 247, 0.9);
	margin-bottom: 20px;
}

.hero-title {
	font-size: 36px;
	font-weight: 700;
	color: #0f172a;
	margin: 0 0 16px 0;
	letter-spacing: -0.02em;
	line-height: 1.2;
}

.hero-description {
	font-size: 17px;
	color: #475569;
	line-height: 1.6;
	margin: 0 0 28px 0;
}

/* ——— Metrics ——— */
.metrics-row {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 20px;
	flex-wrap: wrap;
	margin-bottom: 20px;
}

.metric-item {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 8px 16px;
	background: rgba(255, 255, 255, 0.7);
	border: 1px solid rgba(226, 232, 240, 0.8);
	border-radius: 10px;
	font-size: 14px;
	font-weight: 600;
	color: #334155;
	backdrop-filter: blur(8px);
}

.metric-item .q-icon {
	color: rgba(80, 100, 247, 0.7);
}

/* ——— Tags ——— */
.tags-row {
	display: flex;
	justify-content: center;
	flex-wrap: wrap;
	gap: 8px;
}

.tag-chip {
	background: rgba(255, 255, 255, 0.7);
	border: 1px solid rgba(226, 232, 240, 0.8);
	color: #475569;
	font-weight: 500;
	backdrop-filter: blur(8px);
}

/* ——— Training Card ——— */
.training-card {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 20px;
	padding: 32px;
	box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.card-header {
	display: flex;
	align-items: center;
	gap: 16px;
	margin-bottom: 24px;
}

.card-icon {
	width: 64px;
	height: 64px;
	border-radius: 16px;
	background: rgba(80, 100, 247, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(80, 100, 247, 0.9);
	flex-shrink: 0;
}

.card-header-text {
	flex: 1;
	min-width: 0;
}

.card-title {
	font-size: 20px;
	font-weight: 600;
	color: #0f172a;
	margin-bottom: 4px;
}

.card-subtitle {
	font-size: 14px;
	color: #64748b;
	line-height: 1.5;
}

.card-divider {
	height: 1px;
	background: #e2e8f0;
	margin-bottom: 24px;
}

/* ——— Features List ——— */
.card-features {
	display: flex;
	flex-direction: column;
	gap: 16px;
	margin-bottom: 28px;
}

.feature-item {
	display: flex;
	align-items: flex-start;
	gap: 14px;
}

.feature-icon {
	width: 40px;
	height: 40px;
	border-radius: 10px;
	background: #f8fafc;
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(80, 100, 247, 0.7);
	flex-shrink: 0;
	padding: 8px;
}

.feature-text {
	flex: 1;
	min-width: 0;
}

.feature-label {
	font-size: 15px;
	font-weight: 600;
	color: #0f172a;
	margin-bottom: 4px;
}

.feature-desc {
	font-size: 13px;
	color: #64748b;
	line-height: 1.5;
}

/* ——— Start Button ——— */
.start-btn {
	width: 100%;
	padding: 16px 32px;
	font-size: 16px;
	font-weight: 600;
	border-radius: 14px;
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.3);
	transition: all 0.2s ease;
}

.start-btn:hover {
	box-shadow: 0 6px 24px rgba(80, 100, 247, 0.4);
	transform: translateY(-2px);
}

/* ——— Info Note ——— */
.info-note {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	padding: 12px 20px;
	background: rgba(59, 130, 246, 0.08);
	border: 1px solid rgba(59, 130, 246, 0.15);
	border-radius: 12px;
	font-size: 13px;
	color: #1e40af;
	font-weight: 500;
}

.info-note .q-icon {
	color: rgba(59, 130, 246, 0.7);
}

/* ——— Responsive ——— */
@media (max-width: 768px) {
	.passage-page {
		padding: 24px 16px;
	}

	.hero-title {
		font-size: 28px;
	}

	.hero-description {
		font-size: 15px;
	}

	.metrics-row {
		gap: 12px;
	}

	.metric-item {
		font-size: 13px;
		padding: 6px 12px;
	}

	.training-card {
		padding: 24px;
	}

	.card-icon {
		width: 56px;
		height: 56px;
	}

	.card-title {
		font-size: 18px;
	}

	.start-btn {
		font-size: 15px;
		padding: 14px 28px;
	}
}
</style>