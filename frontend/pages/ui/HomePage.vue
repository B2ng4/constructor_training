<template>
	<div class="home-page">
		<div class="home-inner">
			<header class="home-hero animate-fade-in-up">
				<h1 class="home-hero__title">
					Добро пожаловать, {{ userStore.first_name || "Пользователь" }}
				</h1>
				<p class="home-hero__subtitle">
					Управляйте тренингами и следите за прогрессом
				</p>
			</header>

			<div v-if="loading" class="home-loading">
				<q-spinner-dots size="48px" color="primary" class="home-loading__spinner" />
				<p class="home-loading__text">Загрузка...</p>
			</div>

			<div v-else class="home-stack animate-stagger-children">
				<!-- Сводка -->
				<section class="home-panel" aria-labelledby="home-summary-heading">
					<div class="home-panel__head">
						<h2 id="home-summary-heading" class="home-panel__title">
							<q-icon name="insights" size="18px" class="home-panel__title-icon" />
							Сводка
						</h2>
					</div>
					<div class="stats-grid">
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
				</section>

				<!-- Быстрые действия -->
				<section class="home-panel" aria-labelledby="home-actions-heading">
					<div class="home-panel__head">
						<h2 id="home-actions-heading" class="home-panel__title">
							<q-icon name="bolt" size="18px" class="home-panel__title-icon" />
							Быстрые действия
						</h2>
					</div>
					<div class="quick-actions">
						<div
							class="action-item"
							role="button"
							tabindex="0"
							@click="$router.push('/personal/training')"
							@keydown.enter="$router.push('/personal/training')"
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
							role="button"
							tabindex="0"
							@click="$router.push('/personal/library')"
							@keydown.enter="$router.push('/personal/library')"
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
						<div
							class="action-item"
							role="button"
							tabindex="0"
							@click="$router.push('/personal/courses')"
							@keydown.enter="$router.push('/personal/courses')"
						>
							<div class="action-icon">
								<q-icon name="school" size="24px" />
							</div>
							<div class="action-content">
								<div class="action-title">Мои курсы</div>
								<div class="action-desc">Собрать и управлять курсами</div>
							</div>
							<q-icon name="arrow_forward" size="20px" class="action-arrow" />
						</div>
					</div>
				</section>

				<!-- Недавние или пустое состояние -->
				<section
					v-if="recentTrainings.length > 0"
					class="home-panel home-panel--grow"
					aria-labelledby="home-recent-heading"
				>
					<div class="home-panel__head">
						<h2 id="home-recent-heading" class="home-panel__title">
							<q-icon name="history" size="18px" class="home-panel__title-icon" />
							Недавние тренинги
						</h2>
						<q-btn
							flat
							dense
							no-caps
							color="primary"
							label="Все тренинги"
							to="/personal/training"
							class="home-panel__link"
						/>
					</div>
					<div class="trainings-grid">
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
									{{ training.publish ? "Опубликован" : "Черновик" }}
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
				</section>

				<section
					v-else
					class="home-panel home-panel--empty animate-scale-in"
					aria-labelledby="home-empty-heading"
				>
					<div class="empty-inner">
						<div class="empty-icon" aria-hidden="true">
							<q-icon name="school" size="48px" />
						</div>
						<h2 id="home-empty-heading" class="empty-title">У вас пока нет тренингов</h2>
						<p class="empty-desc">Создайте первый тренинг, чтобы начать работу</p>
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
				</section>
			</div>
		</div>
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

const recentTrainings = computed(() => trainings.value.slice(0, 6));

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
	padding: 24px 24px 40px;
	min-height: 100%;
	box-sizing: border-box;
}

/* Вровень с шапкой и списком тренингов: колонка слева, без «острова» по центру экрана */
.home-inner {
	max-width: 960px;
	margin-left: 0;
	margin-right: auto;
	width: 100%;
}

/* ——— Hero ——— */
.home-hero {
	margin-bottom: 24px;
}

.home-hero__title {
	font-size: 26px;
	font-weight: 700;
	color: #1a1a2e;
	margin: 0 0 8px 0;
	letter-spacing: -0.02em;
	line-height: 1.2;
}

.home-hero__subtitle {
	font-size: 15px;
	color: #64748b;
	margin: 0;
	font-weight: 400;
	line-height: 1.45;
	max-width: 36em;
}

/* ——— Loading ——— */
.home-loading {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 56px 0;
	gap: 16px;
}

.home-loading__spinner {
	animation: pulse-soft 1.2s var(--anim-ease-in-out) infinite;
}

.home-loading__text {
	font-size: 14px;
	color: #64748b;
	margin: 0;
	font-weight: 500;
}

/* ——— Stack & panels ——— */
.home-stack {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.home-panel {
	background: #fafbfc;
	border: 1px solid rgba(26, 26, 46, 0.08);
	border-radius: 14px;
	padding: 20px 22px 22px;
	box-shadow: none;
}

.home-panel--grow {
	flex: 1;
	min-height: 0;
}

.home-panel__head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	margin-bottom: 18px;
	flex-wrap: wrap;
}

