<template>
	<q-dialog ref="dialog" v-model="showModal" persistent>
		<q-card class="training-modal-card">
			<q-card-section class="modal-header row items-center">
				<div class="modal-header-content">
					<q-icon name="school" size="28px" color="primary" class="q-mr-sm" />
					<span class="text-h6">Создание тренинга</span>
				</div>
				<q-space />
				<q-btn flat round dense icon="close" v-close-popup :disable="loading" />
			</q-card-section>

			<q-card-section class="modal-body">
				<div v-if="metaLoading" class="modal-loading-overlay">
					<q-spinner-dots size="40px" color="primary" />
				</div>

				<!-- Основное -->
				<div class="form-section form-section--spaced">
					<div class="form-section-label">
						<q-icon name="edit_note" size="18px" />
						<span>Основное</span>
					</div>
				<q-input
					v-model="dataTraining.title"
					outlined
					dense
					rounded
					label="Название"
					placeholder="Введите название тренинга"
					color="primary"
					:rules="[(v) => !!v?.trim() || 'Обязательное поле']"
					lazy-rules
					class="form-field"
					autofocus
				/>
				<q-input
					v-model="dataTraining.description"
					outlined
					dense
					rounded
					label="Описание"
					placeholder="Кратко опишите содержание тренинга"
					type="textarea"
					rows="3"
					color="primary"
					autogrow
					class="form-field form-field--textarea"
				/>
				</div>

				<q-separator class="modal-separator" />

				<!-- Дополнительно -->
				<div class="form-section form-section--spaced">
					<div class="form-section-label">
						<q-icon name="label" size="18px" />
						<span>Дополнительно</span>
					</div>
				<q-select
					ref="tagSelectRef"
					v-model="dataTraining.tag_ids"
					outlined
					dense
					rounded
					multiple
					emit-value
					map-options
					option-value="value"
					option-label="label"
					:options="filteredTags"
					use-chips
					use-input
					@filter="filterTags"
					@input-value="onInputValue"
					@popup-show="onPopupShow"
					new-value-mode="add-unique"
					@new-value="createNewTag"
					input-debounce="0"
					label="Теги"
					placeholder="Введите для поиска или добавьте новый тег (Enter)"
					color="primary"
					class="form-field tags-select"
				>
					<template v-slot:no-option>
						<q-item>
							<q-item-section class="text-grey-7 text-center">
								<div>Ничего не найдено.</div>
								<div class="text-caption">Нажмите Enter для создания нового тега "<strong>{{ currentInputValue }}</strong>"</div>
							</q-item-section>
						</q-item>
					</template>
				</q-select>
					<div class="row q-col-gutter-md">
						<div class="col-6">
						<q-input
							v-model.number="dataTraining.duration_minutes"
							outlined
							dense
							rounded
							type="number"
							min="0"
							label="Продолжительность (мин)"
							placeholder="0"
							color="primary"
							class="form-field"
						/>
					</div>
					<div class="col-6">
						<q-select
							v-model="dataTraining.level_id"
							outlined
							dense
							rounded
							emit-value
							map-options
							option-value="value"
							option-label="label"
							:options="levelList"
							label="Уровень подготовки"
							placeholder="Выберите уровень"
							color="primary"
							behavior="menu"
							class="form-field"
						/>
						</div>
					</div>
				</div>

				<q-separator class="modal-separator" />

				<!-- Настройки -->
				<div class="form-section">
					<div class="form-section-label">
						<q-icon name="tune" size="18px" />
						<span>Настройки</span>
					</div>
					<div class="row items-center q-gutter-sm">
						<q-toggle
							v-model="dataTraining.skip_steps"
							color="primary"
							size="lg"
						/>
						<div>
							<span class="text-body2 text-weight-medium">Пропуск шагов</span>
							<p class="text-caption text-grey-7 q-ma-none">Прохождение в любом порядке</p>
						</div>
						<q-icon name="help_outline" size="20px" color="grey-6" class="cursor-help">
							<q-tooltip anchor="top middle" :offset="[0, 8]">
								Позволяет проходить шаги тренинга в произвольной последовательности
							</q-tooltip>
						</q-icon>
					</div>
				</div>
			</q-card-section>

			<q-card-actions class="modal-actions">
				<q-btn
					flat
					no-caps
					rounded
					label="Отмена"
					v-close-popup
					:disable="loading"
				/>
				<q-space />
				<q-btn
					unelevated
					no-caps
					rounded
					color="primary"
					icon="add"
					label="Создать тренинг"
					:loading="loading"
					:disable="loading || !dataTraining.title?.trim()"
					class="btn-create-training"
					@click="createTraining"
				/>
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { ref, watch } from "vue";
import { useQuasar } from "quasar";
import { TrainingApi } from "@api/api/TrainingApi.js";
import { MetaTrainingApi } from "@api/api/MetaTrainingApi.js";
import { trainingEvents } from "@utils/eventBus.js";

