<template>
	<q-dialog ref="dialog" v-model="showModal" persistent>
		<q-card class="training-modal" flat bordered>
			<q-card-section class="training-modal__header">
				<div class="training-modal__title">
					{{ mode === "edit" ? "Настройки тренинга" : "Создание тренинга" }}
				</div>
				<q-btn flat round dense icon="close" v-close-popup :disable="loading" />
			</q-card-section>

			<q-card-section class="training-modal__body">
				<div v-if="metaLoading" class="training-modal__loading">
					<q-spinner-dots size="40px" color="primary" />
				</div>

				<div class="training-modal__layout">
					<!-- Обложка -->
					<div class="training-modal__cover">
						<div
							class="cover-preview"
							:style="iconPreviewUrl ? { backgroundImage: `url(${iconPreviewUrl})` } : {}"
						>
							<div v-if="!iconPreviewUrl" class="cover-placeholder">
								<q-icon name="image" size="28px" />
								<span>Обложка тренинга</span>
							</div>
						</div>
						<input
							ref="iconInput"
							type="file"
							accept="image/jpeg, image/png, image/webp"
							class="hidden"
							@change="handleIconSelect"
						/>
						<q-btn
							outline
							no-caps
							color="primary"
							label="Загрузить обложку"
							size="sm"
							class="cover-btn"
							@click="triggerIconUpload"
						/>
						<span class="cover-hint">JPG, PNG, WebP до 2 МБ</span>
					</div>

					<!-- Основное -->
					<div class="form-group">
						<label class="form-group__label">Название</label>
						<q-input
							v-model="dataTraining.title"
							outlined
							dense
							placeholder="Введите название тренинга"
							color="primary"
							:rules="[(v) => !!v?.trim() || 'Обязательное поле']"
							lazy-rules
							autofocus
						/>
					</div>

					<div class="form-group">
						<label class="form-group__label">Описание</label>
						<q-input
							v-model="dataTraining.description"
							outlined
							dense
							placeholder="Кратко опишите содержание"
							type="textarea"
							autogrow
							color="primary"
							:input-style="{ minHeight: '88px' }"
						/>
					</div>

					<div class="form-row">
						<div class="form-group form-group--half">
							<label class="form-group__label">Минут на прохождение</label>
							<q-input
								v-model.number="dataTraining.duration_minutes"
								outlined
								dense
								type="number"
								min="0"
								placeholder="0"
								color="primary"
							/>
						</div>
						<div class="form-group form-group--half">
							<label class="form-group__label">Уровень подготовки</label>
							<q-select
								v-model="dataTraining.level_id"
								outlined
								dense
								emit-value
								map-options
								option-value="value"
								option-label="label"
								:options="levelList"
								placeholder="Выбрать"
								color="primary"
								behavior="menu"
							/>
						</div>
					</div>

					<div class="form-group">
						<label class="form-group__label">Теги</label>
						<q-select
							ref="tagSelectRef"
							v-model="dataTraining.tag_ids"
							outlined
							dense
							multiple
							options-dense
							emit-value
							map-options
							option-value="value"
							option-label="label"
							:options="tagSelectOptions"
							use-chips
							max-values="3"
							use-input
							@filter="filterTags"
							@input-value="onInputValue"
							@popup-show="onPopupShow"
							new-value-mode="add-unique"
							@new-value="onNewValue"
							input-debounce="0"
							placeholder="Начните вводить или нажмите Enter"
							color="primary"
							class="tags-select"
							behavior="menu"
							menu-shrink
							menu-anchor="bottom left"
							menu-self="top left"
							:menu-offset="[0, 8]"
						>
							<template #no-option>
								<q-item
									v-if="currentInputValue.trim()"
									clickable
									class="tags-create-item"
									@click.prevent.stop="createNewTagFromInput"
								>
									<q-item-section avatar>
										<q-icon name="add_circle_outline" color="primary" />
									</q-item-section>
									<q-item-section>
										<q-item-label>
											Создать тег «<strong>{{ currentInputValue.trim() }}</strong>»
										</q-item-label>
									</q-item-section>
								</q-item>
								<q-item v-else>
									<q-item-section class="text-grey-7 text-center">
										<span>Введите название и нажмите Enter</span>
									</q-item-section>
								</q-item>
							</template>
						</q-select>
					</div>

					<div class="toggles">
						<div class="toggle-row">
							<q-toggle
								v-model="dataTraining.skip_steps"
								color="primary"
							/>
							<div class="toggle-row__text">
								<div class="toggle-row__title">Прохождение в любом порядке</div>
								<div class="toggle-row__desc">Разрешить пользователям проходить шаги не последовательно</div>
							</div>
						</div>
						<div class="toggle-row">
							<q-toggle
								v-model="dataTraining.hints_enabled"
								color="primary"
							/>
							<div class="toggle-row__text">
								<div class="toggle-row__title">Подсказки в процессе прохождения</div>
								<div class="toggle-row__desc">Показывать кнопку подсказок, если пользователь застрял</div>
							</div>
						</div>
					</div>
				</div>
			</q-card-section>

			<q-card-actions class="training-modal__actions">
				<q-btn
					flat
					no-caps
					rounded
					label="Отмена"
					v-close-popup
					:disable="loading"
				/>
				<q-btn
					unelevated
					no-caps
					rounded
					color="primary"
					:label="mode === 'edit' ? 'Сохранить изменения' : 'Создать тренинг'"
					:loading="loading"
					:disable="loading || !dataTraining.title?.trim()"
					class="training-modal__submit"
					@click="submitTraining"
				/>
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { useQuasar } from "quasar";
import { TrainingApi } from "@api/api/TrainingApi.js";
import { MetaTrainingApi } from "@api/api/MetaTrainingApi.js";
import { trainingEvents } from "@utils/eventBus.js";

