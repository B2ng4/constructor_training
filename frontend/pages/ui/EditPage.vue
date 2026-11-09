<template>
	<div class="edit-page">
		<BackgroundProcessingIndicator class="edit-page__processing-indicator" />

		<scenario-map-dialog v-model="scenarioMapOpen" />
		<editor-passage-preview v-model="previewOpen" />

		<base-loader size="100px" v-model="loadingStatus" />

		<template v-if="!loadingStatus">
			<!-- Пустое состояние: нет шагов -->
			<div v-if="!storeSteps || storeSteps.length === 0" class="empty-state">
				<upload-photo />
			</div>

			<!-- Панель задания слева, скрин справа -->
			<template v-else>
				<div class="edit-split premium-bg-container">
					<aside class="edit-split__aside glass-panel">
						<step-task-editor />
						<AIGeneratedBanner />
					</aside>

					<div class="edit-split__main">
						<edit-editor-header
							:show-crop="cropButtonVisible"
							@preview="previewOpen = true"
							@map="scenarioMapOpen = true"
							@crop="cropDialogOpen = true"
							@home="goToTrainingList"
							@duplicate="trainingEvents.duplicateStep.trigger()"
							@detect="detectStepElements"
						/>

						<transition name="step-fade" mode="out-in">
							<div :key="selectedStep?.id" class="edit-content-wrap">
								<div v-if="selectedStep?.image_url" class="edit-area">
									<transition name="hint-fade">
										<div
											v-if="!store.selectedEvent && !hintHidden"
											class="edit-hint"
										>
											<q-icon name="touch_app" size="20px" class="q-mr-sm" />
											<span>Выберите действие внизу и выделите область на скриншоте</span>
											<q-btn
												flat
												dense
												round
												size="sm"
												icon="close"
												color="white"
												class="q-ml-sm"
												@click="hideHint"
											/>
										</div>
									</transition>

									<vue-flow-component />
									<tool-bar />
								</div>
							</div>
						</transition>
					</div>
				</div>
			</template>
		</template>

		<screenshot-crop-dialog
			v-model="cropDialogOpen"
			:training-uuid="trainingUuidParam"
			:step-id="selectedStep?.id ?? null"
			@saved="onScreenshotSaved"
		/>
	</div>
</template>

<script setup>
import VueFlowComponent from "@components/features/edit_page/VueFlowComponent.vue";
import { UploadPhoto } from "@components/features/edit_page/uploader_photo";
import { TrainingApi, TrainingStepApi } from "@api";
import { useRoute, useRouter } from "vue-router";
import { nextTick, onMounted, onUnmounted, ref, watch, computed } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import StepTaskEditor from "@components/features/edit_page/StepTaskEditor.vue";
import AIGeneratedBanner from "@components/features/edit_page/AIGeneratedBanner.vue";
import { BaseLoader } from "@components/base_components/index.js";
import ToolBar from "@components/features/edit_page/tool_bar/ui/ToolBar.vue";
import ScreenshotCropDialog from "@components/features/edit_page/ScreenshotCropDialog.vue";
import { useQuasar } from "quasar";
import BackgroundProcessingIndicator from "@components/features/personal_page/header/BackgroundProcessingIndicator.vue";
import ScenarioMapDialog from "@components/features/edit_page/scenario_map/ScenarioMapDialog.vue";
import EditorPassagePreview from "@components/features/edit_page/EditorPassagePreview.vue";
import EditEditorHeader from "@components/features/edit_page/EditEditorHeader.vue";
import { useEditorKeyboard } from "@composables/useEditorKeyboard.js";
import { useEditorSaveStatus } from "@composables/useEditorSaveStatus.js";
import { trainingEvents } from "@utils/eventBus.js";
import { onBeforeRouteLeave } from "vue-router";

const trainingApi = new TrainingApi();
const trainingStepApi = new TrainingStepApi();
const route = useRoute();
const router = useRouter();
const store = useTrainingData();
const $q = useQuasar();
const { steps: storeSteps, selectedStep } = storeToRefs(store);

const loadingStatus = ref(true);
const scenarioMapOpen = ref(false);
const previewOpen = ref(false);
const { isDirty } = useEditorSaveStatus();

const trainingUuidParam = computed(() => {
	const u = route.params?.uuid;
	return u != null && u !== "" ? String(u) : "";
});

const cropButtonVisible = computed(
	() =>
		!loadingStatus.value &&
		Array.isArray(storeSteps.value) &&
		storeSteps.value.length > 0 &&
		!!selectedStep.value?.image_url
);

const cropDialogOpen = ref(false);

function onScreenshotSaved() {
	void nextTick();
}

const hintHidden = ref(false);
let hintAutoHideTimer = null;

function hideHint() {
	hintHidden.value = true;
}

function goToTrainingList() {
	router.push("/personal/training");
}

const detecting = ref(false);

async function detectStepElements() {
	const step = selectedStep.value;
	if (detecting.value || !step?.id || !trainingUuidParam.value) return;
	detecting.value = true;
	try {
		const { data } = await trainingStepApi.detectStepElements(
			trainingUuidParam.value,
			step.id
		);
		const detections = data?.meta?.ui_detections;
		if (Array.isArray(detections)) {
			step.meta = { ...(step.meta || {}), ui_detections: detections };
			const inList = store.steps?.find((s) => s.id === step.id);
			if (inList) inList.meta = JSON.parse(JSON.stringify(step.meta));
		}
		$q.notify({
			color: "positive",
			message: `Найдено элементов: ${detections?.length ?? 0}`,
			position: "bottom-right",
			timeout: 1800,
		});
	} catch {
		$q.notify({
			color: "negative",
			message: "Не удалось определить элементы",
			position: "top",
		});
	} finally {
		detecting.value = false;
	}
}

