<template>
	<q-layout view="hHh lpR fFf">
		<q-drawer width="250" show-if-above side="left" bordered>
			<EditPageSteps @select-url="selectTrainingUrl" :steps="traininData.steps"/>
		</q-drawer>

		<q-page-container>
			<div class="page-container" :class="{'justify-center': statusSteps}">
				<EditPageToolbar v-if="!statusSteps" style="margin-left: 5%"/>
				<EditPageUploadPhoto v-if="statusSteps"/>
				<EditPagePhotoView v-else :steps="steps"/>
			</div>
		</q-page-container>
	</q-layout>
</template>

<script>

import axios from "axios";
import EditPageUploadPhoto from "@components/for_pages/EditPage/EditPageUploadPhoto.vue";
import EditPageSteps from "@components/for_pages/EditPage/EditPageSteps.vue";
import EditPagePhotoView from "@components/for_pages/EditPage/EditPagePhotoView.vue";
import EditPageToolbar from "@components/for_pages/EditPage/EditPageToolbar.vue";
export default {
	components: {EditPageUploadPhoto, EditPageSteps, EditPagePhotoView, EditPageToolbar},
	data() {
		return {
			traininData: {},
			steps: '',
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
	min-height: 100vh;
	grid-gap: 5%
}
</style>