<template>
	<page-shell title="Мои тренинги" subtitle="Создавайте и управляйте обучающими материалами">
		<template #actions>
			<q-input
				outlined
				dense
				v-model="searchQuery"
				placeholder="Поиск..."
				class="page-search"
				color="primary"
				clearable
			>
				<template #prepend><q-icon name="search" /></template>
			</q-input>
			<q-btn
				unelevated
				color="primary"
				icon="add"
				label="Создать"
				class="page-cta"
				@click="openCreateModal"
			/>
		</template>

		<q-tabs
			v-model="filterTab"
			dense
			class="page-tabs"
			active-color="primary"
			indicator-color="primary"
			align="left"
			narrow-indicator
		>
			<q-tab name="all" label="Все" />
			<q-tab name="published" label="Опубликованные" />
			<q-tab name="drafts" label="Черновики" />
		</q-tabs>

		<div v-if="status" class="page-loading">
			<q-spinner-dots size="44px" color="primary" />
			<p class="page-loading__text">Загрузка тренингов...</p>
		</div>

		<div
			v-else-if="filteredTrainings.length === 0 && trainings.length === 0"
			class="page-empty"
		>
			<div class="page-empty__icon">
				<q-icon name="school" size="40px" />
			</div>
			<h3 class="page-empty__title">Пока нет тренингов</h3>
			<p class="page-empty__desc">
				Создайте первый тренинг и начните обучать с помощью интерактивных скриншотов.
			</p>
			<q-btn
				unelevated
				no-caps
				color="primary"
				icon="add"
				label="Создать тренинг"
				class="page-empty__btn"
				@click="openCreateModal"
			/>
		</div>

		<div
			v-else-if="filteredTrainings.length === 0"
			class="page-empty"
		>
			<q-icon name="search_off" size="64px" color="grey-4" class="q-mb-md" />
			<h3 class="page-empty__title">Ничего не найдено</h3>
			<p class="page-empty__desc">По вашему запросу не найдено ни одного тренинга.</p>
			<q-btn flat color="primary" label="Сбросить фильтры" @click="searchQuery = ''; filterTab = 'all'" />
		</div>

		<div v-else class="page-grid">
			<div
				v-if="filterTab === 'all' && !searchQuery"
				class="page-card page-create-card"
				v-ripple
				@click="openCreateModal"
			>
				<div class="page-create-icon">
					<q-icon name="add" size="32px" />
				</div>
				<div class="page-create-title">Новый тренинг</div>
				<div class="page-create-desc">Нажмите, чтобы создать</div>
			</div>

			<q-card
				v-for="training in filteredTrainings"
				:key="training.uuid"
				class="page-card"
				flat
				bordered
				v-ripple
				@click="editTraining(training.uuid)"
			>
				<q-card-section class="card-content">
					<div class="row items-center justify-between q-mb-md">
						<span
							class="page-status"
							:class="training.publish ? 'page-status--published' : 'page-status--draft'"
						>
							{{ training.publish ? "Опубликован" : "Черновик" }}
						</span>
						<q-btn-dropdown
							flat
							round
							dense
							color="grey-6"
							dropdown-icon="more_vert"
							class="training-card-menu-trigger"
							content-class="training-card-actions-menu"
							:menu-offset="[0, 8]"
							@click.stop
						>
							<q-list dense class="training-card-actions-list">
								<q-item clickable v-close-popup @click="editTraining(training.uuid)">
									<q-item-section avatar>
										<q-icon name="edit" size="sm" />
									</q-item-section>
									<q-item-section>Редактировать шаги</q-item-section>
								</q-item>
								<q-item clickable v-close-popup @click="openSettingsData(training)">
									<q-item-section avatar>
										<q-icon name="settings" size="sm" />
									</q-item-section>
									<q-item-section>Настройки</q-item-section>
								</q-item>
								<q-item clickable v-close-popup @click="openPublishModal(training)">
									<q-item-section avatar>
										<q-icon :name="training.publish ? 'share' : 'publish'" size="sm" color="primary" />
									</q-item-section>
									<q-item-section>{{ training.publish ? "Поделиться" : "Опубликовать" }}</q-item-section>
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
								<q-item
									v-if="training.publish"
									clickable
									v-close-popup
									@click="confirmUnpublish(training)"
								>
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

					<div class="row items-center q-mb-md q-mt-sm">
						<q-avatar v-if="training.icon" size="48px" rounded class="bg-grey-2 q-mr-md shadow-1">
							<img :src="training.icon" style="object-fit: cover; width: 100%; height: 100%;" />
						</q-avatar>
						<div class="page-card__title ellipsis" style="flex: 1" :title="training.title">
							{{ training.title }}
						</div>
					</div>

					<div class="row items-center text-caption text-grey-6 q-mb-md q-gutter-x-md">
						<span class="row items-center">
							<q-icon name="layers" size="18px" class="q-mr-xs" />
							{{ training.steps_count ?? training.steps?.length ?? 0 }} шагов
						</span>
						<span v-if="training.duration_minutes" class="row items-center">
							<q-icon name="schedule" size="18px" class="q-mr-xs" />
							{{ training.duration_minutes }} мин
						</span>
						<span v-if="training.level" class="row items-center">
							<q-icon name="trending_up" size="18px" class="q-mr-xs" />
							{{ training.level.label }}
						</span>
					</div>

					<p class="card-description text-body2 text-grey-7 ellipsis-2 q-mb-md">
						{{ training.description || "Описание отсутствует. Добавьте его в настройках тренинга." }}
					</p>

					<div class="row q-gutter-sm q-mt-auto">
						<q-badge
							v-for="tag in training.tags"
							:key="tag.value"
							class="badge-tag"
							:label="tag.label"
						/>
					</div>
				</q-card-section>
			</q-card>
		</div>

		<training-modal v-model="modal" :mode="modalMode" :editData="editingTraining" />
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
	</page-shell>
