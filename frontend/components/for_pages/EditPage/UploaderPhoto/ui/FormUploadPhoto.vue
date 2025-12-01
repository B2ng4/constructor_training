<template>
	<div
		class="column items-center justify-center cursor-pointer card-section"
		@click="$refs.fileInput.click()"
		@dragover.prevent
		@drop.prevent="(e) => emit('addImage', e)"
		@dragenter.prevent
		@dragleave.prevent
	>
		<q-icon class="block" size="100px" color="primary" name="image" />
		<h6 class="text-primary q-mt-xs">Выберите фото</h6>
		<p class="text-primary">Либо перетащите</p>
		<input multiple @change="(e) => emit('downloadPhotos', e)" ref="fileInput" type="file" class="hidden"/>
	</div>
</template>

<script setup>
const emit = defineEmits(['downloadPhotos', 'addImage']);
</script>

<style scoped>
.card-section {
	max-width: 100%;
	width: 300px;
	height: 300px;
	border-radius: 15px;
	border: 2px dashed rgba(89, 106, 246, 0.24);
	background-color: rgba(191, 197, 244, 0.24);
	transition: background-color 0.4s;
}

.card-section:hover {
	background-color: rgba(148, 159, 243, 0.24);
	transition: 0.3s;
}
</style>