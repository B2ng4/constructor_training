<template>
	<div class="container">
		<div class="header cursor-pointer" @click="$refs.input.click()">
			<img
				style="width: 100px"
				src="@assets/img/cloud.svg"
				alt="нет изображения"
			/>
			<p>Выберите файл для загрузки!</p>
		</div>
		<label v-if="photos.length <= 0" for="file" class="footer">
			<img src="@assets/img/file.svg" alt="нет изображения" />
			<p>Файлы не выбраны</p>
		</label>
		<input ref="input" id="file" type="file" @change="previewFiles" multiple accept=".jpg, .png"/>
		<div class="row group-photo">
			<q-chip
				removable
				clickable
				@remove="deletePhoto(photo)"
				class="chip cursor-pointer"
				v-for="photo in photos"
				:key="photo"
				size="14px"
				icon="photo"
				@click="openModal(photo.url)"
				:label="photo.name"
				:title="photo.name"
			>
			</q-chip>
		</div>
		<q-btn
			v-if="photos.length > 0"
			color="secondary"
			label="Отправить"
			@click="uploadPhoto()"
		/>

	</div>
	<q-dialog v-model="modalOpen" full-width>
		<q-card>
			<q-card-section class="q-pt-none">
				<img :src="urlImg">
			</q-card-section>
		</q-card>
	</q-dialog>
</template>

<script>
import axios from "axios";

export default {
	name: "EditPageUploadPhoto",
	data() {
		return {
			photos: [],
			modalOpen: false,
			urlImg: '',
			files: []
		};
	},
	methods: {
		previewFiles(event) {
			const files = Array.from(event.target.files);

			this.photos = [];
			this.files = [];

			files.forEach(file => {
				this.photos.push({
					url: URL.createObjectURL(file),
					size: file.size,
					name: file.name,
				});
				this.files.push(file);
			});
		},
		deletePhoto(photo) {
			const index = this.photos.indexOf(photo);
			this.photos.splice(index, 1);
			this.files.splice(index, 1);
		},
		openModal(url) {
			this.modalOpen = true;
			this.urlImg = url;
		},
		async uploadPhoto() {
			if (this.files.length === 0) {
				console.error('No files to upload');
				return;
			}

			try {
				const formData = new FormData();

				this.files.forEach((file, index) => {
					formData.append(`files`, file);
				});

				const result = await axios.post(
					`${__BASE__URL__}/training/upload-photos/${this.$route.params.uuid}`,
					formData,
					{
						headers: {
							Authorization: `Bearer ${localStorage.getItem('tokenAuth')}`
						}
					}
				);

				this.photos = [];
				this.files = [];
				this.$refs.input.value = '';

				return result.data;
			} catch (err) {
				console.error('Upload failed:', err);
				throw err;
			}
		}
	},
	beforeUnmount() {
		this.photos.forEach(photo => {
			URL.revokeObjectURL(photo.url);
		});
	}
};
</script>

<style scoped>
.container {
	width: 300px;
	height: auto;
	max-height: 500px;
	border-radius: 10px;
	box-shadow: 4px 4px 30px rgba(0, 0, 0, 0.2);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: space-between;
	padding: 10px;
	gap: 5px;
	background-color: rgba(0, 110, 255, 0);
}

.header {
	flex: 1;
	padding: 26px;
	width: 100%;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-direction: column;
}

.header p {
	text-align: center;
	color: black;
}

.footer {
	background-color: rgba(98, 116, 248, 0.15);
	width: 100%;
	height: 40px;
	padding: 8px;
	border-radius: 10px;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: flex-end;
	color: black;
	border: none;
}

.footer img {
	height: 130%;
	fill: #6274f8;
	background-color: rgba(70, 66, 66, 0.103);
	border-radius: 50%;
	padding: 2px;
	cursor: pointer;
	box-shadow: 0 2px 30px rgba(0, 0, 0, 0.205);
}

.footer p {
	flex: 1;
	text-align: center;
	margin-bottom: 0;
}

#file {
	display: none;
}

.chip {
	background-color: rgba(98, 116, 248, 0.15);
	padding: 16px;
	width: 100%;
}

.group-photo {
	max-width: 100%;
	overflow-y: scroll;
	padding: 10px;
	overflow-x: hidden;
}
/* Убираем скролл */
.group-photo::-webkit-scrollbar { width: 0 !important }
</style>