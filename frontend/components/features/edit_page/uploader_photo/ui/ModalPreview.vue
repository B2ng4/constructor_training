<template>
	<q-dialog v-model="model" maximized>
		<div @click="model = false" class="full-height full-width fixed-full no-scroll flex flex-center">
			<q-img
				fit="contain"
				:src="image.url"
				:style="{
					'max-height': '100vh',
					'max-width': '100vw'
				}"
			/>
		</div>
	</q-dialog>
</template>

<script setup>
const model = defineModel();
defineProps(["image"]);
</script>

<style scoped>
.no-scroll {
	overflow: hidden;
}
</style>