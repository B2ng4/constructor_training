<template>
	<div class="edit-page">
		<q-btn
			flat
			no-caps
			rounded
			color="primary"
			icon="home"
			label="На главную"
			class="edit-page__home-btn"
			@click="goToTrainingList"
		/>

		<base-loader size="100px" v-model="loadingStatus" />

		<template v-if="!loadingStatus">
			<!-- Пустое состояние: нет шагов -->
			<div v-if="!storeSteps || storeSteps.length === 0" class="empty-state">
				<upload-photo />
			</div>

			<!-- Скрин слева, панель задания справа -->
			<template v-else>
				<div class="edit-split">
					<div class="edit-split__main">
						<div class="edit-overlays">
							<group-steps />
							<step-title />
						</div>

						<div v-if="selectedStep?.image_url" class="edit-area">
							<transition name="hint-fade">
								<div
									v-if="!store.selectedEvent && !hintHidden"
									class="edit-hint"
								>
									<q-icon name="touch_app" size="20px" class="q-mr-sm" />
									<span>Выберите действие в тулбаре и выделите область на скриншоте</span>
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

							<tool-bar />
							<vue-flow-component />
						</div>
					</div>

					<aside class="edit-split__aside">
						<step-task-editor />
						<AIGeneratedBanner />
					</aside>
				</div>
			</template>
		</template>
	</div>
</template>

<script setup>
import VueFlowComponent from "@components/features/edit_page/VueFlowComponent.vue";
import { UploadPhoto } from "@components/features/edit_page/uploader_photo";
import { GroupSteps } from "@components/features/edit_page/drop_down_list_steps";
import { TrainingApi } from "@api";
import { useRoute, useRouter } from "vue-router";
import { nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useTrainingData } from "@store/editTraining.js";
import StepTitle from "@components/features/edit_page/StepTitle.vue";
import StepTaskEditor from "@components/features/edit_page/StepTaskEditor.vue";
import AIGeneratedBanner from "@components/features/edit_page/AIGeneratedBanner.vue";
import { BaseLoader } from "@components/base_components/index.js";
import ToolBar from "@components/features/edit_page/tool_bar/ui/ToolBar.vue";
import { useQuasar } from "quasar";

const trainingApi = new TrainingApi();
const route = useRoute();
const router = useRouter();
const store = useTrainingData();
const $q = useQuasar();
const { steps: storeSteps, selectedStep } = storeToRefs(store);

const loadingStatus = ref(true);
const hintHidden = ref(false);
let hintAutoHideTimer = null;

function hideHint() {
	hintHidden.value = true;
}

function goToTrainingList() {
	router.push("/personal/training");
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

onMounted(() => {
	getTrainingData();
});
</script>

<style scoped>
.edit-page {
	position: relative;
	width: 100%;
	/* #app без height: 100% — задаём окно целиком, иначе холст Vue Flow с height 0 */
	height: 100vh;
	min-height: 100vh;
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.edit-page__home-btn {
	position: fixed;
	top: 12px;
	right: 12px;
	left: auto;
	z-index: 200;
	background: rgba(255, 255, 255, 0.95) !important;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.empty-state {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 80vh;
}

.edit-split {
	display: flex;
	flex-direction: row-reverse;
	flex: 1;
	min-height: 0;
	width: 100%;
	align-items: stretch;
	overflow: hidden;
}

.edit-split__main {
	position: relative;
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
	background: #fafbfc;
	border-right: 1px solid rgba(15, 23, 42, 0.08);
	overflow: hidden;
}

.edit-overlays {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	z-index: 40;
	pointer-events: none;
}

.edit-overlays > * {
	pointer-events: auto;
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
}

.edit-hint {
	position: absolute;
	bottom: 88px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 100;
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

.hint-fade-enter-active,
.hint-fade-leave-active {
	transition: opacity 0.3s ease, transform 0.3s ease;
}

.hint-fade-enter-from,
.hint-fade-leave-to {
	opacity: 0;
	transform: translateX(-50%) translateY(-8px);
}

@media (max-width: 900px) {
	.edit-split {
		flex-direction: column;
	}

	.edit-split__aside {
		width: 100%;
		max-height: min(45vh, 400px);
		border-right: none;
		border-top: 1px solid rgba(15, 23, 42, 0.08);
	}
}
</style>
