<template>
	<div
		class="upload-container column items-center relative-position"
		:class="{ 'upload-container--photos-filled': uploadMode === 'photos' && images.length > 0 }"
	>
		<q-inner-loading :showing="loading">
			<q-spinner-gears size="48px" color="primary" />
			<div class="q-mt-md text-primary">{{ uploadMode === 'video' ? 'Загрузка видео...' : 'Создание шагов...' }}</div>
		</q-inner-loading>

		<div class="upload-card column items-center">
			<div class="upload-icon-wrap q-mb-lg">
				<q-icon
					:name="uploadMode === 'photos' ? 'add_photo_alternate' : uploadMode === 'video' ? 'videocam' : uploadMode === 'pdf' ? 'picture_as_pdf' : 'screenshot_monitor'"
					size="48px"
					color="primary"
				/>
			</div>
			<h5 class="text-weight-bold text-grey-9 q-mb-xs q-mt-none">
				{{ uploadMode === 'photos' ? 'Начните с добавления скриншотов' : uploadMode === 'video' ? 'Загрузите видео' : uploadMode === 'pdf' ? 'Загрузите PDF инструкцию' : 'Захват экрана' }}
			</h5>
			<p
				v-if="!(uploadMode === 'photos' && images.length > 0)"
				class="text-body2 text-grey-6 text-center q-mb-lg"
				style="max-width: 420px"
			>
				{{ uploadMode === 'photos'
					? 'Загрузите изображения интерфейса, чтобы создать шаги тренинга'
					: uploadMode === 'video'
					? 'AI автоматически создаст шаги с описаниями и определит области действий'
					: uploadMode === 'pdf'
					? 'AI разберет инструкцию, извлечет скрины и определит области для клика'
					: 'Транслируйте нужный экран или окно и делайте снимки на лету'
				}}
			</p>

			<!-- Переключатель режима — карточки -->
			<div class="mode-toggle q-mb-lg">
				<div
					class="mode-card"
					:class="{ 'mode-card--active': uploadMode === 'photos' }"
					@click="uploadMode = 'photos'"
				>
					<q-icon name="photo_library" size="28px" />
					<span class="mode-label">Скриншоты</span>
					<span class="mode-desc">Пачка изображений</span>
				</div>
				<div
					class="mode-card"
					:class="{ 'mode-card--active': uploadMode === 'video' }"
					@click="uploadMode = 'video'"
				>
					<q-icon name="smart_display" size="28px" />
					<span class="mode-label">Видео</span>
					<span class="mode-desc">AI-анализ</span>
				</div>
				<div
					class="mode-card"
					:class="{ 'mode-card--active': uploadMode === 'pdf' }"
					@click="uploadMode = 'pdf'"
				>
					<q-icon name="picture_as_pdf" size="28px" />
					<span class="mode-label">PDF</span>
					<span class="mode-desc">Из инструкции</span>
				</div>
				<div
					class="mode-card"
					:class="{ 'mode-card--active': uploadMode === 'capture' }"
					@click="uploadMode = 'capture'"
				>
					<q-icon name="screenshot_monitor" size="28px" />
					<span class="mode-label">Захват</span>
					<span class="mode-desc">Live-снимки</span>
				</div>
			</div>

			<!-- Режим скриншотов -->
			<template v-if="uploadMode === 'photos'">
				<div class="row justify-center q-mb-md">
					<q-toggle
						v-model="autoDetect"
						color="primary"
						icon="auto_awesome"
						label="Автоматически определять элементы"
						left-label
					>
						<q-tooltip>Запускать YOLO-разметку UI-элементов после загрузки скриншотов</q-tooltip>
					</q-toggle>
				</div>
				<div v-if="images.length === 0" class="dropzone-wrap">
					<form-upload-photo
						@add-image="addImage"
						@download-photos="downloadPhotos"
					/>
				</div>
				<template v-else>
					<div class="photos-preview-area">
						<div class="photos-preview-scroll">
							<photo-list @delete-image="deleteImage" :images="images" :title="true" />
						</div>
						<div class="photos-actions row justify-center q-gutter-sm">
							<q-btn
								outline
								no-caps
								rounded
								color="primary"
								icon="add_photo_alternate"
								label="Ещё фото"
								class="btn-create-steps"
								@click="addMorePhotos"
							/>
							<q-btn
								unelevated
								no-caps
								rounded
								color="primary"
								icon="check"
								label="Создать шаги"
								:loading="loading"
								:disable="loading"
								class="btn-create-steps btn-create-steps--primary"
								@click="uploadImages"
							/>
						</div>
					</div>
				</template>
			</template>

			<!-- Режим захвата экрана -->
			<template v-else-if="uploadMode === 'capture'">
				<div v-if="!videoStream" class="capture-setup column items-center">
					<div class="capture-surface-grid q-mb-md">
						<button
							v-for="opt in CAPTURE_SURFACE_OPTIONS"
							:key="opt.value"
							type="button"
							class="capture-surface-card"
							:class="{ 'capture-surface-card--active': captureSurface === opt.value }"
							@click="captureSurface = opt.value"
						>
							<q-icon :name="opt.icon" size="26px" />
							<span class="capture-surface-card__label">{{ opt.label }}</span>
							<span class="capture-surface-card__desc">{{ opt.desc }}</span>
						</button>
					</div>
					<p class="capture-surface-hint text-caption text-grey-7 text-center q-mb-md">
						{{ activeCaptureHint }}
					</p>
					<div class="capture-start-card" @click="startCapture">
						<q-icon name="screen_share" size="64px" color="primary" class="q-mb-sm" />
						<span class="text-body1 text-grey-8 text-weight-medium">Предоставить доступ</span>
						<span class="text-caption text-grey-5 q-mt-xs">
							{{ captureStartCaption }}
						</span>
					</div>
				</div>

				<div v-else class="capture-container column items-center">
					<q-banner
						v-if="activeCaptureLabel"
						dense
						rounded
						class="capture-active-banner bg-blue-1 text-grey-9 q-mb-sm full-width"
					>
						<template #avatar>
							<q-icon name="fiber_manual_record" color="negative" size="12px" />
						</template>
						Захват: {{ activeCaptureLabel }}
						<template #action>
							<q-btn flat dense no-caps color="primary" label="Сменить" @click="restartCapture" />
						</template>
					</q-banner>
					<div class="video-wrapper relative-position">
						<video ref="videoPlayerRef" autoplay playsinline muted class="capture-video"></video>
					</div>
					<div class="capture-actions q-mt-md row q-gutter-sm justify-center wrap">
						<q-btn
							unelevated
							no-caps
							rounded
							color="negative"
							icon="stop_screen_share"
							label="Завершить"
							class="btn-create-steps"
							@click="finishCapture"
						/>
						<q-btn
							unelevated
							no-caps
							rounded
							color="primary"
							icon="camera"
							label="Снимок"
							class="btn-create-steps btn-create-steps--primary"
							@click="takeSnapshot"
						>
							<q-tooltip>Пробел — когда активна вкладка браузера</q-tooltip>
						</q-btn>
						<q-btn
							v-if="supportsCapturePip"
							outline
							no-caps
							rounded
							color="primary"
							icon="picture_in_picture_alt"
							label="Панель поверх экрана"
							class="btn-create-steps"
							@click="openCapturePipDock"
						/>
					</div>

					<p class="capture-keyboard-hint text-caption text-grey-6 text-center q-mt-sm q-mb-none">
						Пробел работает только в вкладке браузера. В программе — кнопка «Панель поверх экрана» или «Снимок» после Alt+Tab.
					</p>

					<div v-if="images.length" class="capture-gallery q-mt-md full-width">
						<div class="capture-gallery__header row items-center justify-between q-mb-sm">
							<span class="text-subtitle2 text-weight-medium text-grey-9">
								Снимки: {{ images.length }}
							</span>
							<q-btn
								v-if="images.length"
								flat
								dense
								no-caps
								color="primary"
								label="Создать шаги"
								icon="check"
								@click="finishCapture"
							/>
						</div>
						<div ref="captureGalleryRef" class="capture-gallery__strip">
							<div
								v-for="(img, idx) in images"
								:key="img.id"
								:data-shot-id="img.id"
								class="capture-gallery__item"
								:class="{ 'capture-gallery__item--new': highlightSnapshotId === img.id }"
								@click="previewImage = img"
							>
								<img :src="img.url" :alt="img.name" loading="lazy" />
								<span class="capture-gallery__badge">{{ idx + 1 }}</span>
								<q-btn
									class="capture-gallery__delete"
									round
									dense
									flat
									icon="close"
									color="white"
									size="xs"
									@click.stop="deleteCaptureShot(img.id)"
								/>
							</div>
						</div>
					</div>
				</div>

				<q-dialog v-model="previewOpen">
					<q-card v-if="previewImage" class="capture-preview-card">
						<q-card-section class="row items-center q-pb-none">
							<div class="text-subtitle1">{{ previewImage.name }}</div>
							<q-space />
							<q-btn flat round dense icon="close" v-close-popup />
						</q-card-section>
						<q-card-section>
							<img :src="previewImage.url" :alt="previewImage.name" class="capture-preview-img" />
						</q-card-section>
					</q-card>
				</q-dialog>
			</template>

			<!-- Режим видео -->
			<template v-else-if="uploadMode === 'video'">
				<!-- Информация об ограничениях -->
				<div class="video-requirements q-mb-lg">
					<div class="requirements-header">
						<q-icon name="info" size="18px" color="primary" />
						<span class="requirements-title">Требования к видео</span>
					</div>
					<div class="requirements-list">
						<div class="requirement-item">
							<q-icon name="timer" size="16px" color="grey-7" />
							<span>Длительность: <strong>до 5 минут</strong></span>
						</div>
						<div class="requirement-item">
							<q-icon name="auto_fix_high" size="16px" color="grey-7" />
							<span>Объём файла не ограничиваем — перед AI большие ролики <strong>сжимаются автоматически</strong></span>
						</div>
						<div class="requirement-item">
							<q-icon name="slow_motion_video" size="16px" color="grey-7" />
							<span>Интервал между действиями: <strong>2-3 сек</strong></span>
						</div>
						<div class="requirement-item">
							<q-icon name="videocam" size="16px" color="grey-7" />
							<span>Формат: <strong>mp4, webm, avi</strong></span>
						</div>
					</div>
				</div>
				
				<div
					v-if="!videoFile"
					class="dropzone-video"
					@click="triggerVideoInput"
					@dragover.prevent
					@drop.prevent="onVideoDrop"
					@dragenter.prevent
					@dragleave.prevent
				>
					<q-icon name="smart_display" size="64px" color="primary" class="q-mb-sm" />
					<span class="text-body1 text-grey-8 text-weight-medium">Выберите видео</span>
					<span class="text-caption text-grey-5 q-mt-xs">mp4, webm, avi — или перетащите сюда</span>
					<input
						ref="videoInputRef"
						type="file"
						accept="video/*"
						class="hidden"
						@change="onVideoSelected"
					/>
				</div>
				<template v-else>
					<div class="video-preview-card q-mb-md">
						<div class="video-preview-icon">
							<q-icon name="smart_display" size="32px" color="primary" />
						</div>
						<div class="video-preview-info">
							<span class="video-preview-name">{{ videoFile.name }}</span>
							<span class="video-preview-size">{{ formatFileSize(videoFile.size) }}</span>
						</div>
						<q-btn flat round dense icon="close" size="sm" color="grey-6" @click="clearVideo">
							<q-tooltip>Удалить</q-tooltip>
						</q-btn>
					</div>
					<q-btn
						unelevated
						no-caps
						rounded
						color="primary"
						icon="check"
						label="Создать шаги из видео"
						size="lg"
						:loading="loading"
						:disable="loading"
						class="btn-create-steps btn-create-steps--primary btn-create-steps--lg"
						@click="uploadVideo"
					/>
				</template>
			</template>

			<!-- Режим PDF -->
			<template v-else-if="uploadMode === 'pdf'">
				<div class="video-requirements q-mb-lg">
					<div class="requirements-header">
						<q-icon name="picture_as_pdf" size="18px" color="primary" />
						<span class="requirements-title">Разбор инструкции</span>
					</div>
					<p class="text-caption text-grey-7 q-mb-none">
						Загрузите PDF-файл. AI проанализирует каждую страницу, найдет скриншоты и автоматически создаст шаги с описанием и областями для нажатия.
					</p>
				</div>
				
				<div
					v-if="!pdfFile"
					class="dropzone-video"
					@click="triggerPdfInput"
					@dragover.prevent
					@drop.prevent="onPdfDrop"
					@dragenter.prevent
					@dragleave.prevent
				>
					<q-icon name="picture_as_pdf" size="64px" color="primary" class="q-mb-sm" />
					<span class="text-body1 text-grey-8 text-weight-medium">Выберите PDF</span>
					<span class="text-caption text-grey-5 q-mt-xs">Перетащите файл инструкции сюда</span>
					<input
						ref="pdfInputRef"
						type="file"
						accept=".pdf"
						class="hidden"
						@change="onPdfSelected"
					/>
				</div>
				<template v-else>
					<div class="video-preview-card q-mb-md">
						<div class="video-preview-icon">
							<q-icon name="picture_as_pdf" size="32px" color="primary" />
						</div>
						<div class="video-preview-info">
							<span class="video-preview-name">{{ pdfFile.name }}</span>
							<span class="video-preview-size">{{ formatFileSize(pdfFile.size) }}</span>
						</div>
						<q-btn flat round dense icon="close" size="sm" color="grey-6" @click="clearPdf">
							<q-tooltip>Удалить</q-tooltip>
						</q-btn>
					</div>
					<q-btn
						unelevated
						no-caps
						rounded
						color="primary"
						icon="auto_awesome"
						label="Создать шаги из PDF"
						size="lg"
						:loading="loading"
						:disable="loading"
						class="btn-create-steps btn-create-steps--primary btn-create-steps--lg"
						@click="uploadPdf"
					/>
				</template>
			</template>
		</div>
	</div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed, nextTick } from "vue";
