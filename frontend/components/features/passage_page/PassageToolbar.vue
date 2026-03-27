<template>
	<div class="passage-toolbar">
		<q-btn
			v-if="hasPreviousStep"
			round
			unelevated
			dense
			icon="chevron_left"
			color="primary"
			class="nav-btn nav-btn--round"
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
			unelevated
			dense
			icon="chevron_right"
			color="primary"
			class="nav-btn nav-btn--round"
			@click="$emit('next')"
		>
			<q-tooltip>Следующий шаг</q-tooltip>
		</q-btn>

		<q-btn
			v-if="hintsAvailable"
			round
			unelevated
			dense
			:icon="hintsEnabled ? 'lightbulb' : 'lightbulb_outline'"
			:color="hintsEnabled ? 'amber' : 'grey-7'"
			class="nav-btn nav-btn--round nav-btn--hints"
			@click="$emit('toggle-hints')"
		>
			<q-tooltip>
				{{
					hintsEnabled
						? "Подсказки включены: после ошибки подсветим область или подставим текст"
						: "Включить подсказки после ошибки"
				}}
			</q-tooltip>
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
	hintsEnabled: { type: Boolean, default: false },
	hintsAvailable: { type: Boolean, default: true },
});

defineEmits(["prev", "next", "toggle-hints"]);

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
	left: 0;
	right: 0;
	width: 100%;
	padding: 0 20px;
	box-sizing: border-box;
	z-index: 25;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-wrap: wrap;
	gap: 12px;
	pointer-events: none;
}

.nav-btn--hints {
	box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
}

.passage-toolbar > * {
	pointer-events: auto;
}

.nav-btn--round {
	width: 44px;
	height: 44px;
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.35);
}

.nav-btn--round :deep(.q-btn__wrapper) {
	padding: 0;
	min-height: 44px;
	min-width: 44px;
}

.next-btn {
	padding: 10px 20px;
	font-weight: 600;
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.3);
}
</style>
