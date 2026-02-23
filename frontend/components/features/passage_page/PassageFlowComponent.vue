<template>
	<div ref="flowRef" class="passage-flow">
		<div v-if="selectedStep?.image_url" class="flow-inner">
			<!-- Скриншот -->
			<div
				ref="imageWrapRef"
				class="screenshot-wrap"
				:style="screenshotStyle"
			>
				<!-- Область действия (кликабельная/хайлайт), не для keyPress -->
				<div
					v-if="showAreaOnImage && area && (area.width > 0 && area.height > 0)"
					class="action-area"
					:class="areaClass"
					:style="areaStyle"
					@click="onAreaClick"
					@dblclick="onAreaDblClick"
					@contextmenu.prevent="onAreaContextMenu"
					@mouseenter="onAreaMouseEnter"
					@mouseleave="onAreaMouseLeave"
				>
					<!-- Подсказка для keyPress / inputText -->
					<div v-if="isKeyPress" class="area-hint">
						<q-icon name="keyboard" size="20px" />
						<span>Нажмите: {{ hotkeyLabel }}</span>
					</div>
					<div v-else-if="isInputText" class="area-hint">
						<q-icon name="edit" size="20px" />
						<span>Введите текст ниже</span>
					</div>
				</div>
			</div>

			<!-- Поле ввода для inputText -->
			<div v-if="isInputText && area" class="input-text-panel">
				<q-input
					ref="inputRef"
					v-model="inputValue"
					outlined
					dense
					placeholder="Введите текст сюда"
					class="input-field"
					@keyup.enter="checkInputText"
				>
					<template #append>
						<q-btn
							flat
							dense
							round
							icon="check"
							color="primary"
							@click="checkInputText"
						/>
					</template>
				</q-input>
			</div>

			<!-- Оверлей ожидания keyPress -->
			<div
				v-if="needsKeyOverlay"
				class="keypress-overlay"
				@keydown="onKeyDown"
				tabindex="0"
				ref="keyOverlayRef"
			>
				<div class="keypress-hint">
					<q-icon name="keyboard" size="32px" />
					<span>Нажмите: {{ hotkeyLabel }}</span>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";

const props = defineProps({
	selectedStep: { type: Object, default: null },
	mode: { type: String, default: "passage" }, // passage | edit
});

const emit = defineEmits(["action-complete", "action-wrong"]);

const flowRef = ref(null);
const imageWrapRef = ref(null);
const inputRef = ref(null);
const keyOverlayRef = ref(null);
const inputValue = ref("");
const hoverTimer = ref(null);

const eventRequiresArea = (event) => event?.type !== "keyPress";

const area = computed(() => props.selectedStep?.area);
const actionType = computed(() => props.selectedStep?.action_type);

const showAreaOnImage = computed(() => {
	const at = actionType.value;
	if (!at) return false;
	if (at.type === "keyPress") return false; // keyPress — оверлей, не на изображении
	if (at.type === "inputText") return true;
	return eventRequiresArea(at) && area.value;
});

const needsKeyOverlay = computed(() => isKeyPress.value && area.value?.metaKeywords?.length > 0);

const areaStyle = computed(() => {
	const a = area.value;
	const step = props.selectedStep;
	if (!a || !a.width || !a.height || !step) return {};
	const dims = step.photo_dimensions ?? {};
	const imgW = dims.width || 1;
	const imgH = dims.height || 1;
	return {
		left: `${(a.x / imgW) * 100}%`,
		top: `${(a.y / imgH) * 100}%`,
		width: `${(a.width / imgW) * 100}%`,
		height: `${(a.height / imgH) * 100}%`,
	};
});

const areaClass = computed(() => {
	const at = actionType.value;
	if (!at) return "";
	return `action-${at.type}`;
});

const screenshotStyle = computed(() => {
	const step = props.selectedStep;
	if (!step?.image_url) return {};
	return {
		backgroundImage: `url(${step.image_url})`,
		backgroundSize: "contain",
		backgroundPosition: "center",
		backgroundRepeat: "no-repeat",
	};
});

const isKeyPress = computed(() => actionType.value?.type === "keyPress");
const isInputText = computed(() => actionType.value?.type === "inputText");

const hotkeyLabel = computed(() => {
	const kw = area.value?.metaKeywords;
	if (!kw || !kw.length) return "—";
	return kw.join(" + ");
});