const $q = useQuasar();
const metaApi = new MetaTrainingApi();
const trainingApi = new TrainingApi();

const listTags = ref([]);
const levelList = ref([]);
const metaLoading = ref(false);
const loading = ref(false);

const dataTraining = ref({
	title: "",
	description: "",
	tag_ids: [],
	duration_minutes: null,
	level_id: null,
	skip_steps: false
});

const showModal = defineModel();
const filteredTags = ref([]);
const currentInputValue = ref('');
const tagSelectRef = ref(null);

function onPopupShow() {
	// При открытии списка показываем все теги
	filteredTags.value = listTags.value;
	currentInputValue.value = '';
}

function filterTags(val, update) {
	update(() => {
		if (val === '') {
			filteredTags.value = listTags.value;
		} else {
			const needle = val.toLowerCase();
			filteredTags.value = listTags.value.filter(
				tag => tag.label.toLowerCase().includes(needle)
			);
		}
	});
}

function onInputValue(val) {
	currentInputValue.value = val;
}

async function createNewTag(inputValue, doneFn) {
	const label = inputValue?.trim();
	
	if (!label) {
		doneFn(null);
		return;
	}
	
	// Создаём или получаем существующий тег через API
	try {
		const response = await metaApi.createTag(label);
		const newTag = { value: response.data.value, label: response.data.label };
		
		// Проверяем, есть ли уже этот тег в списке
		const existingIndex = listTags.value.findIndex(t => t.value === newTag.value);
		
		if (existingIndex === -1) {
			// Добавляем новый тег в список
			listTags.value = [...listTags.value, newTag].sort((a, b) =>
				(a.label || "").localeCompare(b.label || "")
			);
			
			$q.notify({
				color: "positive",
				message: `Тег "${newTag.label}" создан`,
				position: "top",
				timeout: 1500
			});
		} else {
			// Тег уже был в списке
			$q.notify({
				color: "info",
				message: `Тег "${newTag.label}" уже существует`,
				position: "top",
				timeout: 1500
			});
		}
		
		// Обновляем отфильтрованный список
		filteredTags.value = listTags.value;
		
		// Очищаем текущий input
		currentInputValue.value = '';
		
		// Возвращаем value тега в q-select
		doneFn(newTag.value, 'add-unique');
		
	} catch (e) {
		console.error('Error creating tag:', e);
		
		let msg = "Не удалось создать тег";
		
		if (e?.response?.status === 401) {
			msg = "Ошибка авторизации. Пожалуйста, войдите в систему";
		} else if (e?.response?.data?.detail) {
			msg = e.response.data.detail;
		} else if (e?.message) {
			msg = e.message;
		}
		
		$q.notify({ 
			color: "negative", 
			message: msg, 
			position: "top",
			timeout: 3000
		});
		doneFn(null);
	}
}

function resetForm() {
	dataTraining.value = {
		title: "",
		description: "",
		tag_ids: [],
		duration_minutes: null,
		level_id: null,
		skip_steps: false
	};
	currentInputValue.value = '';
}