watch(
	() => selectedStep.value?.image_url,
	(hasImage) => {
		if (hintAutoHideTimer) {
			clearTimeout(hintAutoHideTimer);
			hintAutoHideTimer = null;
		}
		if (hasImage && !store.selectedEvent) {
			hintHidden.value = false;
			const delay = 3000;
			hintAutoHideTimer = setTimeout(() => {
				hintHidden.value = true;
				hintAutoHideTimer = null;
			}, delay);
		}
	},
	{ immediate: true }
);

onUnmounted(() => {
	if (hintAutoHideTimer) {
		clearTimeout(hintAutoHideTimer);
	}
});

async function getTrainingData() {
	try {
		loadingStatus.value = true;
		await nextTick();
		store.setTrainingData((await trainingApi.getTrainingByUuid(route.params.uuid)).data);
	} catch {
		$q.notify({
			color: "negative",
			message: "Тренинг не найден",
			position: "top",
			icon: "error",
		});
		router.push("/personal/training");
	} finally {
		loadingStatus.value = false;
	}
}

function onTrainingTaskUpdate(event) {
	const detail = event?.detail;
	if (!detail?.training_uuid) return;
	if (String(detail.training_uuid) !== String(route.params.uuid)) return;
	if (detail.status === "completed") {
		void getTrainingData();
	}
}

onMounted(() => {
	getTrainingData();
	window.addEventListener("training-task-update", onTrainingTaskUpdate);
	window.addEventListener("beforeunload", onBeforeUnload);
});

onUnmounted(() => {
	window.removeEventListener("training-task-update", onTrainingTaskUpdate);
	window.removeEventListener("beforeunload", onBeforeUnload);
});

function onBeforeUnload(event) {
	if (!isDirty.value) return;
	event.preventDefault();
	event.returnValue = "";
}

onBeforeRouteLeave((_to, _from, next) => {
	if (!isDirty.value) {
		next();
		return;
	}
	$q.dialog({
		title: "Есть несохранённые изменения",
		message: "Покинуть редактор? Несохранённые правки могут быть потеряны.",
		cancel: { label: "Остаться", flat: true },
		ok: { label: "Выйти", color: "negative", flat: true },
	}).onOk(() => next()).onCancel(() => next(false));
});

useEditorKeyboard({
	onPreviousStep: () => store.goToPreviousStep(),
	onNextStep: () => store.goToNextStep(),
	onSelectAction: (id) => trainingEvents.selectActionById.trigger(id),
	onClearArea: () => trainingEvents.clearCurrentArea.trigger(),
	onForceSave: () => trainingEvents.forceSave.trigger(),
	onTogglePreview: () => {
		if (!storeSteps.value?.length) return;
		previewOpen.value = !previewOpen.value;
	},
	onDuplicateStep: () => trainingEvents.duplicateStep.trigger(),
	onEscape: () => {
		previewOpen.value = false;
		scenarioMapOpen.value = false;
	},
});
</script>

<style scoped>
.edit-page {
	position: relative;
	width: 100%;
	height: 100vh;
	min-height: 100vh;
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.edit-page__processing-indicator {
	position: fixed;
	top: 12px;
	right: 12px;
	z-index: 201;
}

.edit-area {
	position: relative;
	z-index: 1;
	flex: 1;
	min-height: 0;
	width: 100%;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	padding-bottom: 88px;
}

.edit-hint {
	position: absolute;
	bottom: 96px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 11;
	display: flex;
	align-items: center;
	background: rgba(30, 30, 50, 0.8);
	backdrop-filter: blur(12px);
	-webkit-backdrop-filter: blur(12px);
	color: white;
	padding: 10px 16px;
	border-radius: 12px;
	font-size: 13px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
	white-space: nowrap;
}

.edit-split {
	display: flex;
	flex-direction: row;
	flex: 1;
	min-height: 0;
	width: 100%;
	align-items: stretch;
	overflow: hidden;
	background-color: transparent !important;
}

.edit-split__main {
	flex: 1;
	min-width: 0;
	min-height: 0;
	display: flex;
	flex-direction: column;
}

.edit-split__aside {
	width: min(440px, 40vw);
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	min-height: 0;
	z-index: 100;
	padding: 12px;
	gap: 12px;
	margin: 10px 0 10px 12px;
	border-radius: 16px;
	overflow: hidden;
}

.empty-state {
	flex: 1;
	min-height: 0;
	display: flex;
	align-items: flex-start;
	justify-content: center;
	overflow-x: hidden;
	overflow-y: auto;
	padding: 16px;
	-webkit-overflow-scrolling: touch;
}

.hint-fade-enter-active,
.hint-fade-leave-active {
	transition: opacity 0.3s ease, transform 0.3s ease;
}

.hint-fade-enter-from,
.hint-fade-leave-to {
	opacity: 0;
	transform: translateX(-50%) translateY(-8px);
}

.edit-content-wrap {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
	position: relative;
}

.step-fade-enter-active,
.step-fade-leave-active {
	transition: opacity 0.3s var(--anim-ease-out), transform 0.3s var(--anim-ease-out);
}

.step-fade-enter-from {
	opacity: 0;
	transform: perspective(1000px) rotateX(1deg) translateY(4px);
}

.step-fade-leave-to {
	opacity: 0;
	transform: perspective(1000px) rotateX(-1deg) translateY(-4px);
}

@media (max-width: 900px) {
	.edit-split {
		flex-direction: column;
	}

	.edit-split__main {
		order: -1;
	}

	.edit-split__aside {
		width: auto;
		max-height: min(45vh, 400px);
		margin: 0 12px 12px;
	}
}
</style>
