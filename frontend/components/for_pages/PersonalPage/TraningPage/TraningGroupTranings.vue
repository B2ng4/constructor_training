<template>
	<div class="row q-gutter-md q-ma-xl">
		<q-card
			class="my-card"
			flat
			bordered
			v-for="training in trainings"
			:key="training.id"
			@mouseover="training.hiddenStatus = false"
			@mouseleave="training.hiddenStatus = true"
		>
			<q-card-section>

				<div class="fixed-center column q-gutter-xs">
					<a :href="`/training/edit/${training.uuid}`">
						<q-btn
							class="button-edit"
							:class="{ hidden: training.hiddenStatus }"
							color="secondary"
							size="14px"
							round
							icon="edit"
						/>
					</a>
					<q-btn
						class="button-edit"
						:class="{ hidden: training.hiddenStatus }"
						color="negative"
						size="14px"
						round
						icon="delete"
						@click="deleteTraining(training.uuid)"
					/>
				</div>
				<div class="text-overline text-orange-9">
  			{{ new Date(training.created_at).toLocaleString('ru-RU', { year: 'numeric',
					month: 'long',
					day: 'numeric',
					hour: '2-digit',
					minute: '2-digit' })}}
				</div>
				<div class="text-h5 q-mt-sm q-mb-xs">{{ training.title }}</div>
				<div class="text-caption text-grey">
					{{ training.description }}
				</div>
			</q-card-section>
		</q-card>
	</div>
</template>

<script>
import { computed } from 'vue';
import { useTrainingStore } from "../../../../store/trainingStore";
import axios from "axios";

export default {
	setup() {
		const store = useTrainingStore();
		return {
			trainings: computed(() => store.getTrainings),
			store,
		};
	},
	methods: {
		async deleteTraining(uuid) {
			try {
				await axios.delete(`${__BASE__URL__}/training/${uuid}`);
				this.store.deleteTraining(uuid); // Удаляем из хранилища
			} catch (error) {
				console.error("Ошибка при удалении:", error);
			}
		},
	},
	async mounted() {
		await this.store.getAllTrainigs();
	},
};
</script>

<style scoped>
.my-card {
	width: 100%;
	max-width: 350px;
	word-break: break-all;
	border-radius: 25px;
}

.my-card:hover {
	background-color: rgba(0, 0, 0, 0.4);
	transition: all 0.1s ease-out;
	transform: scale(1.02);
}

.my-card:hover .text-overline,
.my-card:hover .text-h5,
.my-card:hover .text-caption {
	color: rgba(0, 0, 0, 0.10) !important;
}

.button-edit {
	cursor: pointer;
}
</style>