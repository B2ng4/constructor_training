<template>
	<q-card style="width: 100%; max-width: 300px; border-radius: 20px">
		<q-card-section>
			<div
				v-if="images.length === 0"
				class="column items-center justify-center cursor-pointer card-section"
				@click="downloadPhotos"
				@dragover.prevent
				@dragenter.prevent
				@dragleave.prevent
				@drop.prevent="addImage"
			>
				<q-icon class="block" size="100px" color="primary" name="image" />
				<h6 class="text-primary q-mt-xs">Выберите фото</h6>
				<input ref="fileInput" type="file" class="hidden"/>
			</div>
		</q-card-section>
	</q-card>
</template>

<script setup>
import { useRoute } from "vue-router";
import useDnd from "@composables/useDnd.js";
import { useTemplateRef } from "vue";

const route = useRoute();
const [images, addImage] = useDnd();
const fileInput = useTemplateRef("fileInput");

const downloadPhotos = () => {
	fileInput.value.click();
}
</script>

<style scoped>
.card-section {
	width: 100%;
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
