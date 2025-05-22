<template>
	<q-layout :class="{'display-none': statusEdit}"  view="hHh lpR fFf">
		<q-drawer width="250" show-if-above side="left" bordered>
			<EditPageSteps @select-url="selectTrainingUrl" :steps="traininData.steps"/>
			</q-drawer>

		<q-page-container  style="overflow: hidden">
			<EditPageGroupButtons @edit-training="editTrainingStatus"/>
			<div class="page-container justify-center">
				<EditPageUploadPhoto v-if="statusSteps"/>
				<EditPagePhotoView v-else :steps="steps"/>
			</div>
		</q-page-container>
	</q-layout>
	<EditPageEditPhoto :steps="steps" :status-edit="statusEdit"/>
</template>

<script>

import axios from "axios";
import EditPageUploadPhoto from "@components/for_pages/EditPage/EditPageUploadPhoto.vue";
import EditPageSteps from "@components/for_pages/EditPage/EditPageSteps.vue";
import EditPagePhotoView from "@components/for_pages/EditPage/EditPagePhotoView.vue";
import EditPageGroupButtons from "@components/for_pages/EditPage/EditPageGroupButtons.vue";
import EditPageEditPhoto from "@components/for_pages/EditPage/EditPageEditPhoto.vue";
export default {
	components: {EditPageUploadPhoto, EditPageSteps, EditPagePhotoView, EditPageGroupButtons, EditPageEditPhoto},
	data() {
		return {
			traininData: {},
			steps: '',
			statusEdit: false,
		}
	},
	computed: {
		statusSteps() {
			return this.traininData.steps && this.traininData.steps.length === 0;
		}
	},
	methods: {
		async getTraining() {
			axios.get(`${__BASE__URL__}/training/` + this.$route.params.uuid)
				.then((response) => {
					this.traininData = response.data;
				})
		},
		selectTrainingUrl(url) {
			this.steps = url;
		},
		editTrainingStatus(status) {
			this.statusEdit = status;
		}
	},
	mounted() {
		this.getTraining();
	}
}
</script>

<style scoped>
.page-container {
	position: relative;
	display: flex;
	align-items: center;
	grid-gap: 5%
}
</style>