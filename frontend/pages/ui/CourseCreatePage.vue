<template>
	<page-shell title="Мои курсы" subtitle="Собирайте курсы из существующих тренингов и запускайте прохождение">
		<template #actions>
			<q-input
				outlined
				dense
				v-model="searchQuery"
				placeholder="Поиск курса..."
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
			<q-tab name="published" label="С опубликованными" />
			<q-tab name="draft" label="Черновые" />
		</q-tabs>

		<div v-if="loading" class="page-loading">
			<q-spinner-dots size="44px" color="primary" />
			<p class="page-loading__text">Загрузка курсов...</p>
		</div>

		<div v-else-if="courses.length === 0" class="page-empty">
			<div class="page-empty__icon">
				<q-icon name="school" size="40px" />
			</div>
			<h3 class="page-empty__title">Пока нет курсов</h3>
			<p class="page-empty__desc">Создайте курс и добавьте в него нужные тренинги.</p>
			<q-btn
				unelevated
				no-caps
				color="primary"
				icon="add"
				label="Создать курс"
				class="page-empty__btn"
				@click="openCreateModal"
			/>
		</div>

		<div v-else-if="filteredCourses.length === 0" class="page-empty">
			<q-icon name="search_off" size="64px" color="grey-4" class="q-mb-md" />
			<h3 class="page-empty__title">Ничего не найдено</h3>
			<p class="page-empty__desc">По вашему запросу курсы не найдены.</p>
			<q-btn flat color="primary" label="Сбросить фильтры" @click="resetFilters" />
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
				<div class="page-create-title">Новый курс</div>
				<div class="page-create-desc">Нажмите, чтобы создать</div>
			</div>

			<q-card
				v-for="course in filteredCourses"
				:key="course.id"
				class="page-card"
				flat
				bordered
				v-ripple
				@click="openDetails(course)"
			>
				<q-card-section class="card-content">
					<div class="row items-center justify-between q-mb-md">
						<span
							class="page-status"
							:class="courseStatusClass(course)"
						>
							{{ courseStatusLabel(course) }}
						</span>
						<q-btn
							flat
							round
							dense
							color="negative"
							icon="delete"
							@click.stop="confirmDelete(course)"
						/>
					</div>

					<div class="page-card__title ellipsis" :title="course.title">
						{{ course.title }}
					</div>

					<div class="row items-center text-caption text-grey-6 q-mb-md q-gutter-x-md">
						<span class="row items-center">
							<q-icon name="menu_book" size="18px" class="q-mr-xs" />
							{{ course.trainings?.length || 0 }} тренингов
						</span>
						<span class="row items-center">
							<q-icon name="public" size="18px" class="q-mr-xs" />
							{{ publishedCount(course) }} опубл.
						</span>
					</div>

					<p class="card-description text-body2 text-grey-7 ellipsis-2 q-mb-md">
						{{ course.description || "Описание отсутствует." }}
					</p>

					<div class="row q-gutter-sm q-mt-auto">
						<q-badge
							v-for="training in (course.trainings || []).slice(0, 3)"
							:key="training.uuid"
							class="course-badge"
							:label="training.title"
						/>
						<q-badge
							v-if="(course.trainings?.length || 0) > 3"
							class="course-badge course-badge--more"
							:label="`+${course.trainings.length - 3}`"
						/>
					</div>

					<div class="page-card__footer">
						<span class="text-caption text-grey-6">Создан: {{ formatDate(course.created_at) }}</span>
						<span class="row items-center text-caption text-primary text-weight-bold">
							<q-icon name="visibility" size="16px" class="q-mr-xs" />
							Открыть
						</span>
					</div>
				</q-card-section>
			</q-card>
		</div>
	</page-shell>

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
				<q-input v-model.trim="searchTrainings" outlined dense label="Поиск тренинга" class="q-mb-md" />
				<div class="text-caption text-grey-7 q-mb-sm">
					Выбрано тренингов: {{ form.training_uuids.length }}
				</div>
				<q-list bordered separator class="trainings-select-list">
					<q-item v-if="filteredTrainingsForCreate.length === 0">
						<q-item-section class="text-grey-6">Тренинги не найдены</q-item-section>
					</q-item>
					<q-item
						v-for="training in filteredTrainingsForCreate"
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
				<q-btn flat no-caps label="Отмена" class="btn-rounded" v-close-popup />
				<q-btn
					unelevated
					no-caps
					color="primary"
					label="Создать курс"
					class="btn-rounded"
					:disable="!canCreate"
					@click="createCourse"
				/>
			</q-card-actions>
		</q-card>
	</q-dialog>

	<q-dialog v-model="detailsModal">
		<q-card class="details-modal" flat bordered>
			<q-card-section class="details-header row items-center no-wrap">
				<div class="details-header-icon q-mr-md">
					<q-icon name="school" size="28px" color="primary" />
				</div>
				<div class="col">
					<div class="text-h6">{{ selectedCourse?.title || "Курс" }}</div>
					<div class="text-body2 text-grey-7 q-mt-xs">
						Тренингов в курсе: {{ selectedCourse?.trainings?.length || 0 }}
					</div>
				</div>
				<q-btn icon="close" flat round dense v-close-popup color="grey-7" />
			</q-card-section>
			<q-separator />
			<q-card-section class="details-body">
				<div v-if="!(selectedCourse?.trainings?.length)" class="page-empty" style="border: none; background: transparent;">
					<div class="page-empty__icon" style="width: 64px; height: 64px; margin-bottom: 16px;">
						<q-icon name="auto_stories" size="32px" />
					</div>
					<h3 class="page-empty__title" style="font-size: 18px;">В этом курсе пока нет тренингов</h3>
				</div>

				<div v-else class="course-trainings-list">
					<div
						v-for="(training, index) in selectedCourse?.trainings || []"
						:key="training.uuid"
						class="page-list-item"
					>
						<div class="page-list-item__number">{{ index + 1 }}</div>
						<div class="page-list-item__icon">
							<q-icon name="play_lesson" size="22px" />
						</div>
						<div class="col overflow-hidden q-pr-md">
							<div class="text-subtitle1 text-weight-bold text-dark ellipsis q-mb-xs" :title="training.title">
								{{ training.title }}
							</div>
							<div class="row items-center text-caption text-grey-6 q-gutter-x-md">
								<span class="row items-center">
									<q-icon name="trending_up" size="16px" class="q-mr-xs" />
									{{ training.level?.label ?? "Без уровня" }}
								</span>
								<span class="row items-center">
									<q-icon name="schedule" size="16px" class="q-mr-xs" />
									{{ training.duration_minutes || "—" }} мин
								</span>
								<span
									class="page-status"
									:class="training.publish ? 'page-status--published' : 'page-status--draft'"
								>
									{{ training.publish ? "Опубликован" : "Черновик" }}
								</span>
							</div>
						</div>
						<div class="row items-center q-gutter-x-sm no-wrap">
							<q-btn
								flat
								dense
								no-caps
								color="primary"
								icon="edit"
								class="btn-rounded q-px-sm"
								label="Открыть"
								@click.stop="openTrainingEditor(training.uuid)"
							/>
							<q-btn
								unelevated
								dense
								no-caps
								color="primary"
								icon="play_arrow"
								class="btn-rounded q-px-sm"
								label="Пройти"
								@click.stop="startTrainingPassage(training)"
							/>
						</div>
					</div>
				</div>
			</q-card-section>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useQuasar } from "quasar";