import useDnd from "@composables/useDnd.js";
import { MetaTrainingApi, TrainingApi } from "@api";
import { useRoute, useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useTrainingData } from "@store/editTraining.js";
import { ensureNotificationsConnected } from "@store/notifications.js";
import {
	FormUploadPhoto,
	PhotoList
} from "@components/features/edit_page/uploader_photo";

const metaApi = new MetaTrainingApi();
const trainingApi = new TrainingApi();
const $q = useQuasar();
const store = useTrainingData();
const [images, addImage] = useDnd();
const route = useRoute();
const router = useRouter();
const loading = ref(false);
const uploadMode = ref("photos");
const autoDetect = ref(true);
const videoFile = ref(null);
const videoInputRef = ref(null);
const pdfFile = ref(null);
const pdfInputRef = ref(null);

const videoStream = ref(null);
const videoPlayerRef = ref(null);
const captureSurface = ref("monitor");
const activeCaptureLabel = ref("");
const captureGalleryRef = ref(null);
const highlightSnapshotId = ref(null);
const previewImage = ref(null);
const capturePipWindow = ref(null);

const previewOpen = computed({
	get: () => previewImage.value != null,
	set: (open) => {
		if (!open) previewImage.value = null;
	},
});

const supportsCapturePip = computed(
	() => typeof window !== "undefined" && "documentPictureInPicture" in window
);

