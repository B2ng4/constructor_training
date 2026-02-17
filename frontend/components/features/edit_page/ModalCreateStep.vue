<template>
	<q-dialog v-model="value" persistent>
		<q-card class="modal-create-step relative-position">
			<video-processing-loader v-if="loading && uploadMode === 'video'" />
			<q-inner-loading :showing="loading && uploadMode === 'photos'">
				<q-spinner-gears size="48px" color="primary" />
			</q-inner-loading>
			<q-card-section class="row items-center q-pb-sm">
				<div class="text-h6">Добавить шаги</div>
				<q-space />
				<q-btn flat dense round icon="close" v-close-popup :disable="loading" />
			</q-card-section>
			<q-card-section class="q-pt-none">
				<!-- Переключатель режима — мини-карточки -->
				<div class="mode-toggle q-mb-md">
					<div
						class="mode-card"
						:class="{ 'mode-card--active': uploadMode === 'photos' }"
						@click="uploadMode = 'photos'"
					>
						<q-icon name="photo_library" size="20px" />
						<span>Скриншоты</span>
					</div>
					<div
						class="mode-card"
						:class="{ 'mode-card--active': uploadMode === 'video' }"
						@click="uploadMode = 'video'"
					>
						<q-icon name="smart_display" size="20px" />
						<span>Видео</span>
					</div>
				</div>
				<p class="modal-hint text-caption text-grey-6 q-mt-none q-mb-md">
					{{ uploadMode === 'video'
						? 'AI создаст шаги с описаниями и определит области действий автоматически'
						: 'Загрузите изображения интерфейса для создания шагов'
					}}
				</p>
				
				<!-- Требования к видео -->
				<div v-if="uploadMode === 'video'" class="video-requirements-compact q-mb-md">
					<div class="requirements-compact-row">
						<q-icon name="timer" size="14px" color="grey-6" />
						<span>до 5 мин</span>
					</div>
					<div class="requirements-compact-row">
						<q-icon name="storage" size="14px" color="grey-6" />
						<span>до 100 МБ</span>
					</div>
					<div class="requirements-compact-row">
						<q-icon name="slow_motion_video" size="14px" color="grey-6" />
						<span>2-3 сек между действиями</span>
					</div>
				</div>
				
				<div class="modal-content-slot">
					<!-- Режим скриншотов -->
					<template v-if="uploadMode === 'photos'">
						<template v-if="images.length > 0">
							<div class="photo-list-scroll">
								<photo-list
									@delete-image="deleteImage"
									:images="images"
									:title="false"
								/>
							</div>
							<q-btn
								outline
								no-caps
								color="primary"
								icon="add_photo_alternate"
								label="Ещё фото"
								size="sm"
								class="q-mt-sm"
								@click="addPhoto"
							/>
						</template>
						<div
							v-else
							class="photo-dropzone"
							@click="addPhoto"
						>
							<q-icon name="add_photo_alternate" size="40px" color="primary" />
							<span class="text-body2 text-grey-7 q-mt-sm">Нажмите, чтобы выбрать изображения</span>
						</div>
					</template>
					<!-- Режим видео -->
					<template v-else>
						<div
							v-if="!videoFile"
							class="video-dropzone"
							@click="triggerVideoInput"
						>
							<q-icon name="smart_display" size="40px" color="primary" />
							<span class="text-body2 text-grey-7 q-mt-sm">Выберите видео (mp4, webm, avi)</span>
							<input
								ref="videoInputRef"
								type="file"
								accept="video/*"
								class="hidden"
								@change="onVideoSelected"
							/>
						</div>
						<div v-else class="video-preview">
							<div class="video-preview-icon">
								<q-icon name="smart_display" size="22px" color="primary" />
							</div>
							<div class="video-preview-info">
								<span class="video-preview-name">{{ videoFile.name }}</span>
								<span class="video-preview-size">{{ formatFileSize(videoFile.size) }}</span>
							</div>
							<q-btn flat round dense icon="close" size="sm" color="grey-6" @click.stop="clearVideo">
								<q-tooltip>Удалить</q-tooltip>
							</q-btn>
						</div>
					</template>
				</div>
			</q-card-section>
			<q-card-actions class="q-px-md q-pb-md">
				<q-space />
				<q-btn flat no-caps label="Отмена" v-close-popup :disable="loading" />
				<q-btn
					unelevated
					no-caps
					rounded
					color="primary"
					icon="add"
					:label="uploadMode === 'video' ? 'Создать шаги из видео' : 'Создать шаги'"
					:loading="loading"
					:disable="uploadMode === 'photos' ? images.length === 0 : !videoFile"
					class="btn-create-steps"
					@click="addSteps"
				/>
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { useRoute } from "vue-router";
import { MetaTrainingApi, TrainingApi } from "@api";
import { ref, watch } from "vue";
import { useQuasar } from "quasar";
import { useTrainingData } from "@store/editTraining.js";
import { PhotoList } from "@components/features/edit_page/uploader_photo";
import VideoProcessingLoader from "@components/features/edit_page/VideoProcessingLoader.vue";

