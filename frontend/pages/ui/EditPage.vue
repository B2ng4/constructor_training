<template>
	<base-loader size="100px" v-model="loadingStatus" />
	<template v-if="!loadingStatus">
		<group-steps v-if="store.steps"/>
		<step-title />
		<div v-if="store.selectedStep?.image_url">
			<tool-bar />
			<vue-flow-component />
		</div>
	</template>
	<upload-photo
		class="absolute-center"
		v-if="store.steps === null"
	/>
</template>

<script setup>
import VueFlowComponent from "@components/features/edit_page/VueFlowComponent.vue";
import { UploadPhoto } from "@components/features/edit_page/uploader_photo";
import { GroupSteps } from "@components/features/edit_page/drop_down_list_steps";
import { TrainingApi } from "@api";
import { useRoute } from "vue-router";
import { nextTick, onMounted, ref } from "vue";
import { useTrainingData } from "@store/editTraining.js";
import StepTitle from "@components/features/edit_page/StepTitle.vue";
import { BaseLoader } from "@components/base_components/index.js";
import ToolBar from "@components/features/edit_page/tool_bar/ui/ToolBar.vue";

const trainingApi = new TrainingApi();
const route = useRoute();
const store = useTrainingData();

const loadingStatus = ref(true);

async function getTrainingData() {
	try {
		loadingStatus.value = true;
		await nextTick();
		store.setTrainingData((await trainingApi.getTrainingByUuid(route.params.uuid)).data);
	} catch {
		alert("Данные тренинга не найдены");
	} finally {
		loadingStatus.value = false;
	}
}

onMounted(() => {
	getTrainingData();
});
</script>