const CAPTURE_SURFACE_OPTIONS = [
	{
		value: "monitor",
		label: "Монитор",
		desc: "Рекомендуется",
		icon: "monitor",
		hint: "Захватывает весь монитор — в кадре будут меню, диалоги и новые окна. В диалоге Chrome выберите «Экран» / «Screen 1».",
		startCaption: "Выберите экран (монитор) в системном диалоге",
	},
	{
		value: "window",
		label: "Окно",
		desc: "Одно окно",
		icon: "crop_square",
		hint: "Только выбранное окно. Всплывающие меню и новые окна приложения часто не видны — ограничение Windows и браузера, не приложения.",
		startCaption: "Выберите окно приложения в системном диалоге",
	},
	{
		value: "any",
		label: "Любой",
		desc: "Как в Chrome",
		icon: "tab_unselected",
		hint: "Стандартный выбор браузера: вкладка, окно или весь экран.",
		startCaption: "Выберите источник в системном диалоге",
	},
];

const activeCaptureHint = computed(
	() => CAPTURE_SURFACE_OPTIONS.find((o) => o.value === captureSurface.value)?.hint ?? ""
);

const captureStartCaption = computed(
	() => CAPTURE_SURFACE_OPTIONS.find((o) => o.value === captureSurface.value)?.startCaption ?? ""
);

