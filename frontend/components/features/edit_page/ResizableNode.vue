<template>
	<NodeResizer min-width="100" min-height="30" />
	<NodeToolbar :is-visible="node.data.toolbarVisible">
		<div class="column">
			<template v-if="saveMode">
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
</style>

