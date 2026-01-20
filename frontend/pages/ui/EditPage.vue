<template>
	<base-loader size="100px" v-model="loadingStatus" />
	<template v-if="!loadingStatus">
		<group-steps v-if="store.steps"/>
		<step-title />
		<div v-if="store.selectedStep?.image_url">
			<tool-bar @select-event="flowComponent?.createNode"/>
			<vue-flow-component ref="flowComponent"  />
		</div>
	</template>
	<upload-photo
		@upload-photo="getTrainingData"
		class="absolute-center"
		v-if="store.selectedStep === null"
	/>
</template>

<script setup>
import VueFlowComponent from "@components/for_pages/EditPage/VueFlowComponent.vue";
import { UploadPhoto } from "@components/for_pages/EditPage/UploaderPhoto";
import { GroupSteps } from "@components/for_pages/EditPage/DropDownListSteps";
import { TrainingApi } from "@api";
import { useRoute } from "vue-router";
import { onMounted, ref, useTemplateRef } from "vue";
import { useTrainingData } from "@store/editTraining.js";
import StepTitle from "@components/for_pages/EditPage/StepTitle.vue";
import { BaseLoader } from "@components/base_components/index.js";
import ToolBar from "@components/for_pages/EditPage/ToolBar.vue";

const trainingApi = new TrainingApi();
const route = useRoute();
const store = useTrainingData();

const flowComponent = useTemplateRef('flowComponent');

const loadingStatus = ref(true);

async function getTrainingData() {
	try {
		loadingStatus.value = true;
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
