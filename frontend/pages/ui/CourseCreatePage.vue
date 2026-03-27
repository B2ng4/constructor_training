<template>
	<div class="course-page">
		<div class="q-pa-lg animate-fade-in-up">
			<h1 class="page-title text-h4 text-weight-bold q-mb-xs">Мои курсы</h1>
			<p class="text-body2 text-grey-7">Собирайте курсы из существующих тренингов</p>
		</div>

		<div v-if="loading" class="loading-state q-pa-xl column items-center justify-center">
			<q-spinner-gears size="48px" color="primary" class="loading-spinner" />
			<p class="text-grey-7 q-mt-md loading-text">Загрузка курсов...</p>
		</div>

		<div
			v-else-if="courses.length === 0"
			class="empty-state q-pa-xl column items-center justify-center animate-scale-in"
		>
			<q-icon name="school" size="80px" color="grey-4" class="q-mb-lg empty-icon" />
			<p class="text-h6 text-grey-8 q-mb-xs">Пока нет курсов</p>
			<p class="text-body2 text-grey-6 text-center q-mb-lg">
				Создайте первый курс и объедините в нем нужные тренинги
			</p>
			<q-btn
				unelevated
				no-caps
				color="primary"
				size="lg"
				icon="add"
				label="Создать курс"
				@click="openCreateModal"
			/>
		</div>

		<div v-else class="courses-grid q-px-lg q-pb-xl animate-stagger-children">
			<q-card class="course-card create-card" flat bordered @click="openCreateModal">
				<q-card-section class="create-card-section">
					<div class="column items-center justify-center full-height">
						<div class="create-icon-wrap">
							<q-icon name="add" size="40px" color="primary" />
						</div>
						<p class="create-title text-weight-bold">Создать курс</p>
						<p class="create-subtitle text-body2 text-grey-6">Добавить новый курс</p>
					</div>
				</q-card-section>
			</q-card>

			<q-card v-for="course in courses" :key="course.id" class="course-card" flat bordered>
				<q-card-section class="card-content">
					<div class="row no-wrap items-start q-mb-md">
						<div class="card-icon">
							<q-icon name="school" size="32px" color="primary" />
						</div>
						<div class="col q-pl-md overflow-hidden">
							<p class="card-title text-weight-bold text-body1 ellipsis">{{ course.title }}</p>
							<p class="text-caption text-grey-7 q-mb-sm">
								Тренингов в курсе: {{ course.trainings?.length || 0 }}
							</p>
						</div>
					</div>

					<p v-if="course.description" class="card-description text-body2 text-grey-8 ellipsis-2 q-mb-md">
						{{ course.description }}
					</p>

					<div class="q-gutter-xs q-mb-md">
						<q-badge
							v-for="training in course.trainings || []"
							:key="training.uuid"
							class="badge-tag"
							:label="training.title"
						/>
					</div>

					<div class="row items-center justify-between card-footer">
						<span class="status-draft text-caption text-grey-6">
							Создан: {{ formatDate(course.created_at) }}
						</span>
						<q-btn
							flat
							round
							dense
							color="negative"
							icon="delete"
							@click="confirmDelete(course)"
						/>
					</div>
				</q-card-section>
			</q-card>
		</div>
	</div>

	<q-dialog v-model="createModal">
		<q-card class="course-modal" flat bordered>
			<q-card-section class="row items-center no-wrap">
				<div class="text-h6">Новый курс</div>
				<q-space />
				<q-btn icon="close" flat round dense v-close-popup />
			</q-card-section>
			<q-separator />
			<q-card-section>
				<q-input v-model.trim="form.title" outlined label="Название курса" class="q-mb-md" />
				<q-input
					v-model.trim="form.description"
					outlined
					label="Описание (необязательно)"
					type="textarea"
					autogrow
					class="q-mb-md"
				/>
				<q-input v-model.trim="search" outlined dense label="Поиск тренинга" class="q-mb-md" />
				<div class="text-caption text-grey-7 q-mb-sm">
					Выбрано тренингов: {{ form.training_uuids.length }}
				</div>
				<q-list bordered separator class="trainings-select-list">
					<q-item v-if="filteredTrainings.length === 0">
						<q-item-section class="text-grey-6">Тренинги не найдены</q-item-section>
					</q-item>
					<q-item
						v-for="training in filteredTrainings"
						:key="training.uuid"
						clickable
						v-ripple
						@click="toggleTraining(training.uuid)"
					>
						<q-item-section avatar>
							<q-checkbox
								:model-value="selectedSet.has(training.uuid)"
								@update:model-value="toggleTraining(training.uuid)"
								@click.stop
							/>
						</q-item-section>
						<q-item-section>
							<q-item-label>{{ training.title }}</q-item-label>
							<q-item-label caption>{{ training.level?.label ?? "Без уровня" }}</q-item-label>
						</q-item-section>
					</q-item>
				</q-list>
			</q-card-section>
			<q-card-actions align="right">
				<q-btn flat no-caps label="Отмена" v-close-popup />
				<q-btn
					unelevated
					no-caps
					color="primary"
					label="Создать курс"
					:disable="!canCreate"
					@click="createCourse"
				/>
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useQuasar } from "quasar";
import { CourseApi, TrainingApi } from "@api";

