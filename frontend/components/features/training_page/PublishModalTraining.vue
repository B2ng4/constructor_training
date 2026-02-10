<template>
	<q-dialog class="custom-dialog" v-model="model">
		<q-card class="q-pa-xs" style="min-width: 400px; width: 700px; border-radius: 14px">
			<q-card-section>
				<div class="text-h6">Ссылка на тренинг</div>
			</q-card-section>

			<q-card-section class="q-pt-none">
				<q-card class="q-mb-md q-pa-md bg-grey-3 row" flat>
					<q-icon name="visibility" color="grey-7" size="24px" class="q-mr-md"/>
					<div>
						<div class="text-subtitle2 q-mb-xs">Просмотр</div>
						<div class="text-body2 text-grey-8">
							Просматривать смогут все, у кого есть ссылка
						</div>
					</div>
				</q-card>

				<q-card class="q-mb-md q-pa-md bg-grey-3 row" flat>
					<q-icon name="shield" color="grey-7" size="24px" class="q-mr-md"/>
					<div>
						<div class="text-subtitle2 q-mb-xs">Настройки безопасности</div>
						<div class="text-body2 text-grey-8">
							Установить пароль, срок действия ссылки и запретить скачивание
						</div>
					</div>
				</q-card>

				<div class="row">
					<q-btn
						color="primary"
						label="Скопировать"
						no-caps
						icon="content_copy"
						class="rounded-12"
						padding="10px"
					/>
					<div class="q-ml-xl q-gutter-md">
						<q-btn
							color="grey-3"
							text-color="black"
							no-caps
							icon="mail"
							class="rounded-12"
							padding="10px"
						/>
						<q-btn
							color="grey-3"
							text-color="black"
							no-caps
							icon="qr_code"
							class="rounded-12"
							padding="10px"
						/>
					</div>
					<q-btn
						color="grey-3"
						text-color="black"
						no-caps
						icon="link"
						class="rounded-12 q-ml-auto"
						padding="10px"
						@click="publishTraining"
					/>
				</div>
			</q-card-section>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { trainingApi } from "@api/api/TrainingApi.js";

const model = defineModel();
const props = defineProps(['data']);
const emit = defineEmits(['updatePublish']);

async function publishTraining() {
	try {
		await trainingApi.updateTraining(props.data.uuid, {publish: !props.data.publish});
		emit('updatePublish');
	} catch (e) {
		console.error(e);
	}
}
</script>

<style scoped>
</style>