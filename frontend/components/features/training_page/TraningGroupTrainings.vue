<template>
	<div class="training-page">
		<!-- Заголовок страницы -->
		<div class="q-pa-lg animate-fade-in-up">
			<h1 class="page-title text-h4 text-weight-bold q-mb-xs">Мои тренинги</h1>
			<p class="text-body2 text-grey-7">Создавайте и управляйте интерактивными тренингами</p>
		</div>

		<!-- Состояние загрузки -->
		<div v-if="status" class="loading-state q-pa-xl column items-center justify-center">
			<q-spinner-gears size="48px" color="primary" class="loading-spinner" />
			<p class="text-grey-7 q-mt-md loading-text">Загрузка тренингов...</p>
		</div>

		<!-- Пустое состояние -->
		<div
			v-else-if="trainings.length === 0"
			class="empty-state q-pa-xl column items-center justify-center animate-scale-in"
		>
			<q-icon name="school" size="80px" color="grey-4" class="q-mb-lg empty-icon" />
			<p class="text-h6 text-grey-8 q-mb-xs">Пока нет тренингов</p>
			<p class="text-body2 text-grey-6 text-center q-mb-lg">
				Создайте первый тренинг и начните обучать с помощью интерактивных скриншотов
			</p>
			<q-btn
				unelevated
				no-caps
				color="primary"
				size="lg"
				icon="add"
				label="Создать тренинг"
				@click="modal = true"
			/>
		</div>

		<!-- Сетка карточек -->
		<div v-else class="trainings-grid q-px-lg q-pb-xl animate-stagger-children">
			<!-- Карточка создания -->
			<q-card class="training-card create-card" flat bordered @click="modal = true">
				<q-card-section class="create-card-section">
					<div class="column items-center justify-center full-height">
						<div class="create-icon-wrap">
							<q-icon name="add" size="40px" color="primary" />
						</div>
						<p class="create-title text-weight-bold">Создать тренинг</p>
						<p class="create-subtitle text-body2 text-grey-6">Добавить новый тренинг</p>
					</div>
				</q-card-section>
			</q-card>

			<!-- Карточки тренингов -->
			<q-card
				v-for="training in trainings"
				:key="training.uuid"
				class="training-card"
				flat
				bordered
				@click="editTraining(training.uuid)"
			>
				<q-card-section class="card-content">
					<div class="row no-wrap items-start q-mb-md">
						<div class="card-icon">
							<q-icon name="playlist_add_check" size="32px" color="primary" />
						</div>
						<div class="col q-pl-md overflow-hidden">
							<p class="card-title text-weight-bold text-body1 ellipsis">{{ training.title }}</p>
							<p class="text-caption text-grey-7 q-mb-sm">
								{{ training.level?.label ?? "Без уровня" }}
								<span v-if="training.duration_minutes" class="q-ml-sm">
									· {{ training.duration_minutes }} мин
								</span>
							</p>
						</div>
					</div>

					<p v-if="training.description" class="card-description text-body2 text-grey-8 ellipsis-2 q-mb-md">
						{{ training.description }}
					</p>

					<div v-if="training.tags?.length" class="q-gutter-xs q-mb-md">
						<q-badge
							v-for="tag in training.tags"
							:key="tag.value"
							class="badge-tag"
							:label="tag.label"
						/>
					</div>

					<div class="row items-center justify-between card-footer">
						<q-badge
							v-if="training.publish"
							class="status-badge published"
							label="Опубликовано"
						/>
						<span v-else class="status-draft text-caption text-grey-6">Черновик</span>
						<q-btn-dropdown
							flat
							round
							dense
							color="grey-7"
							dropdown-icon="more_vert"
							class="training-card-menu-trigger"
							content-class="training-card-actions-menu"
							:menu-offset="[0, 8]"
							toggle-aria-label="Действия с тренингом"
							@click.stop
						>
						<q-list dense class="training-card-actions-list">
							<q-item clickable v-close-popup @click="editTraining(training.uuid)">
								<q-item-section avatar>
									<q-icon name="edit" size="sm" />
								</q-item-section>
								<q-item-section>Редактировать</q-item-section>
							</q-item>
							<q-item clickable v-close-popup @click="openPublishModal(training)">
								<q-item-section avatar>
									<q-icon :name="training.publish ? 'share' : 'publish'" size="sm" color="primary" />
								</q-item-section>
								<q-item-section>{{ training.publish ? 'Поделиться' : 'Опубликовать' }}</q-item-section>
							</q-item>
							<q-item
								v-if="training.publish"
								clickable
								v-close-popup
								@click="openPassageStats(training)"
							>
								<q-item-section avatar>
									<q-icon name="bar_chart" size="sm" color="primary" />
								</q-item-section>
								<q-item-section>Статистика</q-item-section>
							</q-item>
							<q-item v-if="training.publish" clickable v-close-popup @click="confirmUnpublish(training)">
								<q-item-section avatar>
									<q-icon name="link_off" size="sm" color="grey-7" />
								</q-item-section>
								<q-item-section>Снять с публикации</q-item-section>
							</q-item>
							<q-separator class="q-my-xs" />
							<q-item clickable v-close-popup @click="confirmDelete(training)">
								<q-item-section avatar>
									<q-icon name="delete" size="sm" color="negative" />
								</q-item-section>
								<q-item-section class="text-negative">Удалить</q-item-section>
							</q-item>
						</q-list>
						</q-btn-dropdown>
					</div>
				</q-card-section>
			</q-card>
		</div>
	</div>

	<training-modal v-model="modal"/>
	<publish-modal-training
		v-model="publishModal"
		:data="publishTrainingData"
		@published="onPublished"
	/>

	<q-dialog v-model="passageStatsOpen">
		<q-card class="passage-stats-card" flat bordered>
			<q-card-section class="passage-stats-header row items-center no-wrap">
				<q-icon name="bar_chart" size="28px" color="primary" class="q-mr-sm passage-stats-header__icon" />
				<div class="col passage-stats-header__titles">
					<div class="text-h6">Статистика прохождений</div>
					<div
						v-if="passageStatsTraining"
						class="text-body2 text-grey-7 ellipsis q-mt-xs"
					>
						{{ passageStatsTraining.title }}
					</div>
				</div>
				<q-btn flat round dense icon="close" v-close-popup />
			</q-card-section>

			<q-separator />

			<q-card-section v-if="passageStatsLoading" class="passage-stats-loading column flex-center q-py-xl">
				<q-spinner-dots color="primary" size="40px" />
				<div class="text-body2 text-grey-7 q-mt-md">Загрузка…</div>
			</q-card-section>

			<template v-else>
				<q-card-section v-if="passageAnalytics" class="passage-stats-body">
					<div class="row q-col-gutter-sm">
						<div class="col-6 col-sm-3">
							<q-card flat bordered class="passage-stats-metric">
								<q-card-section class="q-pa-md">
									<div class="passage-stats-metric__label text-caption text-grey-7">Старты</div>
									<div class="passage-stats-metric__value text-h6 text-weight-bold text-grey-10">
										{{ passageAnalytics.total_starts }}
									</div>
								</q-card-section>
							</q-card>
						</div>
						<div class="col-6 col-sm-3">
							<q-card flat bordered class="passage-stats-metric">
								<q-card-section class="q-pa-md">
									<div class="passage-stats-metric__label text-caption text-grey-7">Завершения</div>
									<div class="passage-stats-metric__value text-h6 text-weight-bold text-grey-10">
										{{ passageAnalytics.total_completions }}
									</div>
								</q-card-section>
							</q-card>
						</div>
						<div class="col-6 col-sm-3">
							<q-card flat bordered class="passage-stats-metric">
								<q-card-section class="q-pa-md">
									<div class="passage-stats-metric__label text-caption text-grey-7">До конца</div>
									<div class="passage-stats-metric__value text-h6 text-weight-bold text-grey-10">
										{{ formatPercent(passageAnalytics.completion_rate) }}
									</div>
								</q-card-section>
							</q-card>
						</div>
						<div class="col-6 col-sm-3">
							<q-card flat bordered class="passage-stats-metric">
								<q-card-section class="q-pa-md">
									<div class="passage-stats-metric__label text-caption text-grey-7">Среднее время</div>
									<div class="passage-stats-metric__value text-h6 text-weight-bold text-grey-10">
										{{ formatDurationHuman(passageAnalytics.avg_duration_seconds) }}
									</div>
								</q-card-section>
							</q-card>
						</div>
					</div>
					<div class="q-mt-md">
						<div class="text-caption text-grey-7 q-mb-xs">Доля завершивших</div>
						<q-linear-progress
							:model-value="completionRateForRing / 100"
							color="primary"
							track-color="grey-3"
							size="4px"
							rounded
						/>
					</div>
				</q-card-section>

				<q-separator />

				<q-card-section class="passage-stats-history q-pb-lg">
					<div class="passage-stats-section-label q-mb-md">
						<q-icon name="history" size="18px" />
						<span>Последние попытки</span>
						<span
							v-if="passageHistory.length"
							class="text-caption text-grey-6 q-ml-sm"
						>
							({{ passageHistory.length }})
						</span>
					</div>

					<q-scroll-area
						v-if="passageHistory.length"
						class="passage-stats-table-wrap"
						:thumb-style="{ borderRadius: '4px', background: 'rgba(0,0,0,0.2)' }"
						:bar-style="{ borderRadius: '4px' }"
					>
						<q-markup-table flat bordered class="passage-stats-table" wrap-cells>
							<thead>
								<tr>
									<th class="text-left">Начало</th>
									<th class="text-left">Конец</th>
									<th class="text-center">Статус</th>
									<th class="text-right">Время</th>
									<th class="text-right">Ошибок</th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="(row, idx) in passageHistory" :key="idx">
									<td class="text-body2 text-grey-9">{{ formatDt(row.started_at) }}</td>
									<td class="text-body2 text-grey-9">{{ formatDt(row.finished_at) }}</td>
									<td class="text-center text-body2">
										<span v-if="row.is_completed" class="text-positive">Завершено</span>
										<span v-else class="text-grey-7">Не завершено</span>
									</td>
									<td class="text-right text-body2 text-grey-9">
										{{ formatDurationHuman(row.duration_seconds) }}
									</td>
									<td class="text-right text-body2 text-grey-9">
										{{ row.wrong_attempts_total != null ? row.wrong_attempts_total : "—" }}
									</td>
								</tr>
							</tbody>
						</q-markup-table>
					</q-scroll-area>

					<q-card
						v-else
						flat
						class="passage-stats-empty bg-grey-3 q-pa-lg"
					>
						<div class="row items-start no-wrap">
							<q-icon name="info_outline" color="grey-7" size="22px" class="q-mr-md passage-stats-empty__lead-icon" />
							<div>
								<div class="text-subtitle2 text-grey-8 q-mb-xs">Пока нет записей</div>
								<div class="text-body2 text-grey-7">
									После прохождения тренинга по публичной ссылке здесь появится история попыток.
								</div>
							</div>
						</div>
					</q-card>
				</q-card-section>
			</template>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { TrainingApi } from "@api/api/TrainingApi.js";
