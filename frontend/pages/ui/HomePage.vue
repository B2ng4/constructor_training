<template>
	<div class="home-page">
		<div class="home-page__bg" aria-hidden="true">
			<div class="home-page__orb home-page__orb--1" />
			<div class="home-page__orb home-page__orb--2" />
		</div>

		<div class="home-page__inner">
			<!-- Header -->
			<header class="home-header">
				<div class="home-header__text">
					<h1 class="home-header__title">
						{{ userStore.isEmployee ? "Мои тренинги" : `${greeting}, ${userStore.fullName}` }}
					</h1>
					<p class="home-header__subtitle">
						{{ userStore.isEmployee
							? "Тренинги, назначенные вашей организацией"
							: "Управляйте обучением и отслеживайте прогресс в одном месте" }}
					</p>
				</div>
				<q-btn
					v-if="!userStore.isEmployee"
					unelevated
					no-caps
					color="primary"
					icon="add"
					label="Создать тренинг"
					to="/personal/training"
					class="page-cta"
				/>
			</header>

			<!-- Loading -->
			<div v-if="loading" class="home-loading">
				<q-spinner-dots size="44px" color="primary" />
				<p class="home-loading__text">Загрузка данных…</p>
			</div>

			<!-- Employee view -->
			<template v-else-if="userStore.isEmployee">
				<section class="home-section">
					<div class="home-section__head">
						<h2 class="home-section__title">
							<q-icon name="school" size="20px" class="home-section__title-icon" />
							Доступные тренинги
						</h2>
					</div>
					<div v-if="assignedTrainings.length" class="trainings-grid">
						<div
							v-for="item in assignedTrainings"
							:key="`${item.organization_id}-${item.training_uuid}`"
							class="training-card training-card--assigned"
							v-ripple
							@click="openAssigned(item)"
						>
							<div class="training-card__thumb training-card__thumb--accent">
								<q-icon name="school" size="28px" />
							</div>
							<div class="training-card__body">
								<h3 class="training-card__title">{{ item.title }}</h3>
								<div class="training-card__meta">
									<q-icon name="business" size="14px" />
									<span>{{ item.organization_name }}</span>
								</div>
							</div>
							<q-icon name="play_circle" size="22px" class="training-card__play" />
						</div>
					</div>
					<div v-else class="empty-card">
						<div class="empty-card__icon">
							<q-icon name="school" size="40px" />
						</div>
						<h3 class="empty-card__title">Пока нет назначенных тренингов</h3>
						<p class="empty-card__desc">Когда организация назначит тренинг, он появится здесь.</p>
					</div>
				</section>
			</template>

			<!-- Creator view -->
			<template v-else>
				<!-- Stats -->
				<section class="stats-row">
					<div
						v-for="stat in statsList"
						:key="stat.key"
						class="stat-card"
					>
						<div class="stat-card__icon">
							<q-icon :name="stat.icon" size="24px" />
						</div>
						<div class="stat-card__body">
							<div class="stat-card__value">{{ stat.value }}</div>
							<div class="stat-card__label">{{ stat.label }}</div>
						</div>
					</div>
				</section>

				<!-- Quick actions -->
				<section class="quick-row">
					<div
						v-for="action in quickActions"
						:key="action.title"
						class="quick-card"
						v-ripple
						tabindex="0"
						role="button"
						@click="$router.push(action.to)"
						@keydown.enter="$router.push(action.to)"
					>
						<div
							class="quick-card__icon"
							:style="{ background: action.iconBg, color: action.iconColor }"
						>
							<q-icon :name="action.icon" size="24px" />
						</div>
						<div class="quick-card__content">
							<div class="quick-card__title">{{ action.title }}</div>
							<div class="quick-card__desc">{{ action.desc }}</div>
						</div>
						<q-icon name="arrow_forward" size="20px" class="quick-card__arrow" />
					</div>
				</section>

				<!-- Recent trainings -->
				<section class="home-section home-section--grow">
					<div class="home-section__head">
						<h2 class="home-section__title">
							<q-icon name="history" size="20px" class="home-section__title-icon" />
							Недавние тренинги
						</h2>
						<q-btn
							flat
							dense
							no-caps
							color="primary"
							icon="arrow_forward"
							label="Все тренинги"
							to="/personal/training"
							class="home-section__link"
						/>
					</div>

					<div v-if="recentTrainings.length" class="trainings-grid">
						<div
							v-for="training in recentTrainings"
							:key="training.uuid"
							class="training-card"
							v-ripple
							@click="openEdit(training.uuid)"
						>
							<div class="training-card__top">
								<div class="training-card__thumb">
									<q-icon name="school" size="24px" />
								</div>
								<span
									class="training-card__status"
									:class="training.publish ? 'training-card__status--published' : 'training-card__status--draft'"
								>
									{{ training.publish ? "Опубликован" : "Черновик" }}
								</span>
							</div>
							<h3 class="training-card__title">{{ training.title }}</h3>
							<div class="training-card__meta">
								<q-icon name="layers" size="14px" />
								<span>{{ training.steps_count ?? training.steps?.length ?? 0 }} шагов</span>
							</div>
							<div class="training-card__footer">
								<span class="training-card__action">Открыть редактор</span>
								<q-icon name="open_in_new" size="16px" />
							</div>
						</div>
					</div>

					<div v-else class="empty-card">
						<div class="empty-card__icon">
							<q-icon name="lightbulb" size="40px" />
						</div>
						<h3 class="empty-card__title">Создайте первый тренинг</h3>
						<p class="empty-card__desc">
							Загрузите скриншоты или видео, добавьте интерактивные шаги и опубликуйте обучение.
						</p>
						<q-btn
							unelevated
							no-caps
							color="primary"
							icon="add"
							label="Создать тренинг"
							to="/personal/training"
							class="empty-card__btn"
						/>
					</div>
				</section>
			</template>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@store/userData.js";
