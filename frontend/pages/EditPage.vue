<template>
	<q-layout view="hHh lpR fFf">
		<q-drawer width="250" show-if-above side="left" bordered>
			<EditPageSteps :steps="traininData.steps"/>
		</q-drawer>

		<q-page-container>
			<EditPageUploadPhoto v-if="traininData.steps && traininData.steps.length === 0" />
		</q-page-container>
	</q-layout>
</template>

<script>

import axios from "axios";
import EditPageUploadPhoto from "@components/for_pages/EditPage/EditPageUploadPhoto.vue";
import EditPageSteps from "@components/for_pages/EditPage/EditPageSteps.vue";
export default {
	components: {EditPageUploadPhoto, EditPageSteps},
	data() {
		return {
			traininData: {},
		}
	},
	methods: {
		async getTraining() {
			axios.get(`${__BASE__URL__}/training/` + this.$route.params.uuid)
				.then((response) => {
					this.traininData = response.data;
				})
		}
	},
	mounted() {
		this.getTraining();
	}
}
</script>

<style scoped></style>