const value = defineModel();
const route = useRoute();
const $q = useQuasar();
const store = useTrainingData();
const metaApi = new MetaTrainingApi();
const trainingApi = new TrainingApi();
const images = ref([]);
const loading = ref(false);
const uploadMode = ref("photos");
const videoFile = ref(null);
const videoInputRef = ref(null);

watch(uploadMode, () => {
	videoFile.value = null;
	images.value = [];
});

watch(value, (open) => {
	if (!open) {
		uploadMode.value = "photos";
		videoFile.value = null;
		images.value = [];
	}
});

const formatFileSize = (bytes) => {
	if (!bytes) return "";
	if (bytes < 1024) return bytes + " Б";
	if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " КБ";
	return (bytes / (1024 * 1024)).toFixed(1) + " МБ";
};

const triggerVideoInput = () => videoInputRef.value?.click();

const onVideoSelected = (event) => {
	const file = event.target.files?.[0];
	if (file) videoFile.value = file;
	event.target.value = "";
};

const clearVideo = () => {
	videoFile.value = null;
	if (videoInputRef.value) videoInputRef.value.value = "";
};

const addPhoto = () => {
	const input = document.createElement('input');
	input.type = 'file';
	input.multiple = true;
	input.accept = 'image/*';

	input.onchange = (event) => {
		const files = event.target.files;
		if (!files || files.length === 0) return;

		const newImages = Array.from(files).map((file, index) => ({
			id: Date.now() + index,
			name: file.name,
			url: URL.createObjectURL(file),
			size: file.size,
			originalFile: file,
		}));

		images.value = [...images.value, ...newImages];
	};
	input.click();
};

const deleteImage = (id) => {
	images.value = images.value.filter((el) => el.id !== id);
};

const addSteps = async () => {
	loading.value = true;
	try {
		if (uploadMode.value === "video" && videoFile.value) {
			const formData = new FormData();
			formData.append("file", videoFile.value);
			await metaApi.uploadVideo(route.params.uuid, formData);
		} else {
			const formData = new FormData();
			images.value.forEach((el) => {
				formData.append("files", el.originalFile);
			});
			await metaApi.uploadImages(route.params.uuid, formData);
		}

		const { data } = await trainingApi.getTrainingByUuid(route.params.uuid);
		store.setTrainingData(data);

		images.value = [];
		clearVideo();
		value.value = false;

		if (uploadMode.value === "video") {
			$q.notify({
				message: "Шаги из видео успешно добавлены!",
				caption: "AI распознал действия автоматически. Вы можете отредактировать описания и уточнить области действий.",
				type: "positive",
				position: "bottom-right",
				icon: "smart_display",
				timeout: 5000,
				actions: [
					{
						label: "Понятно",
						color: "white",
						handler: () => {}
					}
				]
			});
		} else {
			$q.notify({
				message: "Шаги успешно добавлены",
				type: "positive",
				position: "top-right",
			});
		}
	} catch {
		$q.notify({
			message: uploadMode.value === "video" ? "Ошибка обработки видео" : "Ошибка создания шагов",
			type: "negative",
			position: "top",
		});
	} finally {
		loading.value = false;
	}
};
</script>

