<template>
	<div class="q-ma-md column">
		<BaseCard v-for="step in steps" :key="step">
			<template v-slot:title>
				Шаг: {{ step.step_number }}
			</template>
		</BaseCard>
		<q-btn class="q-mt-md" flat color="secondary" label="Добавить шаг" />
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
	watch: {
		steps(newVal) {
			if (newVal) {

			}
		}
	}
};
</script>

<style scoped>

</style>