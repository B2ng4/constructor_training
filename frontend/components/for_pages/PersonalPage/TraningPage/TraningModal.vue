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
				<q-input color="secondary" filled v-model="dataTraining.title" label="Название" />
				<q-input
					v-model="dataTraining.description"
					filled
					class="q-mt-md"
					label="Описание"
					type="textarea"
					color="secondary"
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
					color="secondary"
					label="Теги"
				/>
				<div class="q-mt-md row q-gutter-xs no-wrap">
					<q-input
						v-model="dataTraining.duration_minutes"
						type="number"
						label="Количество недель"
						class="col"
						color="secondary"
						filled/>
					<q-select
						v-model="dataTraining.level_id"
						label="Уровень подготовки"
						class="col"
						color="secondary"
						emit-value
						map-options
						filled
						:options="levelList"/>
				</div>
			</q-card-section>
			<q-card-actions align="right" class="row justify-center">
				<q-btn flat class="fit" label="Создать" color="secondary" @click="createTraining" />
			</q-card-actions>
		</q-card>
	</q-dialog>

	<!-- Кнопка создания -->
	<div class="row q-gutter-sm items-center">
		<q-btn
			color="secondary"
			text-color="white"
			label="Создать"
			@click="openModal"
		/>
		<q-input dense color="secondary" filled v-model="text" label="Поиск" />
	</div>
</template>

<script setup>
import { ref } from "vue";
import { TrainingApi } from "@api/TrainingApi.js";
import { MetaTrainingApi } from "@api/MetaTrainingApi.js";

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

const showModal = ref(false);

async function createTraining() {
	return await trainingApi.createTraining(dataTraining.value);
}

async function openModal() {
	showModal.value = !showModal.value;
	getMetaData();
}

async function getMetaData() {
	try {
		let tags = await metaApi.getTags();
		listTags.value = tags.data;

		let levels = await metaApi.getLevels();
		levelList.value = levels.data;
	} catch {
		alert(0)
	}
}
</script>