import { TrainingApi, organizationApi } from "@api";

const router = useRouter();
const userStore = useUserStore();
const trainingApi = new TrainingApi();
const loading = ref(true);
const trainings = ref([]);
const assignedTrainings = ref([]);

const greeting = computed(() => {
	const hour = new Date().getHours();
	if (hour < 6) return "Доброй ночи";
	if (hour < 12) return "Доброе утро";
	if (hour < 18) return "Добрый день";
	return "Добрый вечер";
});

const stats = computed(() => ({
	totalTrainings: trainings.value.length,
	publishedTrainings: trainings.value.filter((t) => t.publish).length,
	draftTrainings: trainings.value.filter((t) => !t.publish).length,
}));

const statsList = computed(() => [
	{
		key: "total",
		value: stats.value.totalTrainings,
		label: "Всего тренингов",
		icon: "school",
	},
	{
		key: "published",
		value: stats.value.publishedTrainings,
		label: "Опубликовано",
		icon: "check_circle",
	},
	{
		key: "drafts",
		value: stats.value.draftTrainings,
		label: "Черновиков",
		icon: "edit_note",
	},
]);

const quickActions = [
	{
		title: "Создать тренинг",
		desc: "Начните с загрузки скриншотов или видео",
		icon: "add_circle_outline",
		to: "/personal/training",
		iconBg: "rgba(80, 100, 247, 0.10)",
		iconColor: "#5064f7",
	},
	{
		title: "Библиотека",
		desc: "Каталог всех тренингов",
		icon: "library_books",
		to: "/personal/library",
		iconBg: "rgba(16, 185, 129, 0.10)",
		iconColor: "#10b981",
	},
	{
		title: "Мои курсы",
		desc: "Собирайте и управляйте курсами",
		icon: "school",
		to: "/personal/courses",
		iconBg: "rgba(245, 158, 11, 0.10)",
		iconColor: "#f59e0b",
	},
];

const recentTrainings = computed(() => trainings.value.slice(0, 6));