import { useRouter } from "vue-router";
import { CourseApi, TrainingApi } from "@api";
import PageShell from "@components/common/PageShell.vue";

const $q = useQuasar();
const router = useRouter();
const courseApi = new CourseApi();
const trainingApi = new TrainingApi();

const loading = ref(true);
const courses = ref([]);
const trainings = ref([]);

const searchQuery = ref("");
const filterTab = ref("all");

const createModal = ref(false);
const detailsModal = ref(false);
const selectedCourse = ref(null);

const searchTrainings = ref("");
const form = ref({
	title: "",
	description: "",
	training_uuids: [],
});

const selectedSet = computed(() => new Set(form.value.training_uuids));
const canCreate = computed(() => !!form.value.title && form.value.training_uuids.length > 0);

const filteredTrainingsForCreate = computed(() => {
	const query = searchTrainings.value.trim().toLowerCase();
	if (!query) return trainings.value;
	return trainings.value.filter((item) => item.title?.toLowerCase().includes(query));
});

const filteredCourses = computed(() => {
	const q = searchQuery.value.trim().toLowerCase();
	let result = courses.value;
	if (filterTab.value === "published") {
		result = result.filter((course) => publishedCount(course) > 0);
	}
	if (filterTab.value === "draft") {
		result = result.filter((course) => publishedCount(course) === 0);
	}
	if (q) {
		result = result.filter((course) => {
			const inTitle = course.title?.toLowerCase().includes(q);
			const inDesc = course.description?.toLowerCase().includes(q);
			const inTrainings = (course.trainings || []).some((t) => t.title?.toLowerCase().includes(q));
			return inTitle || inDesc || inTrainings;
		});
	}
	return result;
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

function publishedCount(course) {
	return (course.trainings || []).filter((t) => t.publish).length;
}

function courseStatusLabel(course) {
	const total = (course.trainings || []).length;
	const pub = publishedCount(course);
	if (total === 0) return "Пустой курс";
	if (pub === 0) return "Черновик";
	if (pub === total) return "Готов к прохождению";
	return "Частично опубликован";
}

function courseStatusClass(course) {
	const total = (course.trainings || []).length;
	const pub = publishedCount(course);
	if (total === 0 || pub === 0) return "page-status--draft";
	if (pub === total) return "page-status--published";
	return "page-status--mixed";
}

function resetCreateForm() {
	form.value = { title: "", description: "", training_uuids: [] };
	searchTrainings.value = "";
}

function resetFilters() {
	searchQuery.value = "";
	filterTab.value = "all";
}

function openCreateModal() {
	resetCreateForm();
	createModal.value = true;
}

function openDetails(course) {
	selectedCourse.value = course;
	detailsModal.value = true;
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
		$q.notify({ message: "Курс создан", type: "positive", position: "top-right" });
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

function openTrainingEditor(uuid) {
	const route = router.resolve(`/edit/${uuid}`);
	window.open(route.href, "_blank");
}

function extractTokenFromPublishResponse(data) {
	if (!data) return null;
	if (data.access_token) return data.access_token;
	const link = data.public_link || "";
	if (!link) return null;
	const chunks = String(link).split("/").filter(Boolean);
	return chunks[chunks.length - 1] || null;
}

async function startTrainingPassage(training) {
	try {
		const { data } = await trainingApi.publishTraining(training.uuid);
		const token = extractTokenFromPublishResponse(data);
		if (!token) throw new Error("No passage token");
		const route = router.resolve(`/training/passage/${token}/welcome`);
		window.open(route.href, "_blank");
	} catch (error) {
		console.error(error);
		$q.notify({
			message: "Не удалось запустить прохождение",
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
			$q.notify({ message: "Курс удален", type: "positive", position: "top-right" });
			if (selectedCourse.value?.id === course.id) detailsModal.value = false;
			await fetchData();
		} catch (error) {
			console.error(error);
			$q.notify({ message: "Не удалось удалить курс", type: "negative", position: "top" });
		}
	});
}

onMounted(fetchData);
</script>

<style scoped>
.card-content {
	padding: 0;
	flex: 1;
	display: flex;
	flex-direction: column;
}

.course-badge {
	background: #f1f5f9;
	color: #475569;
	border: 1px solid #e2e8f0;
	border-radius: 8px;
	padding: 5px 10px;
	font-size: 12px;
	font-weight: 500;
}

.course-badge--more {
	color: #5064f7;
	background: rgba(80, 100, 247, 0.08);
	border-color: rgba(80, 100, 247, 0.2);
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

.course-modal,
.details-modal {
	width: min(820px, 95vw);
	max-width: 95vw;
	border-radius: 20px !important;
	overflow: hidden;
}

.trainings-select-list {
	max-height: 320px;
	overflow: auto;
	border-radius: 10px;
}

.details-header {
	padding: 20px 24px;
	background: linear-gradient(135deg, rgba(80, 100, 247, 0.04) 0%, rgba(80, 100, 247, 0.01) 100%);
}

.details-header-icon {
	width: 52px;
	height: 52px;
	border-radius: 14px;
	background: rgba(80, 100, 247, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
}

.details-body {
	padding: 20px 24px;
	max-height: 65vh;
	overflow-y: auto;
}

.course-trainings-list {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.btn-rounded {
	border-radius: 10px;
}
</style>
