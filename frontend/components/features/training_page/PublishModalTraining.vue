<template>
	<q-dialog class="publish-dialog custom-dialog" v-model="model">
		<q-card class="publish-modal-card q-pa-xs">
			<q-card-section class="modal-header">
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

				<!-- Поле со ссылкой (после публикации) -->
				<q-input
					v-if="publicLink"
					v-model="publicLink"
					readonly
					outlined
					dense
					class="q-mb-md"
				>
					<template #append>
						<q-btn flat dense round icon="content_copy" @click="copyLink">
							<q-tooltip>Скопировать ссылку</q-tooltip>
						</q-btn>
					</template>
				</q-input>

				<div class="row">
					<q-btn
						color="primary"
						:label="publicLink ? 'Скопировать' : 'Опубликовать'"
						no-caps
						:icon="publicLink ? 'content_copy' : 'publish'"
						class="rounded-12"
						padding="10px"
						:loading="publishing"
						@click="publicLink ? copyLink() : publish()"
					/>
					<div class="q-ml-xl q-gutter-md">
						<q-btn
							color="grey-3"
							text-color="black"
							no-caps
							icon="mail"
							class="rounded-12"
							padding="10px"
							:disable="!publicLink"
							@click="shareByEmail"
						>
							<q-tooltip>Отправить по почте</q-tooltip>
						</q-btn>
						<q-btn
							color="grey-3"
							text-color="black"
							no-caps
							icon="open_in_new"
							class="rounded-12"
							padding="10px"
							:disable="!publicLink"
							@click="openLink"
						>
							<q-tooltip>Открыть в новой вкладке</q-tooltip>
						</q-btn>
					</div>
					<q-btn
						color="grey-3"
						text-color="black"
						no-caps
						icon="link"
						class="rounded-12 q-ml-auto"
						padding="10px"
						:disable="!publicLink"
						@click="copyLink"
					>
						<q-tooltip>Скопировать ссылку</q-tooltip>
					</q-btn>
				</div>
			</q-card-section>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { ref, watch } from "vue";
import { trainingApi } from "@api/api/TrainingApi.js";
import { useQuasar } from "quasar";

const model = defineModel();
const props = defineProps(['data']);
const emit = defineEmits(['published']);

const $q = useQuasar();
const publicLink = ref("");
const publishing = ref(false);

watch(model, (val) => {
	if (!val) {
		publicLink.value = "";
	}
});

async function publish() {
	if (!props.data?.uuid) return;
	publishing.value = true;
	try {
		const { data } = await trainingApi.publishTraining(props.data.uuid);
		publicLink.value = data.public_link;
		emit("published");
		$q.notify({
			color: "positive",
			message: "Тренинг опубликован",
			position: "bottom-right",
			icon: "check_circle",
		});
	} catch (e) {
		console.error(e);
		$q.notify({
			color: "negative",
			message: "Не удалось опубликовать тренинг",
			position: "top",
		});
	} finally {
		publishing.value = false;
	}
}

async function copyLink() {
	try {
		await navigator.clipboard.writeText(publicLink.value);
		$q.notify({
			color: "positive",
			message: "Ссылка скопирована",
			position: "bottom-right",
			icon: "content_copy",
			timeout: 1500,
		});
	} catch {
		$q.notify({
			color: "negative",
			message: "Не удалось скопировать",
			position: "top",
		});
	}
}

function openLink() {
	window.open(publicLink.value, "_blank");
}

function shareByEmail() {
	const subject = encodeURIComponent(props.data?.title ?? "Тренинг");
	const body = encodeURIComponent(`Пройдите тренинг: ${publicLink.value}`);
	window.open(`mailto:?subject=${subject}&body=${body}`);
}
</script>

<style scoped>
.publish-modal-card {
	min-width: 400px;
	width: 700px;
	max-width: 95vw;
	border-radius: 16px;
	box-shadow: 0 24px 56px rgba(0, 0, 0, 0.14);
	animation: scaleIn 0.3s var(--anim-ease-spring) forwards;
}
.publish-modal-card .modal-header {
	padding: 20px 24px;
	border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
.publish-modal-card .q-card > .q-card__section:not(.modal-header) {
	transition: background 0.2s ease;
}
.publish-modal-card .q-card.flat.bg-grey-3:hover {
	background: rgba(80, 100, 247, 0.04) !important;
}
.publish-modal-card .rounded-12 {
	transition: transform 0.25s var(--anim-ease-spring), box-shadow 0.25s ease;
}
.publish-modal-card .rounded-12:hover:not(:disabled) {
	transform: translateY(-1px);
}
</style>
