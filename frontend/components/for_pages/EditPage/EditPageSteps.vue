<template>
	<div class="q-ma-md column">
		<draggable
			:list="mySteps"
			@start="drag=true"
			@end="drag=false"
			item-key="id"
		>
			<template #item="{element}">
				<BaseCard
					@click="selectedTrainingStep(element)"
					class="q-mb-md cursor-move"
					:key="element.step_number"
					:class="{ 'selected-steps': selectTrainingStep === element }"
				>
					<template v-slot:title>
						Шаг: {{ element.step_number }}
					</template>
				</BaseCard>
			</template>
		</draggable>
	</div>
	<q-btn class="full-width" @click="updateSteps" flat color="secondary" label="Добавить шаг" />
</template>

<script>
import BaseCard from "@components/BaseComponents/BaseCard.vue";
import draggable from 'vuedraggable';
import axios from "axios";
export default {
	name: "EditPageSteps",
	components: { BaseCard, draggable},
	props: {
		steps: {
			type: Array,
		}
	},
	data() {
		return {
			drag: false,
			mySteps: [],
			selectTrainingStep: null
		}
	},
	methods: {
		selectedTrainingStep(stepNumber) {
			this.selectTrainingStep = stepNumber;
		},
		async updateSteps() {
			let payload = this.mySteps;
			let response = await axios.put(`${__BASE__URL__}/training/${this.$route.params.uuid}`, {payload});
			try {
				console.log(response);
			} catch (error) {
				console.log(error);
			}
		}
	},
	watch: {
		steps(newVal, oldVal) {
			if (newVal !== oldVal) {
				this.mySteps = newVal;
				this.selectTrainingStep = this.mySteps[0];
			}
		},
		mySteps: {
			handler(newVal) {
				if (newVal) {
					this.mySteps.forEach((step, index) => {
						step.step_number = index + 1;
					});
				}
			},
			deep: true
		}
	}
};
</script>

<style scoped>
.my-card :last-child {
	display: none;
}

.selected-steps {
	border: 2px solid #6274F8;
	transition: all 0.1s ease-out;
	transform: scale(1.03);
}
</style>