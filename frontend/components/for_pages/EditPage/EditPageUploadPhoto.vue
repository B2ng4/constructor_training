<template>
	<q-card class="my-card upload-photo-card fixed-center q-pa-xl">
		<q-card-section>
			<q-file class="q-mt-xl" outlined v-model="photos" multiple>
				<template v-slot:prepend>
					<q-icon name="attach_file" />
				</template>
			</q-file>
		</q-card-section>
	</q-card>
</template>

<script>
export default {
	name: "EditPageUploadPhoto",
	data() {
		return {
			photos: [],
		}
	}
};
</script>


<style scoped>
.upload-photo-card {
	border-radius: 15px;
	max-width: 100%;
	max-height: 100%;
	height: 400px;
	width: 400px;
}
</style>