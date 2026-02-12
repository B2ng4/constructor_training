<template>
	<NodeResizer min-width="100" min-height="30" />
	<NodeToolbar :is-visible="node.data.toolbarVisible">
		<div class="column">
			<template v-if="saveMode">
				<div
					v-if="selectedMode === 'keyPress'"
					class="column q-mb-sm hotkey-controls"
				>
					<q-btn
						no-caps
						outline
						color="primary"
						@click="openHotkeyCapture"
					>
						Назначить хоткей
					</q-btn>
					<div class="row items-center q-gutter-xs q-mt-xs">
						<div class="text-caption text-grey-8">
							Хоткей:
						</div>
						<div class="text-caption text-grey-8">
							{{ hotkeyLabel }}
						</div>
					</div>
				</div>
				<q-btn
					no-caps
					color="primary"
					@click="sendRequest"
				>
					Сохранить
				</q-btn>
			</template>
		</div>
	</NodeToolbar>
	<Handle type="target" :position="Position.Left" />
	<Handle type="source" :position="Position.Right" />
	<template v-if="selectedMode === 'inputText'">
		<input-text
			v-model="metaText"
		/>
	</template>
	<template v-if="selectedMode === 'keyPress'">
		<watch-key
			v-model="metaKeywords"
			v-model:open="isHotkeyDialogOpen"
		/>
	</template>
</template>

<script setup>
import { Handle, Position } from '@vue-flow/core';
import { NodeResizer } from '@vue-flow/node-resizer';
import { NodeToolbar } from '@vue-flow/node-toolbar';
import { computed, ref } from "vue";
import { trainingStepApi } from "@api";
import { useTrainingData } from "@store/editTraining.js";
import InputText from "@components/features/edit_page/InputText.vue";
import WatchKey from "@components/features/edit_page/WatchKey.vue";

const props = defineProps(['node', 'position']);
const store = useTrainingData();
const isHotkeyDialogOpen = ref(false);

const metaText = computed({
	get() {
		return store.selectedStep.area?.metaText || '';
	},
	set(value) {
		// Создаем объект area, если он не существует
		if (!store.selectedStep.area) {
			store.selectedStep.area = {
				metaText: '',
			};
		}
		store.selectedStep.area.metaText = value;
	}
});

const metaKeywords = computed({
	get() {
		return store.selectedStep.area?.metaKeywords || [];
	},
	set(value) {
		if (!store.selectedStep.area) {
			store.selectedStep.area = {
				metaKeywords: []
			};
		}
		store.selectedStep.area.metaKeywords = value;
	}
})

//Для отображения кнопки для сохранения зоны
const saveMode = ref(true);

const selectedMode = computed(() => {
	console.log(props.node.data.type);
	return props.node.data.type;
});

const hotkeyLabel = computed(() => {
	return metaKeywords.value?.join('+') || 'не назначен';
});

const openHotkeyCapture = () => {
	isHotkeyDialogOpen.value = true;
};

const sendRequest = async () => {
	try {
		await trainingStepApi.editStep(
			store.trainingData.uuid,
			store.selectedStep.id,
			{
				action_type_id: store.selectedEvent.id,
				area: {
					width: props.node.dimensions.width,
					height: props.node.dimensions.height,
					x: props.position.x,
					y: props.position.y,
					metaText: metaText.value,
					metaKeywords: metaKeywords.value
				}
			}
		);
	} catch (e) {
		console.error(e);
	}
};
</script>

<style>
@import "@vue-flow/node-resizer/dist/style.css";

.hotkey-controls {
	min-width: 180px;
}
</style>