const $q = useQuasar();
const courseApi = new CourseApi();
const trainingApi = new TrainingApi();

const loading = ref(true);
const courses = ref([]);
const trainings = ref([]);
const createModal = ref(false);
const search = ref("");
const form = ref({
	title: "",
	description: "",
	training_uuids: [],
});

const selectedSet = computed(() => new Set(form.value.training_uuids));
const canCreate = computed(() => form.value.title && form.value.training_uuids.length > 0);
const filteredTrainings = computed(() => {
	const query = search.value.trim().toLowerCase();
	if (!query) return trainings.value;
	return trainings.value.filter((item) => item.title?.toLowerCase().includes(query));
});

function formatDate(value) {
	if (!value) return "—";
	try {
		return new Date(value).toLocaleString("ru-RU", {
			day: "2-digit",
			month: "2-digit",
			year: "numeric",
		});
	} catch {
		return "—";
	}
}

function resetForm() {
	form.value = {
		title: "",
		description: "",
		training_uuids: [],
	};
	search.value = "";
}

function openCreateModal() {
	resetForm();
	createModal.value = true;
}

function toggleTraining(uuid) {
	const set = new Set(form.value.training_uuids);
	if (set.has(uuid)) set.delete(uuid);
	else set.add(uuid);
	form.value.training_uuids = [...set];
}

async function fetchData() {
	try {
		loading.value = true;
		const [coursesResponse, trainingsResponse] = await Promise.all([
			courseApi.getCourses(),
			trainingApi.getTrainings(),
		]);
		courses.value = Array.isArray(coursesResponse.data) ? coursesResponse.data : [];
		trainings.value = Array.isArray(trainingsResponse.data) ? trainingsResponse.data : [];
	} catch (error) {
		console.error(error);
		$q.notify({
			message: "Не удалось загрузить данные курсов",
			type: "negative",
			position: "top",
		});
	} finally {
		loading.value = false;
	}
}

async function createCourse() {
	if (!canCreate.value) return;
	try {
		await courseApi.createCourse(form.value);
		$q.notify({
			message: "Курс создан",
			type: "positive",
			position: "top-right",
		});
		createModal.value = false;
		await fetchData();
	} catch (error) {
		console.error(error);
		$q.notify({
			message: error?.response?.data?.detail || "Не удалось создать курс",
			type: "negative",
			position: "top",
		});
	}
}

function confirmDelete(course) {
	$q.dialog({
		title: "Удалить курс?",
		message: `Курс «${course.title}» будет удалён без возможности восстановления.`,
		cancel: { label: "Отмена", flat: true },
		ok: { label: "Удалить", color: "negative", flat: true },
		persistent: true,
	}).onOk(async () => {
		try {
			await courseApi.deleteCourse(course.id);
			$q.notify({
				message: "Курс удален",
				type: "positive",
				position: "top-right",
			});
			await fetchData();
		} catch (error) {
			console.error(error);
			$q.notify({
				message: "Не удалось удалить курс",
				type: "negative",
				position: "top",
			});
		}
	});
}

onMounted(async () => {
	await fetchData();
});
</script>

<style scoped>
.course-page {
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
.courses-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
	gap: 24px;
}
.course-card {
	border-radius: 14px;
	transition: transform 0.28s var(--anim-ease-spring), box-shadow 0.28s var(--anim-ease-out), border-color 0.2s ease;
	border: 1px solid rgba(0, 0, 0, 0.08);
}
.course-card:hover {
	transform: translateY(-5px);
	box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
	border-color: rgba(80, 100, 247, 0.2);
}
.create-card {
	background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
	border: 2px dashed rgba(80, 100, 247, 0.35);
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
}
.create-title {
	font-size: 18px;
	color: #5064f7;
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
}
.card-title {
	font-size: 16px;
	color: #1a1a2e;
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
.course-modal {
	width: min(720px, 95vw);
	max-width: 95vw;
	border-radius: 14px;
}
.trainings-select-list {
	max-height: 320px;
	overflow: auto;
	border-radius: 10px;
}
</style>
