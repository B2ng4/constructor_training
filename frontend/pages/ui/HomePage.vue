<template>
	<div class="home-page">
		<div class="page-header animate-fade-in-up">
			<h1 class="page-title">
				Добро пожаловать, {{ userStore.first_name || "Пользователь" }}
			</h1>
			<p class="page-subtitle">
				Управляйте тренингами и следите за прогрессом
			</p>
		</div>

		<div v-if="loading" class="loading-state">
			<q-spinner-dots size="48px" color="primary" class="loading-spinner" />
			<p class="loading-text">Загрузка...</p>
		</div>

		<template v-else>
			<!-- Статистика -->
			<div class="stats-grid animate-stagger-children">
				<div class="stat-card">
					<div class="stat-icon">
						<q-icon name="school" size="20px" />
					</div>
					<div class="stat-content">
						<div class="stat-value">{{ stats.totalTrainings }}</div>
						<div class="stat-label">Всего тренингов</div>
					</div>
				</div>
				<div class="stat-card stat-card--success">
					<div class="stat-icon">
						<q-icon name="check_circle" size="20px" />
					</div>
					<div class="stat-content">
						<div class="stat-value">{{ stats.publishedTrainings }}</div>
						<div class="stat-label">Опубликовано</div>
					</div>
				</div>
				<div class="stat-card stat-card--draft">
					<div class="stat-icon">
						<q-icon name="edit_note" size="20px" />
					</div>
					<div class="stat-content">
						<div class="stat-value">{{ stats.draftTrainings }}</div>
						<div class="stat-label">Черновиков</div>
					</div>
				</div>
			</div>

			<!-- Быстрые действия -->
			<div class="quick-actions animate-stagger-children">
				<div
					class="action-item"
					@click="$router.push('/personal/training')"
				>
					<div class="action-icon">
						<q-icon name="add_circle_outline" size="24px" />
					</div>
					<div class="action-content">
						<div class="action-title">Создать тренинг</div>
						<div class="action-desc">Добавить новый интерактивный тренинг</div>
					</div>
					<q-icon name="arrow_forward" size="20px" class="action-arrow" />
				</div>
				<div
					class="action-item"
					@click="$router.push('/personal/library')"
				>
					<div class="action-icon">
						<q-icon name="library_books" size="24px" />
					</div>
					<div class="action-content">
						<div class="action-title">Библиотека</div>
						<div class="action-desc">Каталог всех тренингов</div>
					</div>
					<q-icon name="arrow_forward" size="20px" class="action-arrow" />
				</div>
			</div>

			<!-- Последние тренинги -->
			<div v-if="recentTrainings.length > 0" class="recent-section">
				<div class="section-header animate-fade-in-up animate-stagger-3">
					<h2 class="section-title">Недавние тренинги</h2>
					<q-btn
						flat
						dense
						no-caps
						color="grey-8"
						label="Все тренинги"
						to="/personal/training"
						class="section-action"
					/>
				</div>
				<div class="trainings-grid animate-stagger-children">
					<div
						v-for="training in recentTrainings"
						:key="training.uuid"
						class="training-card"
						@click="openEdit(training.uuid)"
					>
						<div class="training-header">
							<div class="training-title">{{ training.title }}</div>
							<div
								class="training-status"
								:class="training.publish ? 'training-status--published' : 'training-status--draft'"
							>
								{{ training.publish ? 'Опубликован' : 'Черновик' }}
							</div>
						</div>
						<div class="training-meta">
							<div class="training-meta-item">
								<q-icon name="layers" size="14px" />
								<span>{{ training.steps?.length || 0 }} шагов</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div v-else class="empty-state animate-scale-in">
				<div class="empty-icon">
					<q-icon name="school" size="48px" />
				</div>
				<div class="empty-title">У вас пока нет тренингов</div>
				<div class="empty-desc">Создайте первый тренинг, чтобы начать работу</div>
				<q-btn
					unelevated
					no-caps
					rounded
					color="primary"
					icon="add"
					label="Создать тренинг"
					class="empty-btn"
					@click="$router.push('/personal/training')"
				/>
			</div>
		</template>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@store/userData.js";
import { TrainingApi } from "@api";

const router = useRouter();
const userStore = useUserStore();
const trainingApi = new TrainingApi();
const loading = ref(true);
const trainings = ref([]);

