<template>
	<base-loader size="100px" v-model="loadingStatus" />
	<div v-if="!loadingStatus">
		<group-steps  />
		<step-title  />
		<div v-if="store.selectedStep?.image_url">
			<tool-bar @select-event="flowComponent?.createNode"/>
			<vue-flow-component ref="flowComponent"  />
		</div>
		<upload-photo
			@upload-photo="getTrainingData"
			class="absolute-center"
			v-else
		/>
	</div>
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
		let response = await trainingApi.getTrainingByUuid(route.params.uuid);
		store.setTrainingData(response.data);
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
