import { ref, computed, unref } from "vue";
import { createComparator } from "@utils/mixed.js";

function compare(actual, operator, expected) {
	if (operator === "==") return String(actual) === String(expected);
	if (operator === "!=") return String(actual) !== String(expected);
	const left = Number(actual);
	const right = Number(expected);
	if (!Number.isFinite(left) || !Number.isFinite(right)) return false;
	if (operator === ">=") return left >= right;
	if (operator === "<=") return left <= right;
	if (operator === ">") return left > right;
	if (operator === "<") return left < right;
	return false;
}

function conditionMatches(condition, context) {
	if (!condition?.field) return true;
	return compare(context?.[condition.field], condition.operator || "==", condition.value);
}

export function usePassageData(trainingDataRef) {
	const steps = computed(() => {
		const data = unref(trainingDataRef);
		return Array.isArray(data?.steps)
			? [...data.steps].sort(createComparator("step_number"))
			: [];
	});
	const transitions = computed(() => unref(trainingDataRef)?.transitions || []);
	const hasScenario = computed(() => transitions.value.length > 0);
	const initialStepId = computed(() =>
		unref(trainingDataRef)?.scenario_start_step_id ?? steps.value[0]?.id ?? null,
	);
	const currentStepId = ref(null);
	const history = ref([]);
	const completed = ref(false);
	const selectedStep = computed(() => {
		const id = currentStepId.value ?? initialStepId.value;
		return steps.value.find((step) => step.id === id) ?? steps.value[0] ?? null;
	});
	const currentIndex = computed(() => steps.value.findIndex((step) => step.id === selectedStep.value?.id));
	const hasPreviousStep = computed(() => history.value.length > 0 || currentIndex.value > 0);
	const outgoingTransitions = computed(() =>
		transitions.value.filter((edge) => edge.source_step_id === selectedStep.value?.id),
	);
	const hasNextStep = computed(() => hasScenario.value ? outgoingTransitions.value.length > 0 : currentIndex.value < steps.value.length - 1);

	function setCurrent(stepId, remember = true) {
		if (remember && selectedStep.value?.id != null) history.value.push(selectedStep.value.id);
		currentStepId.value = stepId;
	}
	function selectStepByIndex(index) {
		const step = steps.value[index];
		if (step) setCurrent(step.id);
	}
	function selectStep(step) { if (step?.id != null) setCurrent(step.id); }
	function resolveTransition(event = "success", context = {}) {
		const routes = outgoingTransitions.value
			.filter((edge) => {
				if (edge.trigger_type === "default" || edge.is_default) return false;
				if (edge.trigger_type === "condition") return conditionMatches(edge.condition, context);
				if (edge.trigger_type === "attempts_exceeded") return event === "error" && conditionMatches(edge.condition, context);
				return edge.trigger_type === event;
			})
			.sort((a, b) => (b.priority || 0) - (a.priority || 0));
		return routes[0] || outgoingTransitions.value.find((edge) => edge.is_default || edge.trigger_type === "default") || null;
	}
	function advance(event = "success", context = {}) {
		if (!hasScenario.value) {
			if (event !== "success" || currentIndex.value >= steps.value.length - 1) return { completed: currentIndex.value >= steps.value.length - 1 };
			setCurrent(steps.value[currentIndex.value + 1].id);
			return { completed: false, step: selectedStep.value };
		}
		const transition = resolveTransition(event, context);
		if (!transition) return { completed: false, blocked: true };
		if (transition.target_step_id == null) {
			completed.value = true;
			return { completed: true, transition };
		}
		setCurrent(transition.target_step_id);
		return { completed: false, step: selectedStep.value, transition };
	}
	function nextStep(context = {}) { return advance("success", context); }
	function prevStep() {
		const previous = history.value.pop();
		if (previous != null) currentStepId.value = previous;
		else if (currentIndex.value > 0) currentStepId.value = steps.value[currentIndex.value - 1].id;
	}
	const skipSteps = computed(() => !!unref(trainingDataRef)?.skip_steps);
	return {
		steps, transitions, currentIndex, selectedStep, hasPreviousStep, hasNextStep,
		selectStepByIndex, selectStep, nextStep, prevStep, advance, resolveTransition,
		hasScenario, completed, skipSteps,
	};
}
