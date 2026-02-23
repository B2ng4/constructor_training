import { ref, computed, unref } from "vue";
import { createComparator } from "@utils/mixed.js";

/**
 * Состояние прохождения тренинга (без редактирования)
 * @param {import('vue').Ref|Object} trainingDataRef - реактивные данные тренинга
 */
export function usePassageData(trainingDataRef) {
	const steps = computed(() => {
		const data = unref(trainingDataRef);
		const s = data?.steps;
		if (!Array.isArray(s)) return [];
		return [...s].sort(createComparator("step_number"));
	});

	const currentIndex = ref(0);
	const selectedStep = computed(() => steps.value[currentIndex.value] ?? null);

	const hasPreviousStep = computed(() => currentIndex.value > 0);
	const hasNextStep = computed(() => currentIndex.value < steps.value.length - 1);

	function selectStepByIndex(idx) {
		if (idx >= 0 && idx < steps.value.length) {
			currentIndex.value = idx;
		}
	}

	function nextStep() {
		if (hasNextStep.value) {
			currentIndex.value++;
		}
	}

	function prevStep() {
		if (hasPreviousStep.value) {
			currentIndex.value--;
		}
	}

	function selectStep(step) {
		const idx = steps.value.findIndex((s) => s.id === step?.id);
		if (idx >= 0) currentIndex.value = idx;
	}

	const skipSteps = computed(() => !!unref(trainingDataRef)?.skip_steps);

	return {
		steps,
		currentIndex,
		selectedStep,
		hasPreviousStep,
		hasNextStep,
		selectStepByIndex,
		selectStep,
		nextStep,
		prevStep,
		skipSteps,
	};
}
