import { defineStore } from "pinia";
import { ref } from "vue";

export const useTrainingData = defineStore("city", () => {
	const trainingData = ref(null);
	const steps = ref(null);

	function setTrainingData(newTrainingData) {
		trainingData.value = newTrainingData;
		setSteps(newTrainingData.steps);
	}

	function setSteps(newSteps) {
		steps.value = newSteps;
	}

	return { trainingData, setTrainingData, setSteps, steps };
});
