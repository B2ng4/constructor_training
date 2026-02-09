<template>
	<q-dialog v-model="value" persistent>
		<q-card style="min-width: 350px">
			<q-card-section>
				<div class="text-h6">Создать шаг</div>
			</q-card-section>
			<q-card-section class="flex column q-gutter-md">
				<photo-list
					@delete-image="deleteImage"
					:images="images"
					:title="false"
					v-if="images.length > 0"
				/>
				<q-btn flat color="primary" @click="addPhoto">Добавить изображение</q-btn>
			</q-card-section>
			<q-card-actions align="right" class="text-primary">
				<q-btn flat label="Отмена" v-close-popup />
				<q-btn flat label="Создать" @click="addSteps" />
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { useRoute } from "vue-router";
import { MetaTrainingApi } from "@api/api/MetaTrainingApi.js";
import { ref } from "vue";
import { PhotoList } from "@components/features/edit_page/uploader_photo";

const value = defineModel();
const route = useRoute();
const api = new MetaTrainingApi();
const images = ref([]);

const addPhoto = () => {
	const input = document.createElement('input');
	input.type = 'file';
	input.multiple = true;
	input.accept = 'image/*';

	input.onchange = (event) => {
		const files = event.target.files;
		if (!files || files.length === 0) return;

		const newImages = Array.from(files).map((file, index) => ({
			id: Date.now() + index,
			name: file.name,
			url: URL.createObjectURL(file),
			size: file.size,
			originalFile: file,
		}));

		images.value = [...images.value, ...newImages];
	};
	input.click();
};

const deleteImage = (id) => {
	images.value = images.value.filter((el) => {
		return el.id !== id;
	});
};

const addSteps = async () => {
	try {
		let formData = new FormData();
		images.value.forEach((el) => {
			formData.append('files', el.originalFile);
		});
		await api.uploadImages(route.params.uuid, formData);
		images.value = [];
		value.value = false;
		window.location.reload();
	} catch {
			alert('Ошибка создания шагов');
	}
};
</script>