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

	function addStep(newStep) {
		steps.value.push(newStep);
	}

	return { trainingData, setTrainingData, setSteps, steps, addStep };
});
