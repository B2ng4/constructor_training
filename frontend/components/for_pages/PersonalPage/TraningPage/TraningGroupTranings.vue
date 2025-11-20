<template>
	<div v-if="trainings.length > 0" class="row q-gutter-md q-ma-xl">
		<q-spinner v-if="status"></q-spinner>
		<q-card
			@click="editTraining(training.uuid)"
			class="my-card shadow-2"
			bordered
			v-for="training in trainings"
			:key="training.id"
		>
			<q-card-section>
				<div class="column">
					<div class="row no-wrap items-center">
						<svg viewBox="0 0 64 64" width="64" height="64" aria-hidden="true">
							<defs>
								<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="rgb(244, 224, 255)" stop-opacity="0.95"></stop><stop offset="1" stop-color="#ffffff" stop-opacity="0.6"></stop></linearGradient>
							</defs>
							<rect x="4" y="4" width="56" height="56" rx="10" fill="url(#g)"></rect>
							<g transform="translate(12,12)" fill="rgba(255,255,255,0.92)">
								<path d="M8 0 L20 0 L8 24 L0 12 Z"></path>
							</g>
						</svg>
						<p style="font-weight: 600; font-size: 15px" class="q-ml-md">{{ training.title }}</p>
					</div>
					<p class="text-grey-8">{{ training.level?.label ?? "Уровень" }}</p>
				</div>
				<div class="q-gutter-xs">
					<q-badge class="badge-tags" v-for="tag in training.tags">{{ tag.label }}</q-badge>
				</div>
				<!--Статус публикации и кнопка шестеренка-->
				<div class="row items-center q-mt-md">
					<div>
						<q-badge v-if="training.publish !== false" class="custom-badge rounden-4" align="middle">
							Опубликовано
						</q-badge>
						<p class="text-grey-8 q-mb-none" v-else>Черновик</p>
					</div>
					<div class="q-ml-auto">
						<q-btn-dropdown @click.stop text-color="grey" color="white" flat dropdown-icon="settings">
							<q-list>
								<q-item clickable @click="editTraining(training.uuid)">
									<q-item-section>
										<q-item-label>Редактировать</q-item-label>
									</q-item-section>
								</q-item>
								<q-item clickable @click="publishTraining(training)">
									<q-item-section>
										<q-item-label>{{training.publish === true ? 'Закрыть доступ' : 'Опубликовать'}}</q-item-label>
									</q-item-section>
								</q-item>
								<q-item clickable @click="deleteTraining(training.uuid)">
									<q-item-section>
										<q-item-label>Удалить</q-item-label>
									</q-item-section>
								</q-item>
							</q-list>
						</q-btn-dropdown>
					</div>
				</div>
			</q-card-section>
		</q-card>
	</div>
</template>

<script setup>
import { TrainingApi } from "@api/TrainingApi.js";
import { onMounted, ref } from "vue";
import { useRouter } from 'vue-router';

const router = useRouter();
const trainings = ref([]);
const api = new TrainingApi();
const status = ref(true);

async function getTrainings() {
	try {
		status.value = true;
		trainings.value = [];
		let response = await api.getTrainings();
		trainings.value = response.data;
	} catch (e) {
		this.$q.notify({
			message: "Ошибка получения списка тренингов",
			position: "top",
			type: "negative"
		});
	} finally {
		status.value = false;
	}
}

async function deleteTraining(uuid) {
	try {
		await api.deleteTraining(uuid);
		await getTrainings();
	} catch (e) {

	}
}

async function publishTraining(training) {
	try {
		await api.updateTraining(training.uuid, {publish: !training.publish});
		training.publish = !training.publish;
	} catch (e) {
	}
}

function editTraining(uuid) {
	const route = router.resolve(`/edit/${uuid}`);
	window.open(route.href, '_blank');
}

onMounted(() => {
	getTrainings();
});

</script>

<style scoped>
.my-card {
	width: 100%;
	max-width: 350px;
	border-radius: 10px;
	transition: box-shadow .14s ease, transform .14s ease;
}

.my-card:hover, .my-card:focus {
	transform: translateY(-6px);
	cursor: pointer;
}

.badge-tags {
	background: rgba(25, 118, 210, 0.06);
	border-radius: 999px;
	color: #1976d2;
	border: 1px solid rgba(25, 118, 210, 0.12);
	padding: 8px;
}

.rounden-4 {
	border-radius: 20px;
}

.custom-badge {
	background: rgba(16, 185, 129, 0.08);
	color: #10b981;
	border: 1px solid rgba(16, 185, 129, 0.14);
	padding: 8px;
}
</style>