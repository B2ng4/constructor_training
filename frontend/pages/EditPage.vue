<template>
	<q-card class="my-card top-left-card q-ml-md q-mt-md row">
		<q-card-section>
			<q-btn color="secondary" label="Меню">
				<q-menu>
					<q-list style="min-width: 100px">
						<q-item clickable v-close-popup>
							<q-item-section>New tab</q-item-section>
						</q-item>
					</q-list>
				</q-menu>
			</q-btn>
		</q-card-section>
	</q-card>
	<q-card class="my-card q-ml-md q-mt-md row left-card">
		<q-card-section>

		</q-card-section>
	</q-card>
</template>

<script>

import axios from "axios";

export default {
	data() {
		return {
			traininData: []
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
.top-left-card{
	width: 100%;
	max-width: 300px;
	border-radius: 10px;
}

.left-card {
	width: 100%;
	max-width: 40px;
	height: 500px;
	border-radius: 10px;
}
</style>