function buildCaptureConstraints(surface) {
	const constraints = {
		video: {
			cursor: "always",
		},
		audio: false,
	};
	if (surface === "window") {
		constraints.video.displaySurface = "window";
	} else if (surface === "monitor") {
		constraints.video.displaySurface = "monitor";
	}
	return constraints;
}

function updateCaptureLabel(stream) {
	const track = stream?.getVideoTracks?.()[0];
	if (!track) {
		activeCaptureLabel.value = "";
		return;
	}
	const surface = track.getSettings?.().displaySurface;
	const labels = {
		monitor: "Монитор",
		window: "Окно",
		browser: "Вкладка",
		application: "Приложение",
	};
	activeCaptureLabel.value = labels[surface] || "Экран";
}

const handleGlobalKeydown = (e) => {
	if (uploadMode.value === "capture" && videoStream.value) {
		// Проверяем все возможные варианты кода клавиши пробел
		if (e.code === "Space" || e.key === " " || e.keyCode === 32) {
			// Игнорируем нажатия, если пользователь печатает в инпут
			const targetTag = e.target?.tagName?.toLowerCase();
			if (targetTag === "input" || targetTag === "textarea") return;
			
			e.preventDefault();
			takeSnapshot();
		}
	}
};

onMounted(() => {
	document.addEventListener("keydown", handleGlobalKeydown, { capture: true });
});

onUnmounted(() => {
	document.removeEventListener("keydown", handleGlobalKeydown, { capture: true });
	closeCapturePipDock();
});

