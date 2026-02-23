<template>
	<div class="passage-page" :class="{ 'passage-page--fullscreen': isPlayRoute }">
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

		<!-- Welcome (child route) -->
		<router-view v-else-if="trainingData" v-slot="{ Component }">
			<component :is="Component" :training-data="trainingData" />
		</router-view>
	</div>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { useRoute } from "vue-router";
import { TrainingApi } from "@api";

const route = useRoute();

const isPlayRoute = computed(() => route.name === "TrainingPlay");
const trainingApi = new TrainingApi();

const loading = ref(true);
const error = ref(false);
const errorMessage = ref("");
const trainingData = ref(null);

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

watch(
	() => route.params.accessToken,
	(accessToken) => {
		if (accessToken) {
			loadTraining();
		}
	},
	{ immediate: true }
);
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

.passage-page--fullscreen {
	padding: 0;
	height: 100vh;
	overflow: hidden;
	align-items: stretch;
}

.passage-page--fullscreen > * {
	flex: 1;
	min-height: 0;
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

/* ——— Responsive ——— */
@media (max-width: 768px) {
	.passage-page {
		padding: 24px 16px;
	}
}
</style>