const props = defineProps({
	mode: { type: String, default: "create" },
	editData: { type: Object, default: null }
});

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
	skip_steps: false,
	hints_enabled: true
});

const showModal = defineModel();
const filteredTags = ref([]);
const currentInputValue = ref("");
const tagSelectRef = ref(null);
const creatingTag = ref(false);

const iconInput = ref(null);
const selectedIconFile = ref(null);
const iconPreviewUrl = ref(null);

const triggerIconUpload = () => {
	if (iconInput.value) {
		iconInput.value.click();
	}
};

const handleIconSelect = (event) => {
	const file = event.target.files[0];
	if (!file) return;

	if (file.size > 2 * 1024 * 1024) {
		$q.notify({
			message: "Файл слишком большой (максимум 2MB)",
			type: "negative",
			position: "top"
		});
		return;
	}

	selectedIconFile.value = file;
	iconPreviewUrl.value = URL.createObjectURL(file);
};

const tagSelectOptions = computed(() => filteredTags.value);

function onPopupShow() {
	filteredTags.value = [...listTags.value];
	currentInputValue.value = "";
}

function filterTags(val, update) {
	update(() => {
		const search = (val || "").trim().toLowerCase();
		if (!search) {
			filteredTags.value = [...listTags.value];
		} else {
			filteredTags.value = listTags.value.filter((tag) =>
				(tag.label || "").toLowerCase().includes(search)
			);
		}
	});
}

function onInputValue(val) {
	currentInputValue.value = val ?? "";
}

async function performCreateTag(label) {
	const trimmed = (label || "").trim();
	if (!trimmed) return null;
	const res = await metaApi.createTag(trimmed);
	const tag = { value: res.data.value, label: res.data.label };
	const exists = listTags.value.some((t) => t.value === tag.value);
	if (!exists) {
		listTags.value = [...listTags.value, tag].sort((a, b) =>
			(a.label || "").localeCompare(b.label || "")
		);
	}
	filteredTags.value = [...listTags.value];
	currentInputValue.value = "";
	return tag;
}

async function onNewValue(inputValue, doneFn) {
	const label = inputValue?.trim();
	if (!label || creatingTag.value) {
		doneFn?.(null);
		return;
	}

	creatingTag.value = true;
	try {
		const existing = listTags.value.find(
			(t) => (t.label || "").trim().toLowerCase() === label.toLowerCase()
		);

		const newTag = existing ?? (await performCreateTag(label));
		if (!newTag) {
			doneFn?.(null);
			return;
		}

		const nextIds = Array.from(
			new Set([...(dataTraining.value.tag_ids || []), newTag.value])
		);
		dataTraining.value = { ...dataTraining.value, tag_ids: nextIds };

		$q.notify({
			color: "positive",
			message: existing
				? `Тег «${newTag.label}» добавлен`
				: `Тег «${newTag.label}» создан`,
			position: "top",
			timeout: 1500,
		});

		doneFn?.(null);
	} catch (e) {
		console.error("Error creating tag:", e);
		const msg =
			e?.response?.status === 401
				? "Ошибка авторизации. Войдите в систему"
				: e?.response?.data?.detail || e?.message || "Не удалось создать тег";
		$q.notify({ color: "negative", message: msg, position: "top", timeout: 3000 });
		doneFn?.(null);
	} finally {
		creatingTag.value = false;
	}
}