.home-panel__title {
	display: flex;
	align-items: center;
	gap: 8px;
	margin: 0;
	font-size: 13px;
	font-weight: 600;
	color: #374151;
	text-transform: uppercase;
	letter-spacing: 0.05em;
}

.home-panel__title-icon {
	color: #5064f7;
	opacity: 0.9;
}

.home-panel__link {
	font-size: 13px;
	font-weight: 600;
	margin: -4px -8px -4px 0;
}

/* ——— Stats ——— */
.stats-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 14px;
}

.stat-card {
	background: #f5f6fa;
	border: 1px solid rgba(26, 26, 46, 0.06);
	border-radius: 12px;
	padding: 16px;
	display: flex;
	align-items: flex-start;
	gap: 12px;
	transition: border-color 0.2s ease, background 0.2s ease;
}

.stat-card:hover {
	border-color: rgba(26, 26, 46, 0.1);
	background: #f0f2f6;
}

.stat-icon {
	width: 40px;
	height: 40px;
	border-radius: 10px;
	background: rgba(80, 100, 247, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #5064f7;
	flex-shrink: 0;
}

.stat-card--success .stat-icon {
	background: rgba(16, 185, 129, 0.12);
	color: #059669;
}

.stat-card--draft .stat-icon {
	background: rgba(148, 163, 184, 0.15);
	color: #64748b;
}

.stat-content {
	flex: 1;
	min-width: 0;
}

.stat-value {
	font-size: 22px;
	font-weight: 700;
	color: #1a1a2e;
	line-height: 1.2;
	margin-bottom: 2px;
}

.stat-label {
	font-size: 12px;
	color: #64748b;
	font-weight: 500;
	line-height: 1.3;
}

/* ——— Quick actions ——— */
.quick-actions {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 12px;
}

.action-item {
	background: #f5f6fa;
	border: 1px solid rgba(26, 26, 46, 0.06);
	border-radius: 12px;
	padding: 16px 18px;
	display: flex;
	align-items: center;
	gap: 14px;
	cursor: pointer;
	transition: border-color 0.2s ease, background 0.2s ease;
	outline: none;
}

.action-item:hover,
.action-item:focus-visible {
	border-color: rgba(80, 100, 247, 0.3);
	background: rgba(80, 100, 247, 0.06);
}

.action-item:focus-visible {
	box-shadow: 0 0 0 2px rgba(80, 100, 247, 0.22);
}

.action-item:hover .action-arrow,
.action-item:focus-visible .action-arrow {
	transform: translateX(3px);
	color: #5064f7;
}

.action-icon {
	width: 44px;
	height: 44px;
	border-radius: 12px;
	background: rgba(80, 100, 247, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #5064f7;
	flex-shrink: 0;
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
	color: #1a1a2e;
	margin-bottom: 4px;
}

.action-desc {
	font-size: 12px;
	color: #64748b;
	line-height: 1.4;
}

.action-arrow {
	color: #cbd5e1;
	transition: transform 0.2s ease, color 0.2s ease;
	flex-shrink: 0;
}

/* ——— Recent trainings ——— */
.trainings-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
	gap: 12px;
}

.training-card {
	background: #f5f6fa;
	border: 1px solid rgba(26, 26, 46, 0.06);
	border-radius: 12px;
	padding: 14px 16px;
	cursor: pointer;
	transition: border-color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.training-card:hover {
	border-color: rgba(80, 100, 247, 0.28);
	background: #eef0f4;
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
	color: #1a1a2e;
	line-height: 1.35;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
}

.training-status {
	font-size: 11px;
	font-weight: 600;
	padding: 4px 8px;
	border-radius: 6px;
	white-space: nowrap;
	flex-shrink: 0;
}

.training-status--published {
	background: rgba(16, 185, 129, 0.12);
	color: #059669;
}

.training-status--draft {
	background: rgba(148, 163, 184, 0.15);
	color: #64748b;
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

/* ——— Empty ——— */
.home-panel--empty {
	padding: 40px 28px;
}

.empty-inner {
	max-width: 400px;
	margin: 0 auto;
	text-align: center;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.empty-icon {
	width: 80px;
	height: 80px;
	border-radius: 20px;
	background: rgba(80, 100, 247, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #5064f7;
	opacity: 0.85;
	margin-bottom: 20px;
}

.empty-title {
	font-size: 17px;
	font-weight: 600;
	color: #1a1a2e;
	margin: 0 0 8px 0;
}

.empty-desc {
	font-size: 14px;
	color: #64748b;
	margin: 0 0 22px 0;
	line-height: 1.45;
}

.empty-btn {
	border-radius: 12px;
	padding: 10px 22px;
	font-weight: 600;
}

/* ——— Responsive ——— */
@media (max-width: 640px) {
	.home-page {
		padding: 20px 16px 32px;
	}

	.home-hero__title {
		font-size: 22px;
	}

	.stats-grid {
		grid-template-columns: 1fr;
	}

	.quick-actions {
		grid-template-columns: 1fr;
	}

	.trainings-grid {
		grid-template-columns: 1fr;
	}
}

</style>
