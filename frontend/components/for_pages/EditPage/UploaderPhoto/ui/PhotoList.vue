<template>
	<h6 class="q-ma-none q-mb-lg">Загруженные изображения</h6>
	<q-list padding>
		<q-item
			clickable
			v-ripple
			:key="element.id"
			v-for="element in props.images"
			@click="openModal(element)"
		>
			<q-item-section>
				<p class="q-ma-none">{{ element.name }}</p>
			</q-item-section>
			<q-item-section>
				<q-icon
					@click.stop="emit('deleteImage', element.id)"
					color="grey"
					size="34px"
					name="delete"
					class="q-ml-auto delete-icon"
				/>
			</q-item-section>
		</q-item>
	</q-list>
	<modal-preview :image="selectedImage" v-model="modal" />
</template>

<script setup>
import { ModalPreview } from "@components/for_pages/EditPage/UploaderPhoto";
import { ref } from "vue";

const props = defineProps(["images"]);
const emit = defineEmits(["deleteImage"]);

const selectedImage = ref(null);
const modal = ref(false);

const openModal = (element) => {
	selectedImage.value = element;
	modal.value = true;
};
</script>

<style scoped>
.delete-icon:hover {
	cursor: pointer;
	transform: scale(1.2);
}
</style>