watch(uploadMode, (newVal) => {
	if (newVal !== "video") videoFile.value = null;
	if (newVal !== "pdf") pdfFile.value = null;
	if (newVal !== "photos" && images.value.length > 0 && newVal !== "capture") images.value = [];
	if (newVal !== "capture") stopCaptureStream();
});

const startCapture = async () => {
	try {
		const stream = await navigator.mediaDevices.getDisplayMedia(
			buildCaptureConstraints(captureSurface.value)
		);
		videoStream.value = stream;
		updateCaptureLabel(stream);

		const track = stream.getVideoTracks()[0];
		track.onended = () => {
			finishCapture();
		};

		setTimeout(() => {
			if (videoPlayerRef.value) {
				videoPlayerRef.value.srcObject = stream;
			}
		}, 100);

		if (captureSurface.value === "window") {
			$q.notify({
				message: "Захват окна",
				caption: "Если меню или диалог не видны — завершите и переключитесь на режим «Монитор».",
				type: "info",
				position: "top-right",
				timeout: 7000,
			});
		}
	} catch (error) {
		console.error("Ошибка при захвате экрана:", error);
		$q.notify({
			message: "Не удалось запустить захват экрана",
			caption: "Возможно, вы отменили выбор или у приложения нет прав",
			type: "negative",
			position: "top",
		});
	}
};

const restartCapture = async () => {
	closeCapturePipDock();
	if (videoStream.value) {
		videoStream.value.getTracks().forEach((track) => track.stop());
		videoStream.value = null;
		activeCaptureLabel.value = "";
	}
	await startCapture();
};

const closeCapturePipDock = () => {
	const pip = capturePipWindow.value;
	if (pip && !pip.closed) {
		pip.close();
	}
	capturePipWindow.value = null;
};

const updatePipShotCount = () => {
	const pip = capturePipWindow.value;
	if (!pip || pip.closed) return;
	const counter = pip.document.getElementById("pip-count");
	if (counter) counter.textContent = String(images.value.length);
};

const openCapturePipDock = async () => {
	if (!supportsCapturePip.value) {
		$q.notify({
			message: "Плавающая панель недоступна",
			caption: "Нужен Chrome или Edge. Или нажмите «Снимок» после Alt+Tab в браузер.",
			type: "warning",
			position: "top",
		});
		return;
	}
	if (capturePipWindow.value && !capturePipWindow.value.closed) {
		capturePipWindow.value.focus();
		return;
	}
	try {
		const pip = await window.documentPictureInPicture.requestWindow({
			width: 248,
			height: 168,
		});
		capturePipWindow.value = pip;
		const doc = pip.document;
		doc.body.style.margin = "0";
		doc.body.style.fontFamily = "system-ui, -apple-system, sans-serif";
		doc.body.style.background = "#1a1a2e";
		doc.body.style.color = "#fff";
		doc.body.innerHTML = `
			<div style="padding:14px;text-align:center;box-sizing:border-box">
				<div style="font-size:11px;line-height:1.4;opacity:0.85;margin-bottom:12px">
					Окно поверх программ — нажмите для снимка
				</div>
				<button id="pip-snap" type="button" style="
					width:100%;padding:14px 12px;border:none;border-radius:12px;
					background:#5064f7;color:#fff;font-size:15px;font-weight:600;cursor:pointer
				">Снимок (<span id="pip-count">${images.value.length}</span>)</button>
			</div>
		`;
		doc.getElementById("pip-snap").addEventListener("click", () => takeSnapshot());
		pip.addEventListener("pagehide", () => {
			capturePipWindow.value = null;
		});
	} catch (error) {
		if (error?.name !== "NotAllowedError") {
			console.error(error);
		}
	}
};

const stopCaptureStream = () => {
	closeCapturePipDock();
	if (videoStream.value) {
		videoStream.value.getTracks().forEach((track) => track.stop());
		videoStream.value = null;
	}
	activeCaptureLabel.value = "";
};

const finishCapture = () => {
	stopCaptureStream();
	if (uploadMode.value === "capture") {
		uploadMode.value = "photos";
	}
};

const stopCapture = () => {
	finishCapture();
};

const deleteCaptureShot = (id) => {
	const removed = images.value.find((img) => img.id === id);
	if (removed?.url) URL.revokeObjectURL(removed.url);
	images.value = images.value.filter((img) => img.id !== id);
	if (previewImage.value?.id === id) previewImage.value = null;
	updatePipShotCount();
};

