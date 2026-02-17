<template>
	<div class="tool-bar-container">
		<!-- Предыдущий шаг -->
		<q-btn
			v-if="hasPreviousStep"
			class="nav-btn"
			round
			dense
			icon="chevron_left"
			color="white"
			text-color="grey-9"
			@click="goToPreviousStep"
		>
			<q-tooltip>Предыдущий шаг</q-tooltip>
		</q-btn>

		<!-- Тулбар -->
		<div class="tool-bar">
			<q-btn
				v-for="event in events"
				:key="event.id"
				dense
				flat
				class="tool-btn"
				:class="{ 'tool-btn-active': store.selectedEvent?.id === event.id }"
				@click="selectEvent(event)"
			>
				<div class="tool-btn-inner">
					<Component :is="event.icon" />
					<span class="tool-btn-label">{{ event.shortName }}</span>
				</div>
				<q-tooltip class="bg-grey-9 text-body2">{{ event.name }}</q-tooltip>
			</q-btn>
		</div>

		<!-- Панель хоткея -->
		<transition name="panel-slide">
			<div v-if="isKeyPressSelected" class="hotkey-panel">
				<div class="hotkey-panel-label">{{ hotkeyLabel }}</div>
				<q-btn
					dense
					no-caps
					unelevated
					color="primary"
					size="sm"
					label="Выбрать"
					@click="openHotkeyDialog"
				/>
			</div>
		</transition>

		<!-- Следующий шаг -->
		<q-btn
			v-if="hasNextStep"
			class="nav-btn"
			round
			dense
			icon="chevron_right"
			color="white"
			text-color="grey-9"
			@click="goToNextStep"
		>
			<q-tooltip>Следующий шаг</q-tooltip>
		</q-btn>

		<watch-key
			v-if="isKeyPressSelected"
			v-model="metaKeywords"
			v-model:open="isHotkeyDialogOpen"
		/>
	</div>
</template>

<script setup>
import {
	RightClick,
	LeftClick,
	DoubleClick,
	Text,
	Mouseover,
	Keyboard,
} from "@components/features/edit_page/icons_tool_bar/index.js";
import WatchKey from "@components/features/edit_page/WatchKey.vue";
import { trainingStepApi } from "@api";
import { useTrainingData } from "@store/editTraining.js";
import { computed, ref, watch } from "vue";

const store = useTrainingData();
const isHotkeyDialogOpen = ref(false);

const hasPreviousStep = computed(() => {
	if (!store.trainingData?.steps) return false;
	const idx = store.trainingData.steps.findIndex(s => s.id === store.selectedStep?.id);
	return idx > 0;
});

const hasNextStep = computed(() => {
	if (!store.trainingData?.steps) return false;
	const idx = store.trainingData.steps.findIndex(s => s.id === store.selectedStep?.id);
	return idx >= 0 && idx < store.trainingData.steps.length - 1;
});

const goToPreviousStep = () => {
	if (!store.trainingData?.steps) return;
	const idx = store.trainingData.steps.findIndex(s => s.id === store.selectedStep?.id);
	if (idx > 0) store.selectStep(store.trainingData.steps[idx - 1]);
};

const goToNextStep = () => {
	if (!store.trainingData?.steps) return;
	const idx = store.trainingData.steps.findIndex(s => s.id === store.selectedStep?.id);
	if (idx < store.trainingData.steps.length - 1) store.selectStep(store.trainingData.steps[idx + 1]);
};

const isKeyPressSelected = computed(() => store.selectedEvent?.type === "keyPress");

const metaKeywords = computed({
	get() { return store.selectedStep?.area?.metaKeywords || []; },
	set(value) {
		if (!store.selectedStep) return;
		if (!store.selectedStep.area) store.selectedStep.area = {};
		store.selectedStep.area.metaKeywords = value;
	}
});

const hotkeyLabel = computed(() =>
	metaKeywords.value?.length ? metaKeywords.value.join(' + ') : "Не назначено"
);

const saveKeyPress = async () => {
	if (!store.trainingData?.uuid || !store.selectedStep?.id || !store.selectedEvent?.id) return;
	try {
		await trainingStepApi.editStep(
			store.trainingData.uuid,
			store.selectedStep.id,
			{
				action_type_id: store.selectedEvent.id,
				area: { ...(store.selectedStep.area || {}), metaKeywords: metaKeywords.value || [] }
			}
		);
	} catch (e) {
		console.error(e);
	}
};

const openHotkeyDialog = () => { isHotkeyDialogOpen.value = true; };

const selectEvent = async (event) => {
	store.selectEvent(event);
	if (event.type === "keyPress") {
		await saveKeyPress();
		openHotkeyDialog();
	}
};

watch(
	() => isHotkeyDialogOpen.value,
	async (isOpen) => {
		if (!isOpen && isKeyPressSelected.value) await saveKeyPress();
	}
);

const events = [
	{ type: "leftClick",  name: "Левый клик",       shortName: "ЛКМ",     icon: LeftClick,   id: 1 },
	{ type: "rightClick", name: "Правый клик",      shortName: "ПКМ",     icon: RightClick,  id: 2 },
	{ type: "doubleClick",name: "Двойной клик",     shortName: "2x клик", icon: DoubleClick, id: 3 },
	{ type: "hover",      name: "Наведение курсора",shortName: "Hover",   icon: Mouseover,   id: 4 },
	{ type: "inputText",  name: "Ввод текста",      shortName: "Текст",   icon: Text,        id: 5 },
	{ type: "keyPress",   name: "Нажатие клавиши",  shortName: "Клавиша", icon: Keyboard,    id: 6 },
];
</script>

<style scoped>
.tool-bar-container {
	position: absolute;
	z-index: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 12px;
	width: 100%;
	left: 0;
	bottom: 24px;
	pointer-events: none;
}

.tool-bar-container > * {
	pointer-events: auto;
}

.tool-bar {
	display: flex;
	gap: 2px;
	background: rgba(255, 255, 255, 0.85);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	padding: 6px;
	border-radius: 16px;
	box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1), 0 1px 4px rgba(0, 0, 0, 0.06);
	border: 1px solid rgba(255, 255, 255, 0.6);
}

.tool-btn {
	border-radius: 12px;
	padding: 6px 10px;
	transition: all 0.2s ease;
	min-width: 56px;
}

.tool-btn:hover {
	background: rgba(80, 100, 247, 0.08);
}

.tool-btn-active {
	background: var(--q-primary) !important;
	color: white !important;
	box-shadow: 0 2px 8px rgba(80, 100, 247, 0.3);
}

.tool-btn-active:hover {
	background: var(--q-primary) !important;
}

.tool-btn-inner {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 2px;
}

.tool-btn-label {
	font-size: 10px;
	font-weight: 500;
	line-height: 1;
	opacity: 0.8;
}

.tool-btn-active .tool-btn-label {
	opacity: 1;
}

.hotkey-panel {
	display: flex;
	align-items: center;
	gap: 10px;
	background: rgba(255, 255, 255, 0.85);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	padding: 8px 14px;
	border-radius: 12px;
	box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
	border: 1px solid rgba(255, 255, 255, 0.6);
}

.hotkey-panel-label {
	font-size: 13px;
	font-weight: 500;
	color: #374151;
}

.nav-btn {
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
	border: 1px solid rgba(0, 0, 0, 0.06);
}

.panel-slide-enter-active,
.panel-slide-leave-active {
	transition: opacity 0.2s ease, transform 0.2s ease;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
	opacity: 0;
	transform: translateY(8px);
}
</style>
