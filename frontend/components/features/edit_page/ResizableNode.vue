<template>
	<NodeResizer min-width="100" min-height="30" />
	<NodeToolbar :is-visible="node.data.toolbarVisible">
		<div class="node-toolbar-content">
			<template v-if="saveMode">
				<div
					v-if="selectedMode === 'keyPress'"
					class="hotkey-controls"
				>
					<q-btn
						dense
						no-caps
						outline
						size="sm"
						color="primary"
						icon="keyboard"
						label="Хоткей"
						@click="openHotkeyCapture"
					/>
					<span class="hotkey-label">{{ hotkeyLabel }}</span>
				</div>
				<q-btn
					dense
					no-caps
					unelevated
					color="primary"
					icon="save"
					label="Сохранить"
					@click="sendRequest"
				>
					<q-tooltip>Сохранить область</q-tooltip>
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
import { computed, inject, nextTick, ref } from "vue";
import { useQuasar } from "quasar";
import { trainingStepApi } from "@api";
import { useTrainingData } from "@store/editTraining.js";
import InputText from "@components/features/edit_page/InputText.vue";
import WatchKey from "@components/features/edit_page/WatchKey.vue";

const props = defineProps(['node']);
const $q = useQuasar();
const store = useTrainingData();
const getAreaForSave = inject("getAreaForSave", () => null);
const isHotkeyDialogOpen = ref(false);

const metaText = computed({
	get() {
		return store.selectedStep.area?.metaText || '';
	},
	set(value) {
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

const saveMode = ref(true);

const selectedMode = computed(() => props.node.data.type);

const hotkeyLabel = computed(() => {
	return metaKeywords.value?.join('+') || 'не назначен';
});

const openHotkeyCapture = () => {
	isHotkeyDialogOpen.value = true;
};

const sendRequest = async () => {
	try {
		await nextTick();
		const area = getAreaForSave?.();
		if (!area || !area.width || !area.height) {
			$q.notify({ color: "negative", message: "Не удалось определить область", position: "top" });
			return;
		}

		await trainingStepApi.editStep(
			store.trainingData.uuid,
			store.selectedStep.id,
			{
				action_type_id: store.selectedEvent.id,
				area: {
					...area,
					metaText: metaText.value,
					metaKeywords: metaKeywords.value
				}
			}
		);
		if (!store.selectedStep.area) store.selectedStep.area = {};
		Object.assign(store.selectedStep.area, area, {
			metaText: metaText.value,
			metaKeywords: metaKeywords.value
		});
		$q.notify({
			color: "positive",
			message: "Область сохранена",
			position: "bottom-right",
		});
	} catch (e) {
		$q.notify({
			color: "negative",
			message: "Не удалось сохранить",
			position: "top",
		});
	}
};
</script>

<style>
@import "@vue-flow/node-resizer/dist/style.css";

.node-toolbar-content {
	display: flex;
	align-items: center;
	gap: 8px;
	background: rgba(255, 255, 255, 0.92);
	backdrop-filter: blur(12px);
	-webkit-backdrop-filter: blur(12px);
	padding: 6px 10px;
	border-radius: 10px;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
	border: 1px solid rgba(255, 255, 255, 0.6);
}

.hotkey-controls {
	display: flex;
	align-items: center;
	gap: 8px;
}

.hotkey-label {
	font-size: 12px;
	font-weight: 500;
	color: #6b7280;
}
</style>
