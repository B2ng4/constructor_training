<template>
	<div class="passage-toolbar">
		<q-btn
			v-if="hasPreviousStep"
			round
			dense
			icon="chevron_left"
			color="white"
			class="nav-btn"
			@click="$emit('prev')"
		>
			<q-tooltip>Предыдущий шаг</q-tooltip>
		</q-btn>

		<!-- Кнопка "Далее" для шагов без действия или при skip_steps -->
		<q-btn
			v-if="showNextButton"
			unelevated
			no-caps
			rounded
			color="primary"
			icon="arrow_forward"
			:label="hasNextStep ? 'Далее' : 'Завершить'"
			class="next-btn"
			@click="$emit('next')"
		/>

		<q-btn
			v-if="hasNextStep && !showNextButton"
			round
			dense
			icon="chevron_right"
			color="white"
			class="nav-btn"
			@click="$emit('next')"
		>
			<q-tooltip>Следующий шаг</q-tooltip>
		</q-btn>
	</div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
	hasPreviousStep: { type: Boolean, default: false },
	hasNextStep: { type: Boolean, default: false },
	selectedStep: { type: Object, default: null },
	skipSteps: { type: Boolean, default: false },
});

defineEmits(["prev", "next"]);

// Показывать кнопку "Далее" если: нет action_type, или skip_steps (свободная навигация)
const showNextButton = computed(() => {
	if (props.skipSteps) return true;
	return !props.selectedStep?.action_type;
});
</script>

<style scoped>
.passage-toolbar {
	position: absolute;
	bottom: 24px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 10;
	display: flex;
	align-items: center;
	gap: 12px;
}

.nav-btn {
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
	border: 1px solid rgba(0, 0, 0, 0.06);
}

.next-btn {
	padding: 10px 20px;
	font-weight: 600;
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.3);
}
</style>
