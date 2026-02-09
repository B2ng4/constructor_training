<template>
	<div class="column">
		<q-card style="width: 100%; max-width: 300px; border-radius: 20px">
			<q-card-section>
				<form-upload-photo
					@add-image="addImage"
					@download-photos="downloadPhotos"
					v-if="images.length === 0"
				/>
				<photo-list v-else @delete-image="deleteImage" :images="images" :title="true"/>
			</q-card-section>
		</q-card>
		<q-btn
			v-if="images.length > 0"
			class="q-mt-lg"
			color="primary"
			@click="uploadImages">
			Создать шаги
		</q-btn>
	</div>
</template>

<script setup>
import useDnd from "@composables/useDnd.js";
import {MetaTrainingApi} from "@api";
import {useRoute} from "vue-router";
import {
	FormUploadPhoto,
	PhotoList
} from "@components/features/edit_page/uploader_photo";

const emit = defineEmits(["uploadPhoto"]);
const metaApi = new MetaTrainingApi();
const [images, addImage] = useDnd();
const route = useRoute();

const downloadPhotos = (event) => {
	let files = [...event.target.files];
	images.value = files.map((item, index) => {
		return {
			id: index,
			name: item.name,
			url: URL.createObjectURL(item),
			size: item.size,
			originalFile: item,
		};
	});
	console.log(files);
};

const deleteImage = (id) => {
	images.value = images.value.filter((el) => {
		return el.id !== id;
	});
};

const uploadImages = async () => {
	try {
		let formData = new FormData();
		images.value.forEach((el) => {
			formData.append('files', el.originalFile);
		});
		await metaApi.uploadImages(route.params.uuid, formData);
		emit('uploadPhoto');
		//TODO ПОКА ТАК ПОТОМ СДЕЛАЕМ НОРМАЛЬНО
		window.location.reload();
	} catch {
		alert('Error');
	}
};
</script>
