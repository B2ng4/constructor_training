<template>
	<q-card style="width: 100%; max-width: 300px; border-radius: 20px">
		<q-card-section>
			<h6 class="q-ma-none">Загрузите изображение</h6>
		</q-card-section>
		<q-card-section>
			<div
				class="column items-center"
				style="width: 100%;
				height: 300px;
				border-radius: 15px;
				background-color: rgba(236,234,234,0.27)"
			>
				<q-icon
					size="60px"
					color="grey"
					name="add_photo_alternate"
					class="q-mt-md"
				/>
				<q-btn
					color="primary"
					label="Загрузить"
					class="q-mt-md"
				/>
			</div>
		</q-card-section>
	</q-card>
</template>

<script setup>
import { useRoute } from 'vue-router';

const route = useRoute();

</script>

<style scoped>

</style>