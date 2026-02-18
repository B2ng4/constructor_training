<template>
	<div class="edit-page">
		<base-loader size="100px" v-model="loadingStatus" />

		<template v-if="!loadingStatus">
			<!-- Пустое состояние: нет шагов -->
			<div v-if="!storeSteps || storeSteps.length === 0" class="empty-state">
				<upload-photo />
			</div>

			<!-- Основной редактор -->
			<template v-else>
				<group-steps />
				<step-title />
				<step-hint />
				<ai-generated-banner />

				<div v-if="selectedStep?.image_url" class="edit-area">
					<!-- Подсказка -->
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
import StepHint from "@components/features/edit_page/StepHint.vue";
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

// Показать подсказку 2–4 сек, затем скрыть
watch(
	() => selectedStep.value?.image_url,
	(hasImage) => {
		if (hintAutoHideTimer) {
			clearTimeout(hintAutoHideTimer);
			hintAutoHideTimer = null;
		}
		if (hasImage && !store.selectedEvent) {
			hintHidden.value = false;
			const delay = 3000; // 3 секунды (в диапазоне 2–4 сек)
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
	height: 100%;
}

.empty-state {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 80vh;
}

.edit-area {
	position: relative;
	width: 100%;
	height: 100%;
}

.edit-hint {
	position: absolute;
	top: 16px;
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
</style>
