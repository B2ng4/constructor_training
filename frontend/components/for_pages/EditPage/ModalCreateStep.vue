<template>
	<q-dialog v-model="value" persistent>
		<q-card style="min-width: 350px">
			<q-card-section>
				<div class="text-h6">Создать шаг</div>
			</q-card-section>
			<q-card-section class="flex column q-gutter-md">
				<q-input dense v-model="step.name" autofocus />
				<q-toggle
					class="q-ml-none"
					label="Вложенные шаги"
					size="lg"
					v-model="childSteps.status"
				/>
				<div class="flex column" v-if="childSteps.status">
					<q-input v-for="el in childSteps.steps" v-model="el.meta.name" :key="el.step_number" />
					<q-btn
						class="q-mt-lg"
						flat
						label="Добавить"
						@click="
							childSteps.steps.push({
								step_number: childSteps.steps.length + 1,
								meta: { name: 'Шаг без названия' },
							})
						"
					/>
				</div>
			</q-card-section>
			<q-card-actions align="right" class="text-primary">
				<q-btn flat label="Отмена" v-close-popup />
				<q-btn flat label="Создать" @click="addStep" />
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { useRoute } from "vue-router";
import { TrainingApi } from "@api/api/TrainingApi.js";
import { ref } from "vue";
import { useTrainingData } from "@store/editTraining.js";

const value = defineModel();
const route = useRoute();
const api = new TrainingApi();
const store = useTrainingData();

const props = defineProps({
	stepCount: Number,
});

const step = ref({ name: "Шаг без названия" });
const childSteps = ref({
	steps: [],
	status: false,
});

async function addStep() {
	try {
		let payload = {
			step_number: props.stepCount + 1,
			meta: step.value,
			steps: childSteps.value.steps,
		};
		const response = await api.addStep(route.params.uuid, payload);
		value.value = false;
		store.addStep(response.data);
	} catch (e) {
		console.error(e);
		alert("Ошибка добавления нового шага");
	}
}
</script>
