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
							dense
							dropdown-icon="more_vert"
							@click.stop
						>
						<q-list dense style="min-width: 180px">
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
</template>

<script setup>
import { TrainingApi } from "@api/api/TrainingApi.js";
import { onMounted, ref, onUnmounted } from "vue";
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
</style>