<style scoped>
.modal-create-step {
	min-width: 460px;
	max-width: 520px;
	border-radius: 14px;
}

/* ——— Переключатель ——— */
.mode-toggle {
	display: flex;
	gap: 8px;
}

.mode-card {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 8px 16px;
	border-radius: 10px;
	border: 1.5px solid rgba(0, 0, 0, 0.08);
	background: #fff;
	cursor: pointer;
	transition: all 0.2s ease;
	font-size: 13px;
	font-weight: 500;
	color: #9e9e9e;
	flex: 1;
	justify-content: center;
}

.mode-card:hover {
	border-color: rgba(80, 100, 247, 0.3);
	color: #666;
}

.mode-card--active {
	border-color: #5064f7;
	background: rgba(80, 100, 247, 0.06);
	color: #5064f7;
}

.modal-hint {
	min-height: 1.4em;
	line-height: 1.4;
}

.modal-content-slot {
	min-height: 140px;
	display: flex;
	flex-direction: column;
}

/* ——— Список фото ——— */
.photo-list-scroll {
	max-height: 240px;
	overflow-y: auto;
	border: 1px solid rgba(0, 0, 0, 0.06);
	border-radius: 10px;
	padding: 8px;
}

.photo-dropzone {
	border: 2px dashed rgba(89, 106, 246, 0.24);
	background: rgba(191, 197, 244, 0.10);
	min-height: 140px;
	border-radius: 10px;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	cursor: pointer;
	transition: background-color 0.25s, border-color 0.25s;
}

.photo-dropzone:hover {
	background: rgba(191, 197, 244, 0.2);
	border-color: rgba(89, 106, 246, 0.4);
}

/* ——— Компактные требования к видео ——— */
.video-requirements-compact {
	display: flex;
	flex-wrap: wrap;
	gap: 12px;
	padding: 10px 12px;
	background: rgba(80, 100, 247, 0.04);
	border: 1px solid rgba(80, 100, 247, 0.1);
	border-radius: 8px;
}

.requirements-compact-row {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 12px;
	color: #6b7280;
	font-weight: 500;
}

/* ——— Зона видео ——— */
.video-dropzone {
	border: 2px dashed rgba(89, 106, 246, 0.24);
	background: rgba(191, 197, 244, 0.10);
	min-height: 140px;
	border-radius: 10px;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 24px;
	cursor: pointer;
	transition: background-color 0.25s, border-color 0.25s;
}

.video-dropzone:hover {
	background: rgba(191, 197, 244, 0.2);
	border-color: rgba(89, 106, 246, 0.4);
}

/* ——— Превью видео ——— */
.video-preview {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 12px 14px;
	background: rgba(80, 100, 247, 0.05);
	border: 1px solid rgba(80, 100, 247, 0.12);
	border-radius: 10px;
	width: 100%;
}

.video-preview-icon {
	width: 40px;
	height: 40px;
	border-radius: 8px;
	background: rgba(80, 100, 247, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.video-preview-info {
	flex: 1;
	min-width: 0;
	display: flex;
	flex-direction: column;
}

.video-preview-name {
	font-size: 13px;
	font-weight: 500;
	color: #333;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.video-preview-size {
	font-size: 11px;
	color: #999;
	margin-top: 1px;
}

.btn-create-steps {
	border-radius: 24px;
	padding: 10px 20px;
	font-weight: 500;
	box-shadow: 0 2px 8px rgba(80, 100, 247, 0.2);
	transition: box-shadow 0.2s, transform 0.2s;
}
.btn-create-steps:hover:not(:disabled) {
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.35);
	transform: translateY(-1px);
}
</style>
