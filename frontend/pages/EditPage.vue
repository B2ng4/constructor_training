<template>
	<q-layout view="hHh lpR fFf">

		<q-drawer width="250" show-if-above side="left" bordered>
			<!-- drawer content -->
		</q-drawer>

		<q-page-container>
			<EditPageUploadPhoto/>
		</q-page-container>

	</q-layout>
</template>

<script>

import axios from "axios";
import EditPageUploadPhoto from "@components/for_pages/EditPage/EditPageUploadPhoto.vue";
export default {
	components: {EditPageUploadPhoto},
	data() {
		return {
			traininData: [],
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

<style scoped>
</style>