import { computed, onMounted, ref, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { trainingEvents } from "@utils/eventBus.js";
import TrainingModal from "@components/features/training_page/TrainingModal.vue";
import PublishModalTraining from "@components/features/training_page/PublishModalTraining.vue";

const router = useRouter();
const $q = useQuasar();
const trainings = ref([]);
const api = new TrainingApi();
const status = ref(true);
const modal = ref(false);
const publishModal = ref(false);
const publishTrainingData = ref(null);

const passageStatsOpen = ref(false);
const passageStatsLoading = ref(false);
const passageStatsTraining = ref(null);
const passageAnalytics = ref(null);
const passageHistory = ref([]);

const completionRateForRing = computed(() => {
	const a = passageAnalytics.value;
	if (!a || a.completion_rate == null || Number.isNaN(a.completion_rate)) return 0;
	return Math.min(100, Math.max(0, a.completion_rate * 100));
});

function formatPercent(rate) {
	if (rate == null || Number.isNaN(rate)) return "—";
	return `${Math.round(rate * 1000) / 10}%`;
}

function formatDurationHuman(sec) {
	if (sec == null || Number.isNaN(Number(sec))) return "—";
	const s = Math.floor(Number(sec));
	if (s < 60) return `${s} с`;
	const m = Math.floor(s / 60);
	const r = s % 60;
	if (m < 60) return `${m} мин ${r > 0 ? `${r} с` : ""}`.trim();
	const h = Math.floor(m / 60);
	const mm = m % 60;
	return `${h} ч ${mm} мин`;
}

function formatDt(iso) {
	if (!iso) return "—";
	try {
		return new Date(iso).toLocaleString("ru-RU", {
			day: "2-digit",
			month: "2-digit",
			year: "numeric",
			hour: "2-digit",
			minute: "2-digit",
		});
	} catch {
		return "—";
	}
}

async function openPassageStats(training) {
	passageStatsTraining.value = training;
	passageAnalytics.value = null;
	passageHistory.value = [];
	passageStatsOpen.value = true;
	passageStatsLoading.value = true;
	try {
		const [anRes, histRes] = await Promise.all([
			api.getPassageAnalytics(training.uuid),
			api.getPassageHistory(training.uuid, { skip: 0, limit: 20 }),
		]);
		passageAnalytics.value = anRes.data;
		passageHistory.value = Array.isArray(histRes.data) ? histRes.data : [];
	} catch (e) {
		console.error(e);
		$q.notify({
			message: "Не удалось загрузить статистику",
			type: "negative",
			position: "top",
		});
		passageStatsOpen.value = false;
	} finally {
		passageStatsLoading.value = false;
	}
}

async function getTrainings() {
	try {
		status.value = true;
		trainings.value = [];
		const response = await api.getTrainings();
		trainings.value = response.data;
	} catch (e) {
		console.error(e);
		$q.notify({
			message: "Ошибка получения списка тренингов",
			position: "top",
			type: "negative",
		});
	} finally {
		status.value = false;
	}
}

function openPublishModal(training) {
	publishModal.value = true;
	publishTrainingData.value = training;
}

async function onPublished() {
	await getTrainings();
}

function confirmUnpublish(training) {
	$q.dialog({
		title: "Снять с публикации?",
		message: `Ссылка на тренинг «${training.title}» перестанет работать. Вы сможете опубликовать его снова и получить новую ссылку.`,
		cancel: { label: "Отмена", flat: true },
		ok: { label: "Снять", color: "primary", flat: true },
		persistent: true,
	}).onOk(async () => {
		await unpublishTraining(training.uuid);
	});
}

async function unpublishTraining(uuid) {
	try {
		await api.unpublishTraining(uuid);
		$q.notify({
			message: "Тренинг снят с публикации",
			type: "positive",
			position: "top-right",
		});
		await getTrainings();
	} catch (e) {
		console.error(e);
		$q.notify({
			message: "Не удалось снять с публикации",
			type: "negative",
			position: "top",
		});
	}
}

function confirmDelete(training) {
	$q.dialog({
		title: "Удалить тренинг?",
		message: `Тренинг «${training.title}» будет удалён без возможности восстановления.`,
		cancel: { label: "Отмена", flat: true },
		ok: { label: "Удалить", color: "negative", flat: true },
		persistent: true,
	}).onOk(async () => {
		await deleteTraining(training.uuid);
	});
}

async function deleteTraining(uuid) {
	try {
		await api.deleteTraining(uuid);
		$q.notify({
			message: "Тренинг успешно удалён",
			type: "positive",
			position: "top-right",
		});
		await getTrainings();
	} catch (e) {
		console.error(e);
		$q.notify({
			message: "Не удалось удалить тренинг",
			type: "negative",
			position: "top",
		});
	}
}

function editTraining(uuid) {
	const route = router.resolve(`/edit/${uuid}`);
	window.open(route.href, "_blank");
}

const unsubscribe = trainingEvents.created.on(() => {
	getTrainings();
});

onMounted(() => {
	getTrainings();
});

onUnmounted(() => {
	unsubscribe.off();
});
</script>

<style scoped>
.training-page {
	min-height: 60vh;
}

.page-title {
	color: #1a1a2e;
}

.loading-state,
.empty-state {
	min-height: 300px;
}
.loading-spinner {
	animation: pulse-soft 1.2s var(--anim-ease-in-out) infinite;
}
.loading-text {
	font-weight: 500;
}
.empty-icon {
	transition: transform 0.4s var(--anim-ease-spring);
}
.empty-state:hover .empty-icon {
	transform: scale(1.05);
}

.trainings-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
	gap: 24px;
}

