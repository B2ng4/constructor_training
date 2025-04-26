import { defineStore } from 'pinia'

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
		setTrainings(newTrainings) {
			this.trainings = newTrainings;
		},
		addTraining(training) {
			this.trainings.push(training);
		}
	}
})