<template>
	<!-- Модалка -->
	<q-dialog ref="dialog" v-model="showModal" persistent transition-show="scale" transition-hide="scale">
		<q-card style="width: 700px; max-width: 80vw;">
			<q-card-section class="row">
				<div class="text-h6">Создание тренинга</div>
				<q-space />
				<q-btn icon="close" flat round dense v-close-popup />
			</q-card-section>
			<q-card-section>
				<q-input color="primary" filled v-model="dataTraining.title" label="Название" />
				<q-input
					v-model="dataTraining.description"
					filled
					class="q-mt-md"
					label="Описание"
					type="textarea"
					color="primary"
				/>
				<q-select
					class="q-mt-md"
					filled
					v-model="dataTraining.tag_ids"
					multiple
					:options="listTags"
					use-chips
					emit-value
					map-options
					color="primary"
					label="Теги"
				/>
				<div class="q-mt-md row q-gutter-xs no-wrap">
					<q-input
						v-model="dataTraining.duration_minutes"
						type="number"
						label="Количество недель"
						class="col"
						color="primary"
						filled/>
					<q-select
						v-model="dataTraining.level_id"
						label="Уровень подготовки"
						class="col"
						color="primary"
						emit-value
						map-options
						filled
						:options="levelList"/>
				</div>
			</q-card-section>
			<q-card-actions align="right" class="row justify-center">
				<q-btn flat class="fit" label="Создать" color="primary" @click="createTraining" />
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { ref } from "vue";
import { TrainingApi } from "@api/api/TrainingApi.js";
import { MetaTrainingApi } from "@api/api/MetaTrainingApi.js";
import { trainingEvents } from "@utils/eventBus.js";

const metaApi = new MetaTrainingApi();
const listTags = ref([]);
const levelList = ref([]);

const trainingApi = new TrainingApi();
const dataTraining = ref({
	title: "",
	description: "",
	tag_ids: [],
	duration_minutes: [],
	level_id: [],
});

const showModal = defineModel();

async function createTraining() {
	try {
		await trainingApi.createTraining(dataTraining.value);
		await trainingEvents.created.trigger();
		showModal.value = false;
	} catch (e) {
		console.error(e);
	}
}

async function openModal() {
	showModal.value = !showModal.value;
	await getMetaData();
}

async function getMetaData() {
	try {
		listTags.value = (await metaApi.getTags()).data;
		levelList.value = (await metaApi.getLevels()).data;
	} catch {
		console.error('Ошибка получения метаданных');
	}
}

defineExpose(
	openModal
);
</script>