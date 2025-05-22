<template>
	<div :class="{'display-none': !statusEdit}">
		<q-img class="rounded-8" :src="steps.image_url" no-native-menu style="width: 100%;">
		</q-img>
	</div>
</template>

<script>
export default {
	name: "EditPageEditPhoto",
	props: {
		steps: {
			type: String,
		},
		statusEdit: {
			type: Boolean,
			default: false,
		}
	}
};
</script>

<style scoped>

</style>