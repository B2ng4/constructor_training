<template>
	<div>
		<h6 class="q-ma-none q-mb-md" v-if="title">Загруженные изображения ({{ props.images.length }})</h6>
		<div class="photo-grid">
			<div
				v-for="element in props.images"
				:key="element.id"
				class="photo-card"
				@click="openModal(element)"
			>
				<div class="photo-thumb">
					<q-img
						:src="element.url"
						fit="cover"
						class="thumb-img"
						spinner-color="primary"
						spinner-size="20px"
					/>
					<div class="photo-overlay">
						<q-btn
							flat
							round
							dense
							icon="zoom_in"
							color="white"
							size="sm"
						/>
					</div>
				</div>
				<div class="photo-info">
					<span class="photo-name">{{ element.name }}</span>
					<q-btn
						flat
						round
						dense
						icon="close"
						color="grey-6"
						size="xs"
						class="delete-btn"
						@click.stop="emit('deleteImage', element.id)"
					>
						<q-tooltip>Удалить</q-tooltip>
					</q-btn>
				</div>
			</div>
		</div>
		<modal-preview :image="selectedImage" v-model="modal" />
	</div>
</template>

<script setup>
import { ModalPreview } from "@components/features/edit_page/uploader_photo";
import { ref } from "vue";

const props = defineProps(["images", "title"]);
const emit = defineEmits(["deleteImage"]);

const selectedImage = ref(null);
const modal = ref(false);

const openModal = (element) => {
	selectedImage.value = element;
	modal.value = true;
};
</script>

<style scoped>
.photo-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
	gap: 12px;
	width: 100%;
}

.photo-card {
	border-radius: 10px;
	border: 1px solid rgba(0, 0, 0, 0.08);
	overflow: hidden;
	cursor: pointer;
	transition: box-shadow 0.2s, transform 0.2s;
	background: #fff;
}

.photo-card:hover {
	box-shadow: 0 4px 16px rgba(0, 0, 0, 0.10);
	transform: translateY(-2px);
}

.photo-thumb {
	position: relative;
	width: 100%;
	height: 100px;
	overflow: hidden;
}

.thumb-img {
	width: 100%;
	height: 100%;
}

.photo-overlay {
	position: absolute;
	inset: 0;
	background: rgba(0, 0, 0, 0.3);
	display: flex;
	align-items: center;
	justify-content: center;
	opacity: 0;
	transition: opacity 0.2s;
}

.photo-card:hover .photo-overlay {
	opacity: 1;
}

.photo-info {
	display: flex;
	align-items: center;
	padding: 6px 8px;
	gap: 4px;
}

.photo-name {
	flex: 1;
	min-width: 0;
	font-size: 12px;
	color: #555;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.delete-btn {
	flex-shrink: 0;
	opacity: 0.5;
	transition: opacity 0.2s;
}

.delete-btn:hover {
	opacity: 1;
}
</style>