async function createNewTagFromInput() {
	const label = currentInputValue.value.trim();
	if (!label || creatingTag.value) return;
	creatingTag.value = true;
	try {
		const newTag = await performCreateTag(label);
		if (newTag) {
			const nextIds = Array.from(
				new Set([...(dataTraining.value.tag_ids || []), newTag.value])
			);
			dataTraining.value = { ...dataTraining.value, tag_ids: nextIds };

			$q.notify({
				color: "positive",
				message: `Тег «${newTag.label}» создан и добавлен`,
				position: "top",
				timeout: 1500,
			});
		}
		currentInputValue.value = "";
		tagSelectRef.value?.hidePopup?.();
	} catch (e) {
		console.error("Error creating tag:", e);
		const msg =
			e?.response?.status === 401
				? "Ошибка авторизации. Войдите в систему"
				: e?.response?.data?.detail || e?.message || "Не удалось создать тег";
		$q.notify({ color: "negative", message: msg, position: "top", timeout: 3000 });
	} finally {
		creatingTag.value = false;
	}
}

function resetForm() {
	dataTraining.value = {
		title: "",
		description: "",
		tag_ids: [],
		duration_minutes: null,
		level_id: null,
		skip_steps: false,
		hints_enabled: true
	};
	currentInputValue.value = "";
	selectedIconFile.value = null;
	iconPreviewUrl.value = null;
}