</template>

<script setup>
import { TrainingApi } from "@api/api/TrainingApi.js";
import { computed, onMounted, ref, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { trainingEvents } from "@utils/eventBus.js";
import TrainingModal from "@components/features/training_page/TrainingModal.vue";
import PublishModalTraining from "@components/features/training_page/PublishModalTraining.vue";
import PageShell from "@components/common/PageShell.vue";

const router = useRouter();
const $q = useQuasar();
const trainings = ref([]);
const api = new TrainingApi();
const status = ref(true);
const modal = ref(false);
const modalMode = ref("create");
const editingTraining = ref(null);
const publishModal = ref(false);
const publishTrainingData = ref(null);

const searchQuery = ref("");
const filterTab = ref("all");

const handleTaskUpdate = (event) => {
	const data = event.detail;
	if (data.status === "completed") {
		getTrainings(true);
	}
};

const unsubscribeCreated = trainingEvents.created.on(() => {
	getTrainings();
});

onMounted(async () => {
	await getTrainings();
	window.addEventListener("training-task-update", handleTaskUpdate);
});

onUnmounted(() => {
	unsubscribeCreated.off();
	window.removeEventListener("training-task-update", handleTaskUpdate);
});

const filteredTrainings = computed(() => {
	let result = trainings.value;

	if (filterTab.value === "published") {
		result = result.filter((t) => t.publish);
	} else if (filterTab.value === "drafts") {
		result = result.filter((t) => !t.publish);
	}

	if (searchQuery.value) {
		const q = searchQuery.value.toLowerCase();
		result = result.filter(
			(t) =>
				t.title.toLowerCase().includes(q) ||
				(t.description && t.description.toLowerCase().includes(q))
		);
	}

	return result;
});

function openCreateModal() {
	modalMode.value = "create";
	editingTraining.value = null;
	modal.value = true;
}

function openSettingsData(training) {
	modalMode.value = "edit";
	editingTraining.value = training;
	modal.value = true;
}

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

async function getTrainings(background = false) {
	try {
		if (!background) status.value = true;
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
		if (!background) status.value = false;
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
</script>

<style scoped>
.card-content {
	padding: 0;
	flex: 1;
	display: flex;
	flex-direction: column;
}

.badge-tag {
	background: #f1f5f9;
	color: #475569;
	border: 1px solid #e2e8f0;
	border-radius: 8px;
	padding: 5px 10px;
	font-size: 12px;
	font-weight: 500;
}

.card-description {
	line-height: 1.5;
	flex: 1;
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

.training-card-menu-trigger {
	margin-right: -10px;
	margin-top: -6px;
	opacity: 0.75;
	transition: opacity 0.2s ease, background 0.2s ease;
}

.training-card-menu-trigger:hover {
	opacity: 1;
	background: rgba(0, 0, 0, 0.04) !important;
}

/* Stats dialog styles */
.passage-stats-card {
	min-width: min(480px, 94vw);
	max-width: 700px;
	width: 100%;
	border-radius: 20px !important;
	overflow: hidden;
	border-color: rgba(0, 0, 0, 0.08) !important;
}

.passage-stats-header {
	padding: 20px 24px;
	background: linear-gradient(135deg, rgba(80, 100, 247, 0.04) 0%, rgba(80, 100, 247, 0.01) 100%);
}

.passage-stats-header__icon {
	flex-shrink: 0;
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
	font-size: 12px;
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
</style>

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
