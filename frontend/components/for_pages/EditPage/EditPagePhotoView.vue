<template>
		<q-img class="rounded-8" :src="steps.image_url" no-native-menu style="width: 70%;">
			<div class="absolute-top text-center">
				Caption
			</div>
		</q-img>
</template>

<script>
export default {
	name: "EditPagePhotoView",
	props: {
		steps: {
			type: String,
		}
	}
};
</script>

<style scoped>
</style>