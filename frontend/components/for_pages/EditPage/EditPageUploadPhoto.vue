<template>
	<div class="container fixed-center">
		<div class="header">
			<img style="width: 100px" src="@assets/img/cloud.svg">
 			<p>Выберите файл для загрузки!</p>
		</div>
		<label for="file" class="footer">
			<img src="@assets/img/file.svg">
			<p>Файлы не выбраны</p>
			<img style="width: 30px" src="@assets/img/trash.svg">
		</label>
		<input id="file" type="file" @change="previewFiles" multiple>
	</div>
</template>


<script>
export default {
	name: "EditPageUploadPhoto",
	data() {
		return {
			photos: [],
		}
	},
	methods: {
		previewFiles(event) {
				const imageURL = URL.createObjectURL(event.target.files[0]);
				this.photos = imageURL
		}
	}
};
</script>

<style scoped>
.container {
	height: 300px;
	width: 300px;
	border-radius: 10px;
	box-shadow: 4px 4px 30px rgba(0, 0, 0, .2);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: space-between;
	padding: 10px;
	gap: 5px;
	background-color: rgba(0, 110, 255, 0.041);
}

.header {
	flex: 1;
	width: 100%;
	border: 2px dashed #6274F8;
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
	background-color: rgba(0, 110, 255, 0.075);
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
	fill: #6274F8;
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
</style>