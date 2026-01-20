import { defineStore } from "pinia";
import { ref } from "vue";

export const useTrainingData = defineStore("training", () => {
	const trainingData = ref(null);
	const steps = ref(null);
	const selectedStep = ref(null);

	function setTrainingData(newTrainingData) {
		trainingData.value = newTrainingData;
		setSteps(newTrainingData.steps);
	}

	function setSteps(newSteps) {
		steps.value = newSteps;
		if (steps.value.length > 0) {
			selectStep(steps.value[0]);
		}
	}

	function addStep(newStep) {
		steps.value.push(newStep);
	}

	function selectStep(newStep) {
		selectedStep.value = newStep;
	}

	return {
		trainingData,
		setTrainingData,
		setSteps,
		steps,
		addStep,
		selectStep,
		selectedStep,
	};
});