function openEdit(uuid) {
	const route = router.resolve(`/edit/${uuid}`);
	window.open(route.href, "_blank");
}

function openAssigned(item) {
	if (item.public_link) {
		router.push(item.public_link);
	}
}

onMounted(async () => {
	if (!userStore.isLoaded) {
		await userStore.fetchUser();
	}
	try {
		if (userStore.isEmployee) {
			const { data } = await organizationApi.assignedTrainings();
			assignedTrainings.value = data || [];
		} else {
			const { data } = await trainingApi.getTrainings();
			trainings.value = data || [];
		}
	} catch {
		trainings.value = [];
		assignedTrainings.value = [];
	} finally {
		loading.value = false;
	}
});
</script>

<style scoped>
.home-page {
	position: relative;
	min-height: 100%;
	padding: 0;
	background: transparent;
}

.home-page__bg {
	position: fixed;
	inset: 0;
	pointer-events: none;
	z-index: 0;
	overflow: hidden;
}

.home-page__orb {
	position: absolute;
	border-radius: 50%;
	filter: blur(90px);
	opacity: 0.35;
}

.home-page__orb--1 {
	width: 560px;
	height: 560px;
	top: -180px;
	right: -120px;
	background: radial-gradient(circle, rgba(80, 100, 247, 0.35) 0%, rgba(80, 100, 247, 0) 70%);
}

.home-page__orb--2 {
	width: 420px;
	height: 420px;
	bottom: -120px;
	left: -120px;
	background: radial-gradient(circle, rgba(16, 185, 129, 0.22) 0%, rgba(16, 185, 129, 0) 70%);
}

.home-page__inner {
	position: relative;
	z-index: 1;
	max-width: 1200px;
	margin: 0 auto;
	padding: 36px 32px 56px;
	display: flex;
	flex-direction: column;
	gap: 28px;
}

/* Header */
.home-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 24px;
	margin-bottom: 4px;
}

.home-header__text {
	min-width: 0;
}

.home-header__title {
	font-size: 34px;
	font-weight: 750;
	color: #0f172a;
	margin: 0 0 6px;
	letter-spacing: -0.03em;
	line-height: 1.15;
}

.home-header__subtitle {
	font-size: 16px;
	color: #64748b;
	margin: 0;
	font-weight: 450;
	line-height: 1.5;
	max-width: 520px;
}

.home-header__cta {
	border-radius: 14px;
	padding: 10px 22px;
	font-weight: 600;
	font-size: 15px;
	box-shadow: 0 4px 14px rgba(80, 100, 247, 0.28);
	flex-shrink: 0;
	transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.home-header__cta:hover {
	transform: translateY(-1px);
	box-shadow: 0 6px 20px rgba(80, 100, 247, 0.35);
}

/* Loading */
.home-loading {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 80px 0;
	gap: 16px;
}

.home-loading__text {
	font-size: 15px;
	color: #64748b;
	margin: 0;
	font-weight: 500;
}

/* Sections */
.home-section {
	background: rgba(255, 255, 255, 0.82);
	backdrop-filter: blur(28px);
	-webkit-backdrop-filter: blur(28px);
	border: 1px solid rgba(0, 0, 0, 0.05);
	border-radius: 24px;
	padding: 26px 28px;
	box-shadow: 0 10px 34px rgba(15, 23, 42, 0.04);
}

.home-section--grow {
	flex: 1;
}

.home-section__head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 16px;
	margin-bottom: 22px;
	flex-wrap: wrap;
}

.home-section__title {
	display: flex;
	align-items: center;
	gap: 10px;
	margin: 0;
	font-size: 17px;
	font-weight: 700;
	color: #0f172a;
	letter-spacing: -0.01em;
}

.home-section__title-icon {
	color: #5064f7;
	background: rgba(80, 100, 247, 0.10);
	padding: 7px;
	border-radius: 10px;
}

