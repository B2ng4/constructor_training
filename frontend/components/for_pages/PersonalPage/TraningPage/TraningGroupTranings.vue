<template>
	<div class="row q-gutter-md q-ma-xl">
		<q-card
			class="my-card"
			flat
			bordered
			v-for="training in trainings"
			:key="training.id"
		>
			<q-card-section>
				<div class="text-overline text-orange-9">Какая-то надпись</div>
				<div class="text-h5 q-mt-sm q-mb-xs">{{ training.title }}</div>
				<div class="text-caption text-grey">
					{{ training.description }}
				</div>
			</q-card-section>
		</q-card>
	</div>
</template>

<script>
import axios from "axios";
import { useTrainingStore } from "../../../../store/trainingStore";

export default {
	data() {
		return {
			trainings: [],
		};
	},
	methods: {
		async getTrainings() {
			this.trainings = [];
			const store = useTrainingStore();
			axios
				.get(`${__BASE__URL__}/training/my_trainings/`, {
					headers: {
						Authorization: `Bearer ${localStorage.getItem("tokenAuth")}`,
					},
				})
				.then((response) => {
					response.data.forEach((element) => {
						this.trainings.push(element);
					});
					store.setTrainings(this.trainings)
				});
		},
	},
	mounted() {
		const store = useTrainingStore();
		if (store.getTrainings.length > 0) {
			this.trainings = store.getTrainings;
		}
		else {
			this.getTrainings();
		}
	},
};
</script>

<style scoped>
.my-card {
	width: 100%;
	max-width: 350px;
	word-break: break-all;
	border-radius: 5%;
}

.my-card:hover {
	background-color: rgba(0, 0, 0, 0.095);
	transition: all 0.1s ease-out;
	transform: scale(1.02);
	cursor: pointer;
}
</style>