async function createTraining() {
	if (!dataTraining.value.title?.trim()) return;
	try {
		loading.value = true;
		const payload = {
			...dataTraining.value,
			duration_minutes: dataTraining.value.duration_minutes ?? undefined
		};
		await trainingApi.createTraining(payload);
		trainingEvents.created.trigger();
		showModal.value = false;
		resetForm();
		$q.notify({
			color: "positive",
			message: "Тренинг создан",
			position: "bottom-right",
			icon: "check_circle"
		});
	} catch (e) {
		console.error(e);
		$q.notify({
			color: "negative",
			message: "Не удалось создать тренинг",
			position: "top",
			icon: "error"
		});
	} finally {
		loading.value = false;
	}
}

watch(showModal, async (val) => {
	if (val) {
		resetForm();
		metaLoading.value = true;
		try {
			const [tagsRes, levelsRes] = await Promise.all([
				metaApi.getTags(),
				metaApi.getLevels()
			]);
			listTags.value = tagsRes.data ?? [];
			filteredTags.value = tagsRes.data ?? [];
			levelList.value = levelsRes.data ?? [];
		} catch {
			$q.notify({
				color: "negative",
				message: "Ошибка загрузки данных",
				position: "top"
			});
		} finally {
			metaLoading.value = false;
		}
	}
});
</script>

<style scoped>
.training-modal-card {
	width: 520px;
	max-width: 95vw;
	border-radius: 16px;
	overflow: visible;
	box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.modal-header {
	padding: 20px 24px;
	background: linear-gradient(135deg, rgba(80, 100, 247, 0.04) 0%, rgba(80, 100, 247, 0.01) 100%);
	border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.modal-header-content {
	display: flex;
	align-items: center;
}

.modal-body {
	position: relative;
	min-height: 300px;
	padding: 24px 28px 20px;
	background: #fff;
}

.modal-loading-overlay {
	position: absolute;
	inset: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(255, 255, 255, 0.9);
	z-index: 10;
}

.form-section {
	margin-bottom: 0;
	position: relative;
}

.form-section--spaced {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.form-section--spaced .row {
	margin-top: 0;
	margin-bottom: 0;
}

.form-section-label {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 13px;
	font-weight: 600;
	color: #374151;
	margin-bottom: 12px;
}

.form-section-label .q-icon {
	opacity: 0.8;
}

.form-field {
	display: block;
	width: 100%;
	flex-shrink: 0;
}

.form-field :deep(.q-field__control) {
	border-radius: 12px;
}

.form-field :deep(.q-field__control):before {
	border-color: rgba(0, 0, 0, 0.12);
}

.form-field :deep(.q-field__control):hover:before {
	border-color: rgba(80, 100, 247, 0.5);
}

.form-field--textarea {
	min-height: 90px;
}

.form-field--textarea :deep(.q-field__control) {
	min-height: 90px;
}

.tags-select {
	min-height: 56px;
	position: relative;
	z-index: 1;
}

.tags-select :deep(.q-chip) {
	border-radius: 8px;
	background: rgba(80, 100, 247, 0.1);
}

.tags-select :deep(.q-chip__icon) {
	color: rgba(80, 100, 247, 0.8);
}

.modal-separator {
	margin: 20px 0;
	background: rgba(0, 0, 0, 0.06);
}

.modal-actions {
	padding: 16px 28px;
	border-top: 1px solid rgba(0, 0, 0, 0.06);
	background: #fafbfc;
}

.btn-create-training {
	border-radius: 24px;
	padding: 10px 24px;
	font-weight: 500;
	box-shadow: 0 2px 10px rgba(80, 100, 247, 0.25);
	transition: box-shadow 0.2s, transform 0.2s;
}

.btn-create-training:hover:not(:disabled) {
	box-shadow: 0 4px 18px rgba(80, 100, 247, 0.4);
	transform: translateY(-1px);
}
</style>