.home-section__link {
	font-size: 14px;
	font-weight: 600;
	border-radius: 10px;
	margin: -4px -8px -4px 0;
}

/* Stats row */
.stats-row {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20px;
}

.stat-card {
	background: rgba(255, 255, 255, 0.85);
	backdrop-filter: blur(28px);
	-webkit-backdrop-filter: blur(28px);
	border: 1px solid rgba(0, 0, 0, 0.05);
	border-radius: 20px;
	padding: 22px 24px;
	display: flex;
	align-items: center;
	gap: 16px;
	box-shadow: 0 8px 28px rgba(15, 23, 42, 0.04);
	transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.stat-card:hover {
	transform: translateY(-2px);
	box-shadow: 0 12px 32px rgba(80, 100, 247, 0.08);
}

.stat-card__icon {
	width: 50px;
	height: 50px;
	border-radius: 14px;
	background: rgba(80, 100, 247, 0.10);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #5064f7;
	flex-shrink: 0;
}

.stat-card__body {
	flex: 1;
	min-width: 0;
}

.stat-card__value {
	font-size: 30px;
	font-weight: 800;
	color: #0f172a;
	line-height: 1.1;
	letter-spacing: -0.03em;
	margin-bottom: 4px;
}

.stat-card__label {
	font-size: 13px;
	color: #64748b;
	font-weight: 600;
	letter-spacing: 0.02em;
}

/* Quick actions */
.quick-row {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20px;
}

.quick-card {
	background: rgba(255, 255, 255, 0.85);
	backdrop-filter: blur(28px);
	-webkit-backdrop-filter: blur(28px);
	border: 1px solid rgba(0, 0, 0, 0.05);
	border-radius: 20px;
	padding: 22px 24px;
	display: flex;
	align-items: center;
	gap: 16px;
	cursor: pointer;
	outline: none;
	box-shadow: 0 8px 28px rgba(15, 23, 42, 0.04);
	transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.quick-card:hover,
.quick-card:focus-visible {
	transform: translateY(-2px);
	box-shadow: 0 14px 34px rgba(80, 100, 247, 0.10);
	border-color: rgba(80, 100, 247, 0.2);
}

.quick-card:focus-visible {
	box-shadow: 0 0 0 3px rgba(80, 100, 247, 0.25);
}

.quick-card__icon {
	width: 52px;
	height: 52px;
	border-radius: 14px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	transition: transform 0.25s ease;
}

.quick-card:hover .quick-card__icon {
	transform: scale(1.05);
}

.quick-card__content {
	flex: 1;
	min-width: 0;
}

.quick-card__title {
	font-size: 15px;
	font-weight: 700;
	color: #0f172a;
	margin-bottom: 3px;
}

.quick-card__desc {
	font-size: 13px;
	color: #64748b;
	line-height: 1.4;
}

.quick-card__arrow {
	color: #cbd5e1;
	transition: transform 0.25s ease, color 0.25s ease;
	flex-shrink: 0;
}

.quick-card:hover .quick-card__arrow {
	transform: translateX(4px);
	color: #5064f7;
}

/* Training cards */
.trainings-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
	gap: 18px;
}

.training-card {
	background: rgba(255, 255, 255, 0.88);
	backdrop-filter: blur(28px);
	-webkit-backdrop-filter: blur(28px);
	border: 1px solid rgba(0, 0, 0, 0.05);
	border-radius: 20px;
	padding: 22px;
	cursor: pointer;
	transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
	display: flex;
	flex-direction: column;
	min-height: 172px;
	box-shadow: 0 8px 24px rgba(15, 23, 42, 0.03);
}

.training-card:hover {
	transform: translateY(-3px);
	box-shadow: 0 16px 40px rgba(80, 100, 247, 0.10);
	border-color: rgba(80, 100, 247, 0.18);
}

.training-card__top {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
	gap: 12px;
	margin-bottom: 16px;
}

.training-card__thumb {
	width: 52px;
	height: 52px;
	border-radius: 14px;
	background: rgba(80, 100, 247, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #5064f7;
	flex-shrink: 0;
}

.training-card__thumb--accent {
	background: rgba(80, 100, 247, 0.12);
}

.training-card__status {
	font-size: 11px;
	font-weight: 700;
	padding: 5px 10px;
	border-radius: 20px;
	white-space: nowrap;
	letter-spacing: 0.03em;
}

.training-card__status--published {
	background: rgba(16, 185, 129, 0.10);
	color: #059669;
}

.training-card__status--draft {
	background: rgba(100, 116, 139, 0.10);
	color: #475569;
}

.training-card__title {
	font-size: 16px;
	font-weight: 700;
	color: #0f172a;
	line-height: 1.35;
	margin: 0 0 14px;
	letter-spacing: -0.01em;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
}

.training-card__meta {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 13px;
	font-weight: 500;
	color: #64748b;
	margin-top: auto;
	padding-top: 14px;
	border-top: 1px solid #f1f5f9;
}

.training-card__footer {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 8px;
	margin-top: 14px;
	padding-top: 12px;
	border-top: 1px solid #f1f5f9;
}

.training-card__action {
	font-size: 13px;
	font-weight: 700;
	color: #5064f7;
}

.training-card__play {
	color: rgba(80, 100, 247, 0.35);
	transition: color 0.25s ease, transform 0.25s ease;
}

.training-card--assigned:hover .training-card__play {
	color: #5064f7;
	transform: scale(1.08);
}

/* Empty card */
.empty-card {
	text-align: center;
	padding: 52px 28px;
	border: 2px dashed rgba(15, 23, 42, 0.08);
	border-radius: 24px;
	background: rgba(255, 255, 255, 0.55);
}

.empty-card__icon {
	width: 80px;
	height: 80px;
	border-radius: 22px;
	background: rgba(80, 100, 247, 0.10);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #5064f7;
	margin: 0 auto 20px;
	box-shadow: 0 8px 24px rgba(80, 100, 247, 0.12);
}

.empty-card__title {
	font-size: 20px;
	font-weight: 750;
	color: #0f172a;
	margin: 0 0 8px;
	letter-spacing: -0.02em;
}

.empty-card__desc {
	font-size: 15px;
	color: #64748b;
	margin: 0 auto 24px;
	max-width: 440px;
	line-height: 1.5;
}

.empty-card__btn {
	border-radius: 14px;
	padding: 11px 26px;
	font-weight: 600;
	font-size: 15px;
	box-shadow: 0 4px 14px rgba(80, 100, 247, 0.28);
}

/* Animations */
.home-header,
.home-section,
.stats-row,
.quick-row {
	animation: fadeInUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.stats-row { animation-delay: 0.05s; }
.quick-row { animation-delay: 0.1s; }
.home-section--grow { animation-delay: 0.15s; }

@keyframes fadeInUp {
	from {
		opacity: 0;
		transform: translateY(16px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

/* Responsive */
@media (max-width: 1024px) {
	.stats-row,
	.quick-row {
		grid-template-columns: repeat(2, 1fr);
	}
}

@media (max-width: 768px) {
	.home-header {
		flex-direction: column;
		align-items: flex-start;
		gap: 16px;
	}

	.home-header__title {
		font-size: 28px;
	}

	.home-page__inner {
		padding: 28px 24px 40px;
	}

	.home-section {
		padding: 22px;
	}
}

@media (max-width: 640px) {
	.home-page__inner {
		padding: 20px 16px 32px;
		gap: 20px;
	}

	.home-header {
		text-align: center;
		align-items: center;
	}

	.home-header__title {
		font-size: 24px;
	}

	.home-header__subtitle {
		font-size: 15px;
	}

	.stats-row,
	.quick-row {
		grid-template-columns: 1fr;
	}

	.trainings-grid {
		grid-template-columns: 1fr;
	}

	.home-section__head {
		margin-bottom: 18px;
	}
}
</style>
