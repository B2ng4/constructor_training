<template>
	<div class="q-ma-md column">
		<BaseCard
			@drag="replace(step, step.step_number,)"
			draggable="true"
			class="q-mb-md cursor-move"
			v-for="step in steps"
			:key="step"
		>
			<template v-slot:title>
				Шаг: {{ step.step_number }}
			</template>
		</BaseCard>
		<q-btn flat color="secondary" label="Добавить шаг" />
	</div>
</template>

<script>
import BaseCard from "@components/BaseComponents/BaseCard.vue";
export default {
	name: "EditPageSteps",
	components: {BaseCard},
	props: {
		steps: ''
	},
	methods: {
		replace(step, newPosition, oldPosition) {
			this.steps
		}
	}
};
</script>

<style scoped>
.my-card :last-child {
	display: none;
}
</style>