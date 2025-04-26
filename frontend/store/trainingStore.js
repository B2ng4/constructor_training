import { defineStore } from 'pinia'
import axios from 'axios'

export const useTrainingStore = defineStore('useTrainingStore', {
	state: () => {
		return {
			trainings: [],
		}
	},
	getters: {
			getTrainings: (state) => state.trainings,
	},
	actions: {
		async getAllTrainigs() {
			try {
				const response = await axios.get(`${__BASE__URL__}/training/my_trainings/`, {
					headers: {
						Authorization: `Bearer ${localStorage.getItem("tokenAuth")}`,
					},
				});
				response.data.forEach((element) => {
					//статус для скрытия кнопок
					element.hiddenStatus = true;
				})
				this.trainings = response.data;
			} catch (error) {
				this.trainings = error.data;
			}
		},
		deleteTraining(trainingId) {
			this.trainings.splice(this.trainings.indexOf(trainingId), 1);
		}
	}
})