.training-card {
	border-radius: 14px;
	cursor: pointer;
	transition: transform 0.28s var(--anim-ease-spring), box-shadow 0.28s var(--anim-ease-out), border-color 0.2s ease;
	border: 1px solid rgba(0, 0, 0, 0.08);
}
.training-card:hover {
	transform: translateY(-5px);
	box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
	border-color: rgba(80, 100, 247, 0.2);
}
.training-card:active {
	transform: translateY(-2px);
}

.create-card {
	background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
	border: 2px dashed rgba(80, 100, 247, 0.35);
	transition: border-color 0.25s ease, background 0.3s ease, transform 0.28s var(--anim-ease-spring), box-shadow 0.28s ease;
}
.create-card:hover {
	border-color: rgba(80, 100, 247, 0.55);
	background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);
	box-shadow: 0 8px 24px rgba(80, 100, 247, 0.12);
	transform: translateY(-4px);
}

.create-card-section {
	min-height: 200px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.create-icon-wrap {
	width: 72px;
	height: 72px;
	border-radius: 50%;
	background: rgba(80, 100, 247, 0.12);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 12px;
	transition: transform 0.35s var(--anim-ease-spring), background 0.3s ease;
}
.create-card:hover .create-icon-wrap {
	transform: scale(1.1);
	background: rgba(80, 100, 247, 0.18);
}

.create-title {
	font-size: 18px;
	color: #5064f7;
}

.create-subtitle {
	font-size: 14px;
}

.card-content {
	padding: 20px;
}

.card-icon {
	width: 48px;
	height: 48px;
	border-radius: 12px;
	background: rgba(80, 100, 247, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	transition: transform 0.3s var(--anim-ease-spring);
}
.training-card:hover .card-icon {
	transform: scale(1.06);
}

.card-title {
	font-size: 16px;
	color: #1a1a2e;
}

.card-description {
	max-height: 2.6em;
	line-height: 1.3;
}

.ellipsis {
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.ellipsis-2 {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.badge-tag {
	background: rgba(80, 100, 247, 0.1);
	color: #5064f7;
	border-radius: 6px;
	padding: 4px 10px;
	font-size: 12px;
}

.card-footer {
	margin-top: 4px;
	padding-top: 12px;
	border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.status-badge {
	border-radius: 6px;
	padding: 4px 10px;
	font-size: 12px;
}

.status-badge.published {
	background: rgba(16, 185, 129, 0.12);
	color: #10b981;
}

.full-height {
	height: 100%;
}

/* В духе TrainingModal / PublishModal: спокойно, без ярких градиентов */
.passage-stats-card {
	min-width: min(480px, 94vw);
	max-width: 700px;
	width: 100%;
	border-radius: 18px;
	overflow: hidden;
	box-shadow: 0 24px 56px rgba(0, 0, 0, 0.14);
	border-color: rgba(0, 0, 0, 0.08) !important;
}

.passage-stats-header {
	padding: 20px 24px;
	background: linear-gradient(135deg, rgba(80, 100, 247, 0.04) 0%, rgba(80, 100, 247, 0.01) 100%);
}

.passage-stats-header__icon {
	flex-shrink: 0;
}

.passage-stats-header__titles {
	min-width: 0;
}

.passage-stats-header .text-h6 {
	color: #1a1a2e;
	font-weight: 700;
	letter-spacing: -0.01em;
}

.passage-stats-loading {
	min-height: 200px;
}

.passage-stats-body {
	padding: 20px 24px 16px;
}

.passage-stats-metric {
	border-radius: 12px;
	border-color: rgba(0, 0, 0, 0.08) !important;
	background: #fff;
}

.passage-stats-metric__label {
	letter-spacing: 0.02em;
}

.passage-stats-metric__value {
	margin-top: 6px;
	line-height: 1.25;
	word-break: break-word;
}

.passage-stats-section-label {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 13px;
	font-weight: 600;
	color: #374151;
}

.passage-stats-section-label .q-icon {
	opacity: 0.85;
	color: #5064f7;
}

.passage-stats-history {
	padding: 20px 24px 24px;
}

.passage-stats-table-wrap {
	height: min(260px, 40vh);
	border-radius: 12px;
	overflow: hidden;
	border: 1px solid rgba(0, 0, 0, 0.08);
}

.passage-stats-table {
	background: #fff;
}

.passage-stats-table thead tr {
	background: #f3f4f6;
}

.passage-stats-table thead th {
	font-size: 12px;
	font-weight: 600;
	color: #6b7280;
	padding: 10px 12px;
	border-color: rgba(0, 0, 0, 0.06);
}

.passage-stats-table tbody td {
	padding: 10px 12px;
	border-color: rgba(0, 0, 0, 0.06);
	vertical-align: middle;
}

.passage-stats-table tbody tr:nth-child(even) {
	background: rgba(249, 250, 251, 0.9);
}

.passage-stats-empty {
	border-radius: 12px;
	border: 1px solid rgba(0, 0, 0, 0.06);
}

.passage-stats-empty__lead-icon {
	flex-shrink: 0;
}

.training-card-menu-trigger {
	opacity: 0.88;
	transition: opacity 0.2s ease, background 0.2s ease;
}

.training-card-menu-trigger:hover {
	opacity: 1;
	background: rgba(0, 0, 0, 0.05) !important;
}
</style>

/* Меню рендерится в портале — стили без scoped */
<style>
.training-card-actions-menu {
	border-radius: 14px !important;
	padding: 8px 0 !important;
	background: #fff !important;
	border: 1px solid rgba(26, 26, 46, 0.1) !important;
	box-shadow: 0 16px 48px rgba(26, 26, 46, 0.12), 0 4px 12px rgba(0, 0, 0, 0.06) !important;
	overflow: hidden;
}

.training-card-actions-menu .training-card-actions-list {
	min-width: 208px;
	padding: 0;
}

.training-card-actions-menu .q-item {
	min-height: 42px;
	padding: 8px 14px;
	margin: 2px 10px;
	border-radius: 10px;
	font-size: 14px;
	font-weight: 500;
	color: #1a1a2e;
	transition: background 0.15s ease, color 0.15s ease;
}

.training-card-actions-menu .q-item:hover {
	background: rgba(80, 100, 247, 0.08) !important;
}

.training-card-actions-menu .q-item__section--avatar {
	min-width: 40px;
}

.training-card-actions-menu .q-item__section--avatar .q-icon {
	opacity: 0.9;
}

.training-card-actions-menu .q-separator {
	margin: 6px 14px;
	background: rgba(26, 26, 46, 0.08) !important;
}
</style>