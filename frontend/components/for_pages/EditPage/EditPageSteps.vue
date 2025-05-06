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
					class="q-mb-md cursor-move"
					:key="element.step_number"
				>
					<template v-slot:title>
						Шаг: {{ element.step_number }}
					</template>
				</BaseCard>
			</template>
		</draggable>
	</div>
	<q-btn class="full-width" flat color="secondary" label="Добавить шаг" />
</template>

<script>
import BaseCard from "@components/BaseComponents/BaseCard.vue";
import draggable from 'vuedraggable';
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
		}
	},
	watch: {
		//Хорошая практика, когда мы не изменяем пропсы () => поэтому когда данные приходят, заносим в локальную переменную
		steps(newVal, oldVal) {
			if (newVal !== oldVal) {
				this.mySteps = newVal;
			}
		}
	}
};
</script>

<style scoped>
.my-card :last-child {
	display: none;
}
</style>