const stats = computed(() => ({
	totalTrainings: trainings.value.length,
	publishedTrainings: trainings.value.filter((t) => t.publish).length,
	draftTrainings: trainings.value.filter((t) => !t.publish).length,
}));

const recentTrainings = computed(() =>
	trainings.value.slice(0, 6)
);

function openEdit(uuid) {
	const route = router.resolve(`/edit/${uuid}`);
	window.open(route.href, "_blank");
}

onMounted(async () => {
	try {
		const { data } = await trainingApi.getTrainings();
		trainings.value = data || [];
	} catch {
		trainings.value = [];
	} finally {
		loading.value = false;
	}
});
</script>

<style scoped>
.home-page {
	padding: 32px 40px 24px;
	height: calc(100vh - 56px);
	overflow-y: auto;
	display: flex;
	flex-direction: column;
}

/* ——— Header ——— */
.page-header {
	margin-bottom: 32px;
	flex-shrink: 0;
}

.page-title {
	font-size: 28px;
	font-weight: 600;
	color: #0f172a;
	margin: 0 0 6px 0;
	letter-spacing: -0.02em;
}

.page-subtitle {
	font-size: 15px;
	color: #64748b;
	margin: 0;
	font-weight: 400;
}

/* ——— Loading ——— */
.loading-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 60px 0;
	flex: 1;
	gap: 16px;
}
.loading-spinner {
	animation: pulse-soft 1.2s var(--anim-ease-in-out) infinite;
}
.loading-text {
	font-size: 14px;
	color: #64748b;
	margin: 0;
	font-weight: 500;
}

/* ——— Stats Grid ——— */
.stats-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	gap: 12px;
	margin-bottom: 32px;
	flex-shrink: 0;
}

.stat-card {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 14px;
	padding: 20px;
	display: flex;
	align-items: flex-start;
	gap: 14px;
	transition: border-color 0.25s ease, box-shadow 0.25s var(--anim-ease-out), transform 0.25s var(--anim-ease-spring);
}
.stat-card:hover {
	border-color: #cbd5e1;
	box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
	transform: translateY(-2px);
}
.stat-card:active {
	transform: translateY(0);
}

.stat-icon {
	width: 40px;
	height: 40px;
	border-radius: 12px;
	background: rgba(80, 100, 247, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(80, 100, 247, 0.9);
	flex-shrink: 0;
	transition: transform 0.3s var(--anim-ease-spring);
}
.stat-card:hover .stat-icon {
	transform: scale(1.08);
}

.stat-card--success .stat-icon {
	background: rgba(34, 197, 94, 0.08);
	color: rgba(34, 197, 94, 0.9);
}

.stat-card--draft .stat-icon {
	background: rgba(148, 163, 184, 0.08);
	color: rgba(100, 116, 139, 0.9);
}

.stat-content {
	flex: 1;
	min-width: 0;
}

.stat-value {
	font-size: 24px;
	font-weight: 700;
	color: #0f172a;
	line-height: 1.2;
	margin-bottom: 2px;
}

.stat-label {
	font-size: 12px;
	color: #64748b;
	font-weight: 500;
}

/* ——— Quick Actions ——— */
.quick-actions {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
	gap: 12px;
	margin-bottom: 32px;
	flex-shrink: 0;
}

.action-item {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 14px;
	padding: 18px 20px;
	display: flex;
	align-items: center;
	gap: 14px;
	cursor: pointer;
	transition: border-color 0.25s ease, background 0.25s ease, box-shadow 0.25s var(--anim-ease-out), transform 0.25s var(--anim-ease-spring);
}
.action-item:hover {
	border-color: rgba(80, 100, 247, 0.35);
	background: rgba(80, 100, 247, 0.04);
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.08);
	transform: translateY(-2px);
}
.action-item:active {
	transform: translateY(0);
}
.action-item:hover .action-arrow {
	transform: translateX(4px);
	color: rgba(80, 100, 247, 0.9);
}
.action-item:hover .action-icon {
	transform: scale(1.05);
}

.action-icon {
	width: 44px;
	height: 44px;
	border-radius: 12px;
	background: rgba(80, 100, 247, 0.06);
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(80, 100, 247, 0.9);
	flex-shrink: 0;
	transition: transform 0.3s var(--anim-ease-spring);
}