function onAreaClick(e) {
	if (actionType.value?.type === "leftClick") {
		e.preventDefault();
		emit("action-complete");
	}
}

function onAreaDblClick(e) {
	if (actionType.value?.type === "doubleClick") {
		e.preventDefault();
		emit("action-complete");
	}
}

function onAreaContextMenu(e) {
	if (actionType.value?.type === "rightClick") {
		e.preventDefault();
		emit("action-complete");
	}
}

function onAreaMouseEnter() {
	if (actionType.value?.type !== "hover") return;
	hoverTimer.value = setTimeout(() => {
		hoverTimer.value = null;
		emit("action-complete");
	}, 800);
}

function onAreaMouseLeave() {
	if (hoverTimer.value) {
		clearTimeout(hoverTimer.value);
		hoverTimer.value = null;
	}
}

function checkInputText() {
	const expected = area.value?.metaText?.trim() || "";
	const actual = inputValue.value.trim();
	if (actual === expected) {
		inputValue.value = "";
		emit("action-complete");
	} else if (actual && expected) {
		emit("action-wrong");
	}
}

const KEY_ALIASES = { control: "ctrl", " ": "space" };

function normalizeKey(k) {
	const s = String(k).toLowerCase();
	return KEY_ALIASES[s] ?? s;
}

function onKeyDown(e) {
	if (!isKeyPress.value) return;
	const kw = area.value?.metaKeywords || [];
	if (!kw.length) return;

	const key = e.key ?? "";
	const ctrl = e.ctrlKey;
	const alt = e.altKey;
	const shift = e.shiftKey;
	const meta = e.metaKey;

	const parts = [];
	if (ctrl) parts.push("ctrl");
	if (alt) parts.push("alt");
	if (shift) parts.push("shift");
	if (meta) parts.push("meta");
	parts.push(normalizeKey(key));

	const pressed = parts.filter(Boolean).map(normalizeKey).join(" + ");
	const expected = kw.map(normalizeKey).join(" + ");

	if (pressed === expected) {
		e.preventDefault();
		emit("action-complete");
	}
}

watch(
	() => props.selectedStep?.id,
	() => {
		inputValue.value = "";
		setTimeout(() => {
			if (needsKeyOverlay.value && keyOverlayRef.value) {
				keyOverlayRef.value.focus();
			}
		}, 100);
	},
	{ immediate: true }
);

onMounted(() => {
	if (needsKeyOverlay.value && keyOverlayRef.value) {
		setTimeout(() => keyOverlayRef.value?.focus(), 150);
	}
});

onUnmounted(() => {
	if (hoverTimer.value) clearTimeout(hoverTimer.value);
});
</script>

<style scoped>
.passage-flow {
	width: 100%;
	height: 100%;
	overflow: hidden;
	display: flex;
	align-items: stretch;
	justify-content: stretch;
	background: #1a1a1a;
}

.flow-inner {
	position: relative;
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: stretch;
	min-width: 0;
	min-height: 0;
}

.screenshot-wrap {
	position: relative;
	flex: 1;
	min-height: 0;
	background-color: #1a1a1a;
}

.action-area {
	position: absolute;
	cursor: pointer;
	border: 2px solid rgba(80, 100, 247, 0.6);
	background: rgba(80, 100, 247, 0.15);
	border-radius: 6px;
	transition: background 0.2s, border-color 0.2s;
	display: flex;
	align-items: center;
	justify-content: center;
}

.action-area:hover {
	background: rgba(80, 100, 247, 0.25);
	border-color: var(--q-primary);
}

.action-area.action-hover {
	cursor: default;
}

.action-area .area-hint {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 13px;
	font-weight: 500;
	color: var(--q-primary);
	pointer-events: none;
}

.input-text-panel {
	flex-shrink: 0;
	width: 100%;
	max-width: 400px;
	padding: 0 16px 16px;
}

.input-field {
	background: white;
	border-radius: 12px;
}

.keypress-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.4);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 100;
	outline: none;
}

.keypress-overlay:focus {
	outline: none;
}

.keypress-hint {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 12px;
	padding: 24px 32px;
	background: white;
	border-radius: 16px;
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	font-size: 16px;
	font-weight: 600;
	color: #334155;
}
</style>