const takeSnapshot = () => {
	const video = videoPlayerRef.value;
	if (!video || !video.videoWidth) return;

	const canvas = document.createElement("canvas");
	canvas.width = video.videoWidth;
	canvas.height = video.videoHeight;
	const ctx = canvas.getContext("2d");
	ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

	canvas.toBlob((blob) => {
		if (!blob) return;
		const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
		const file = new File([blob], `screenshot_${timestamp}.png`, { type: "image/png" });
		const newImage = {
			id: Date.now(),
			name: file.name,
			url: URL.createObjectURL(file),
			size: file.size,
			originalFile: file,
		};
		images.value = [...images.value, newImage];
		highlightSnapshotId.value = newImage.id;
		updatePipShotCount();

		nextTick(() => {
			const el = captureGalleryRef.value?.querySelector(
				`[data-shot-id="${newImage.id}"]`
			);
			el?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
		});

		setTimeout(() => {
			if (highlightSnapshotId.value === newImage.id) {
				highlightSnapshotId.value = null;
			}
		}, 1400);
	}, "image/png", 1.0);
};

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

const onVideoDrop = (event) => {
	const file = event.dataTransfer?.files?.[0];
	if (file && file.type.startsWith("video/")) {
		videoFile.value = file;
	}
};

const clearVideo = () => {
	videoFile.value = null;
	if (videoInputRef.value) videoInputRef.value.value = "";
};

const triggerPdfInput = () => pdfInputRef.value?.click();

const onPdfSelected = (event) => {
	const file = event.target.files?.[0];
	if (file) pdfFile.value = file;
	event.target.value = "";
};

const onPdfDrop = (event) => {
	const file = event.dataTransfer?.files?.[0];
	if (file && file.type === "application/pdf") {
		pdfFile.value = file;
	}
};

const clearPdf = () => {
	pdfFile.value = null;
	if (pdfInputRef.value) pdfInputRef.value.value = "";
};

const downloadPhotos = (event) => {
	let files = [...event.target.files];
	images.value = files.map((item, index) => ({
		id: index,
		name: item.name,
		url: URL.createObjectURL(item),
		size: item.size,
		originalFile: item,
	}));
};