.action-icon .q-icon {
	font-size: 22px;
}

.action-content {
	flex: 1;
	min-width: 0;
}

.action-title {
	font-size: 14px;
	font-weight: 600;
	color: #0f172a;
	margin-bottom: 3px;
}

.action-desc {
	font-size: 12px;
	color: #64748b;
	line-height: 1.4;
}

.action-arrow {
	color: #cbd5e1;
	transition: all 0.2s ease;
	flex-shrink: 0;
}

/* ——— Recent Section ——— */
.recent-section {
	margin-bottom: 24px;
	flex: 1;
	min-height: 0;
	display: flex;
	flex-direction: column;
}

.section-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 16px;
	flex-shrink: 0;
}

.section-title {
	font-size: 18px;
	font-weight: 600;
	color: #0f172a;
	margin: 0;
}

.section-action {
	font-size: 14px;
	font-weight: 500;
}

.trainings-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
	gap: 12px;
	overflow-y: auto;
	flex: 1;
	align-content: start;
}

.training-card {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 14px;
	padding: 16px;
	cursor: pointer;
	transition: border-color 0.25s ease, box-shadow 0.25s var(--anim-ease-out), transform 0.25s var(--anim-ease-spring);
	height: fit-content;
}
.training-card:hover {
	border-color: rgba(80, 100, 247, 0.25);
	box-shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
	transform: translateY(-3px);
}
.training-card:active {
	transform: translateY(-1px);
}

.training-header {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	gap: 10px;
	margin-bottom: 10px;
}

.training-title {
	flex: 1;
	font-size: 14px;
	font-weight: 600;
	color: #0f172a;
	line-height: 1.4;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
}

.training-status {
	font-size: 11px;
	font-weight: 600;
	padding: 4px 10px;
	border-radius: 6px;
	white-space: nowrap;
	flex-shrink: 0;
}

.training-status--published {
	background: rgba(34, 197, 94, 0.1);
	color: rgba(34, 197, 94, 0.9);
}

.training-status--draft {
	background: rgba(148, 163, 184, 0.1);
	color: rgba(100, 116, 139, 0.9);
}

.training-meta {
	display: flex;
	align-items: center;
	gap: 12px;
}

.training-meta-item {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 13px;
	color: #64748b;
}

/* ——— Empty State ——— */
.empty-state {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 16px;
	padding: 48px 32px;
	text-align: center;
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.empty-icon {
	width: 80px;
	height: 80px;
	border-radius: 22px;
	background: rgba(80, 100, 247, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(80, 100, 247, 0.6);
	margin-bottom: 20px;
	transition: transform 0.4s var(--anim-ease-spring), background 0.3s ease;
}
.empty-state:hover .empty-icon {
	transform: scale(1.05);
	background: rgba(80, 100, 247, 0.1);
}

.empty-title {
	font-size: 18px;
	font-weight: 600;
	color: #0f172a;
	margin-bottom: 8px;
}

.empty-desc {
	font-size: 14px;
	color: #64748b;
	margin-bottom: 24px;
}

.empty-btn {
	border-radius: 12px;
	padding: 10px 24px;
	font-size: 14px;
	font-weight: 500;
	box-shadow: 0 2px 8px rgba(80, 100, 247, 0.25);
	transition: box-shadow 0.25s ease, transform 0.25s var(--anim-ease-spring);
}
.empty-btn:hover {
	box-shadow: 0 4px 20px rgba(80, 100, 247, 0.35);
	transform: translateY(-2px);
}
.empty-btn:active {
	transform: translateY(0);
}

/* ——— Responsive ——— */
@media (max-width: 768px) {
	.home-page {
		padding: 24px 16px 20px;
	}
	
	.page-header {
		margin-bottom: 24px;
	}
	
	.page-title {
		font-size: 24px;
	}
	
	.page-subtitle {
		font-size: 14px;
	}
	
	.stats-grid {
		grid-template-columns: 1fr;
		gap: 10px;
		margin-bottom: 24px;
	}
	
	.quick-actions {
		grid-template-columns: 1fr;
		gap: 10px;
		margin-bottom: 24px;
	}
	
	.trainings-grid {
		grid-template-columns: 1fr;
		gap: 10px;
	}
}
</style>
