<template>
	<div class="flex content-end q-mt-md q-mr-xl column q-gutter-md">
		<EditPageGroupButtonsPublicTraning/>
		<q-btn class="toolbar-btn">
				<span @click="editTraining" class="btn-label">Редактировать</span>
		</q-btn>
	</div>
</template>

<script>
import EditPageGroupButtonsPublicTraning from "@components/for_pages/EditPage/EditPageGroupButtonsPublicTraning.vue";
export default {
	name: "EditPageGroupButtons",
	components: {EditPageGroupButtonsPublicTraning},
	data() {
		return {
			editTrainingStatus: false,
		}
	},
	methods: {
		editTraining() {
			this.editTrainingStatus = true;
			this.$emit("edit-training", this.editTrainingStatus);
		}
	}
};
</script>

<style scoped>
.toolbar-btn {
	width: auto;
	border: 2px solid #6274F8;
}
</style>