const addMorePhotos = () => {
	const input = document.createElement("input");
	input.type = "file";
	input.multiple = true;
	input.accept = "image/*";
	input.onchange = (event) => {
		const files = event.target.files;
		if (!files || files.length === 0) return;
		const newImages = Array.from(files).map((file, i) => ({
			id: Date.now() + i,
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

const uploadImages = async () => {
	loading.value = true;
	try {
		const formData = new FormData();
		images.value.forEach((el) => {
			formData.append("files", el.originalFile);
		});
		await metaApi.uploadImages(route.params.uuid, formData, autoDetect.value);

		const { data } = await trainingApi.getTrainingByUuid(route.params.uuid);
		store.setTrainingData(data);

		images.value = [];

		$q.notify({
			message: "Шаги успешно созданы",
			type: "positive",
			position: "bottom-right",
			icon: "check_circle",
		});
	} catch {
		$q.notify({
			message: "Ошибка загрузки изображений",
			type: "negative",
			position: "top",
		});
	} finally {
		loading.value = false;
	}
};

const uploadVideo = async () => {
	if (!videoFile.value) return;
	loading.value = true;
	try {
		const formData = new FormData();
		formData.append("file", videoFile.value);
		const { data } = await metaApi.uploadVideo(route.params.uuid, formData);

		ensureNotificationsConnected().registerTask({
			...data,
			original_filename: videoFile.value.name,
			message: "Видео принято — создаём шаги тренинга",
		});
		void ensureNotificationsConnected().prepareSystemNotifications();

		clearVideo();

		$q.notify({
			message: "Видео загружено и отправлено на обработку",
			caption: "Разрешите уведомления Windows — сообщим, когда тренинг будет готов, даже если браузер свёрнут.",
			type: "info",
			position: "top-right",
			icon: "hourglass_top",
			timeout: 6000,
			color: "primary",
			classes: "beautiful-notify",
		});

		router.push("/personal/training");
	} catch (error) {
		console.error(error);
		$q.notify({
			message: "Ошибка загрузки видео",
			type: "negative",
			position: "top",
		});
	} finally {
		loading.value = false;
	}
};

const uploadPdf = async () => {
	if (!pdfFile.value) return;
	loading.value = true;
	try {
		const response = await trainingApi.uploadPdf(route.params.uuid, pdfFile.value);
		const data = response.data;

		ensureNotificationsConnected().registerTask({
			id: data.task_id,
			status: "pending",
			progress: 0,
			original_filename: pdfFile.value.name,
			message: "PDF принят — создаём шаги тренинга",
		});
		void ensureNotificationsConnected().prepareSystemNotifications();

		clearPdf();

		$q.notify({
			message: "PDF загружен и отправлен на обработку",
			caption: "Разрешите уведомления Windows — сообщим, когда тренинг будет готов, даже если браузер свёрнут.",
			type: "info",
			position: "top-right",
			icon: "hourglass_top",
			timeout: 6000,
			color: "primary",
			classes: "beautiful-notify",
		});

		router.push("/personal/training");
	} catch (err) {
		console.error("PDF Processing Error:", err);
		$q.notify({
			message: "Ошибка обработки PDF",
			caption: err.response?.data?.detail || "Проверьте формат файла и настройки AI",
			type: "negative",
			position: "top",
		});
	} finally {
		loading.value = false;
	}
};
</script>

<style scoped>
.upload-container {
	padding: 48px 20px;
	min-height: 100%;
	width: 100%;
	box-sizing: border-box;
}

.upload-container--photos-filled {
	padding: 24px 16px 20px;
	align-items: stretch;
}

.upload-container--photos-filled .upload-card {
	max-width: 680px;
	margin: 0 auto;
}

.upload-card {
	text-align: center;
	max-width: 600px;
	width: 100%;
}

.upload-icon-wrap {
	width: 88px;
	height: 88px;
	border-radius: 50%;
	background: rgba(80, 100, 247, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
}

/* ——— Переключатель режима ——— */
.mode-toggle {
	display: flex;
	gap: 12px;
}

.mode-card {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 4px;
	padding: 16px 28px;
	border-radius: 14px;
	border: 2px solid rgba(0, 0, 0, 0.08);
	background: #fff;
	cursor: pointer;
	transition: all 0.25s ease;
	min-width: 150px;
	color: #9e9e9e;
}

.mode-card:hover {
	border-color: rgba(80, 100, 247, 0.3);
	background: rgba(80, 100, 247, 0.03);
}

.mode-card--active {
	border-color: #5064f7;
	background: rgba(80, 100, 247, 0.06);
	color: #5064f7;
	box-shadow: 0 2px 12px rgba(80, 100, 247, 0.15);
}

.mode-label {
	font-size: 14px;
	font-weight: 600;
	line-height: 1.3;
}

.mode-desc {
	font-size: 11px;
	opacity: 0.7;
}

/* ——— Drop-зоны ——— */
.dropzone-wrap {
	border-radius: 16px;
	overflow: hidden;
}

.dropzone-video {
	width: 340px;
	max-width: 100%;
	height: 200px;
	border-radius: 16px;
	border: 2px dashed rgba(89, 106, 246, 0.28);
	background: rgba(191, 197, 244, 0.12);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	cursor: pointer;
	transition: background-color 0.3s, border-color 0.3s;
}

.dropzone-video:hover {
	background: rgba(191, 197, 244, 0.22);
	border-color: rgba(89, 106, 246, 0.45);
}

/* ——— Требования к видео ——— */
.video-requirements {
	background: linear-gradient(135deg, rgba(80, 100, 247, 0.04) 0%, rgba(80, 100, 247, 0.01) 100%);
	border: 1px solid rgba(80, 100, 247, 0.12);
	border-radius: 14px;
	padding: 16px 20px;
	max-width: 480px;
	width: 100%;
}

.requirements-header {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 12px;
}

.requirements-title {
	font-size: 14px;
	font-weight: 600;
	color: #374151;
}

.requirements-list {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.requirement-item {
	display: flex;
	align-items: center;
	gap: 10px;
	font-size: 13px;
	color: #6b7280;
}

.requirement-item strong {
	color: #1f2937;
	font-weight: 600;
}

/* ——— Режим захвата экрана ——— */
.capture-setup {
	width: 100%;
	max-width: 520px;
	margin: 0 auto;
}

.capture-surface-grid {
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: 10px;
	width: 100%;
}

.capture-surface-card {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 4px;
	min-height: 88px;
	padding: 10px 8px;
	border-radius: 12px;
	border: 1px solid rgba(89, 106, 246, 0.18);
	background: #fff;
	color: #64748b;
	cursor: pointer;
	transition: border-color 0.2s, background 0.2s, color 0.2s, box-shadow 0.2s;
}

.capture-surface-card:hover {
	border-color: rgba(89, 106, 246, 0.35);
	background: rgba(191, 197, 244, 0.08);
}

.capture-surface-card--active {
	border-color: #5064f7;
	background: rgba(80, 100, 247, 0.08);
	color: #5064f7;
	box-shadow: 0 4px 14px rgba(80, 100, 247, 0.12);
}

.capture-surface-card__label {
	font-size: 13px;
	font-weight: 600;
	color: inherit;
}

.capture-surface-card__desc {
	font-size: 11px;
	opacity: 0.85;
}

.capture-surface-hint {
	max-width: 420px;
	line-height: 1.45;
}

.capture-active-banner {
	border: 1px solid rgba(80, 100, 247, 0.12);
}

.capture-start-card {
	width: 340px;
	max-width: 100%;
	height: 200px;
	border-radius: 16px;
	border: 2px dashed rgba(89, 106, 246, 0.28);
	background: rgba(191, 197, 244, 0.12);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	cursor: pointer;
	transition: background-color 0.3s, border-color 0.3s;
	text-align: center;
	padding: 0 20px;
}
.capture-start-card:hover {
	background: rgba(191, 197, 244, 0.22);
	border-color: rgba(89, 106, 246, 0.45);
}

.capture-container {
	width: 100%;
	max-width: 520px;
}

.video-wrapper {
	width: 100%;
	aspect-ratio: 16/9;
	border-radius: 14px;
	overflow: hidden;
	background: #111;
	box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
	border: 2px solid rgba(80, 100, 247, 0.1);
}

.capture-video {
	width: 100%;
	height: 100%;
	object-fit: contain;
}

.capture-actions {
	width: 100%;
}

.capture-keyboard-hint {
	max-width: 420px;
	line-height: 1.45;
}

.capture-gallery__header {
	padding: 0 2px;
}

.capture-gallery__strip {
	display: flex;
	gap: 10px;
	overflow-x: auto;
	padding: 4px 2px 8px;
	scroll-snap-type: x mandatory;
}

.capture-gallery__item {
	position: relative;
	flex: 0 0 auto;
	width: 112px;
	height: 72px;
	border-radius: 10px;
	overflow: hidden;
	cursor: pointer;
	border: 2px solid rgba(80, 100, 247, 0.15);
	scroll-snap-align: center;
	transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
}

.capture-gallery__item img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	display: block;
}

.capture-gallery__item--new {
	border-color: #5064f7;
	box-shadow: 0 0 0 3px rgba(80, 100, 247, 0.25);
	transform: scale(1.03);
}

.capture-gallery__badge {
	position: absolute;
	left: 6px;
	bottom: 6px;
	min-width: 20px;
	height: 20px;
	padding: 0 5px;
	border-radius: 999px;
	background: rgba(15, 23, 42, 0.72);
	color: #fff;
	font-size: 11px;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
}

.capture-gallery__delete {
	position: absolute;
	top: 2px;
	right: 2px;
	background: rgba(15, 23, 42, 0.55) !important;
}

.capture-preview-card {
	max-width: min(92vw, 920px);
}

.capture-preview-img {
	display: block;
	max-width: 100%;
	max-height: 75vh;
	margin: 0 auto;
	border-radius: 8px;
}

/* ——— Превью фото ——— */
.photos-preview-area {
	width: 100%;
	max-width: 640px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.photos-preview-scroll {
	max-height: min(52vh, 460px);
	overflow-y: auto;
	overflow-x: hidden;
	padding: 10px 12px;
	border: 1px solid rgba(0, 0, 0, 0.07);
	border-radius: 12px;
	background: rgba(255, 255, 255, 0.72);
	scrollbar-gutter: stable;
}

.photos-preview-scroll::-webkit-scrollbar {
	width: 8px;
}

.photos-preview-scroll::-webkit-scrollbar-thumb {
	background: rgba(80, 100, 247, 0.28);
	border-radius: 999px;
}

.photos-preview-scroll::-webkit-scrollbar-track {
	background: rgba(0, 0, 0, 0.04);
	border-radius: 999px;
}

.photos-preview-scroll :deep(.photo-grid) {
	grid-template-columns: repeat(auto-fill, minmax(118px, 1fr));
	gap: 10px;
}

.photos-preview-scroll :deep(.photo-thumb) {
	height: 84px;
}

.photos-actions {
	position: sticky;
	bottom: 0;
	z-index: 2;
	flex-shrink: 0;
	padding: 8px 0 4px;
	background: linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, #fff 28%);
}

/* ——— Превью видео ——— */
.video-preview-card {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 14px 18px;
	background: rgba(80, 100, 247, 0.06);
	border: 1px solid rgba(80, 100, 247, 0.15);
	border-radius: 12px;
	min-width: 300px;
	max-width: 420px;
}

.video-preview-icon {
	width: 48px;
	height: 48px;
	border-radius: 10px;
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
	text-align: left;
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
	margin-top: 2px;
}

/* ——— Кнопки создания шагов ——— */
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
.btn-create-steps--primary {
	padding: 12px 24px;
}
.btn-create-steps--lg {
	padding: 14px 28px;
	font-size: 15px;
}
</style>