async function submitTraining() {
	if (!dataTraining.value.title?.trim()) return;
	try {
		loading.value = true;
		const payload = {
			...dataTraining.value,
			duration_minutes: dataTraining.value.duration_minutes ?? undefined
		};

		let trainingUuid = null;

		if (props.mode === "create") {
			const res = await trainingApi.createTraining(payload);
			trainingUuid = res?.data?.data?.uuid || null;
			if (!trainingUuid) {
				throw new Error("Не удалось получить UUID созданного тренинга");
			}
			$q.notify({
				color: "positive",
				message: "Тренинг создан",
				position: "bottom-right",
				icon: "check_circle"
			});
		} else {
			trainingUuid = props.editData.uuid;
			await trainingApi.updateTraining(trainingUuid, payload);
			$q.notify({
				color: "positive",
				message: "Тренинг обновлён",
				position: "bottom-right",
				icon: "check_circle"
			});
		}

		if (selectedIconFile.value && trainingUuid) {
			try {
				const formData = new FormData();
				formData.append("file", selectedIconFile.value);
				await trainingApi.uploadIcon(trainingUuid, formData);
				await new Promise((resolve) => setTimeout(resolve, 500));
			} catch (iconError) {
				console.error("Ошибка загрузки иконки:", iconError);
				$q.notify({
					color: "warning",
					message: "Тренинг сохранён, но не удалось загрузить обложку",
					position: "top"
				});
			}
		}

		trainingEvents.created.trigger();
		showModal.value = false;
		resetForm();
	} catch (e) {
		console.error(e);
		$q.notify({
			color: "negative",
			message: props.mode === "create" ? "Не удалось создать тренинг" : "Не удалось обновить тренинг",
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
		if (props.mode === "edit" && props.editData) {
			dataTraining.value = {
				title: props.editData.title || "",
				description: props.editData.description || "",
				tag_ids: props.editData.tags?.map((t) => t.value) || [],
				duration_minutes: props.editData.duration_minutes || null,
				level_id: props.editData.level?.value || null,
				skip_steps: props.editData.skip_steps || false,
				hints_enabled: props.editData.hints_enabled !== false,
			};
			if (props.editData.icon) {
				iconPreviewUrl.value = props.editData.icon;
			}
		}
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
.training-modal {
	width: 640px;
	max-width: 95vw;
	border-radius: 24px;
	overflow: hidden;
	background: #fff;
	box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
}

.training-modal__header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20px 24px;
	border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.training-modal__title {
	font-size: 20px;
	font-weight: 750;
	color: #0f172a;
	letter-spacing: -0.02em;
}

.training-modal__body {
	position: relative;
	padding: 28px 24px;
	max-height: 78vh;
	overflow-y: auto;
}

.training-modal__loading {
	position: absolute;
	inset: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(255, 255, 255, 0.92);
	z-index: 10;
}

.training-modal__layout {
	display: flex;
	flex-direction: column;
	gap: 22px;
}

/* Cover */
.training-modal__cover {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: 12px;
}

.cover-preview {
	width: 100%;
	height: 160px;
	border-radius: 16px;
	background: linear-gradient(135deg, rgba(80, 100, 247, 0.08) 0%, rgba(168, 85, 247, 0.05) 100%);
	background-size: cover;
	background-position: center;
	display: flex;
	align-items: center;
	justify-content: center;
	border: 1px dashed rgba(15, 23, 42, 0.15);
	transition: border-color 0.2s ease;
}

.cover-placeholder {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8px;
	color: #94a3b8;
	font-size: 14px;
	font-weight: 500;
}

.cover-btn {
	border-radius: 10px;
	font-weight: 600;
}

.cover-hint {
	font-size: 12px;
	color: #94a3b8;
}

/* Form groups */
.form-group {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.form-group__label {
	font-size: 13px;
	font-weight: 650;
	color: #374151;
	letter-spacing: -0.01em;
}

.form-row {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16px;
}

/* Inputs */
:deep(.q-field__control) {
	border-radius: 12px !important;
}

:deep(.q-field__control):before {
	border-color: rgba(0, 0, 0, 0.1);
}

:deep(.q-field__control):hover:before {
	border-color: rgba(80, 100, 247, 0.45);
}

:deep(.q-field--focused .q-field__control):after {
	border-width: 1.5px;
	border-color: #5064f7;
}

/* Tags select */
.tags-select :deep(.q-field__native) {
	padding-top: 2px;
	padding-bottom: 2px;
}

.tags-select :deep(.q-chip) {
	border-radius: 8px;
	background: rgba(80, 100, 247, 0.1);
}

.tags-select :deep(.q-chip__content) {
	font-size: 12px;
	font-weight: 600;
}

.tags-select :deep(.q-menu) {
	z-index: 6000;
}

/* Toggles */
.toggles {
	display: flex;
	flex-direction: column;
	gap: 16px;
	padding-top: 6px;
}

.toggle-row {
	display: flex;
	align-items: flex-start;
	gap: 12px;
	padding: 14px 16px;
	border: 1px solid rgba(0, 0, 0, 0.05);
	border-radius: 14px;
	background: rgba(255, 255, 255, 0.5);
	transition: border-color 0.2s ease;
}

.toggle-row:hover {
	border-color: rgba(80, 100, 247, 0.18);
}

.toggle-row__title {
	font-size: 14px;
	font-weight: 650;
	color: #0f172a;
	line-height: 1.3;
	margin-bottom: 2px;
}

.toggle-row__desc {
	font-size: 13px;
	color: #64748b;
	line-height: 1.4;
}

/* Actions */
.training-modal__actions {
	display: flex;
	justify-content: flex-end;
	gap: 12px;
	padding: 16px 24px;
	border-top: 1px solid rgba(0, 0, 0, 0.05);
	background: #fafbfc;
}

.training-modal__submit {
	border-radius: 12px;
	padding: 10px 24px;
	font-weight: 600;
	box-shadow: 0 4px 14px rgba(80, 100, 247, 0.28);
	transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.training-modal__submit:hover:not(:disabled) {
	transform: translateY(-1px);
	box-shadow: 0 6px 20px rgba(80, 100, 247, 0.35);
}

@media (max-width: 640px) {
	.training-modal__body {
		padding: 20px 16px;
	}

	.form-row {
		grid-template-columns: 1fr;
	}

	.toggle-row {
		align-items: center;
	}

	.training-modal__actions {
		flex-direction: column-reverse;
		align-items: stretch;
	}

	.training-modal__submit,
	.training-modal__actions .q-btn {
		width: 100%;
	}
}
</style>
