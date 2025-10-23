<template>
	<div v-if="trainings.length > 0" class="row q-gutter-md q-ma-xl">
		<q-spinner v-if="status"></q-spinner>
		<q-card
			class="my-card shadow-2"
			bordered
			v-for="training in trainings"
			:key="training.id"
		>
			<q-card-section>
				<div class="column">
					<p style="font-weight: 700; font-size: 15px;" class="q-my-xs text-bold">{{ training.title }}</p>
					<p class="text-grey-8">{{ training.level?.label ?? "Уровень" }}</p>
				</div>
				<div class="q-gutter-xs">
					<q-badge class="badge-tags" v-for="tag in training.tags">{{ tag.label }}</q-badge>
				</div>
				<!--Статус публикации и кнопка шестеренка-->
				<div class="row content-center q-mt-md">
					<div>
						<q-badge v-if="training.publish !== false" class="custom-badge rounden-4" align="middle">
							Опубликовано
						</q-badge>
						<p class="text-grey-8 q-mb-none" v-else>Черновик</p>
					</div>
					<div class="q-ml-auto">
						<q-btn-dropdown text-color="grey" color="white" icon="settings">
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

const trainings = ref([]);
const api = new TrainingApi();
const status = ref(true);

onMounted(async () => {
	try {
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