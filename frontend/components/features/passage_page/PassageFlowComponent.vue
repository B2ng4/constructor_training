<template>
	<div ref="flowRef" class="passage-flow">
		<div v-if="selectedStep?.image_url" class="flow-inner">
			<!-- Скриншот: зум + пан как в редакторе; в режиме прохождения область не показываем -->
			<div
				ref="imageWrapRef"
				class="screenshot-wrap"
				:class="{
					'screenshot-wrap--clickable': isPassageMode && canClickToValidate,
					'screenshot-wrap--zoomed': zoom > 1,
					'screenshot-wrap--panning': isPanning,
				}"
				@wheel.prevent="onWheel"
				@mousedown="onWrapMouseDown"
				@click="onWrapClick"
				@dblclick="onWrapDblClick"
				@contextmenu.prevent="onWrapContextMenu"
				@mouseenter="onWrapMouseEnter"
				@mouseleave="onWrapMouseLeave"
				@mousemove="onWrapMouseMove"
			>
				<div
					class="screenshot-aspect"
					:style="screenshotAspectStyle"
				>
					<div
						ref="zoomPanRef"
						class="screenshot-zoom-pan"
						:style="zoomPanStyle"
					>
						<img
							ref="imgRef"
							:src="selectedStep.image_url"
							alt=""
							class="screenshot-img"
							draggable="false"
						/>
					<!-- Область действия: в прохождении подсвечиваем только через 10 сек без верного ответа -->
					<div
						v-if="showAreaVisible && area && (area.width > 0 && area.height > 0)"
						class="action-area"
						:class="areaClass"
						:style="areaStyle"
						@click.stop="onAreaClick"
						@dblclick.stop="onAreaDblClick"
						@contextmenu.prevent.stop="onAreaContextMenu"
						@mouseenter="onAreaMouseEnter"
						@mouseleave="onAreaMouseLeave"
					>
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

			<!-- Подсказка для keyPress (компактная, не на весь экран) -->
			<div v-if="needsKeyOverlay" class="keypress-hint-pill">
				<q-icon name="keyboard" size="18px" />
				<span>Нажмите: {{ hotkeyLabel }}</span>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import {
	eventRequiresArea,
	isKeyPressType,
	isInputTextType,
	isClickValidatedType,
} from "@utils/actionTypes.js";

const props = defineProps({
	selectedStep: { type: Object, default: null },
	mode: { type: String, default: "passage" }, // passage | edit
});

const emit = defineEmits(["action-complete", "action-wrong"]);

const flowRef = ref(null);
const imageWrapRef = ref(null);
const zoomPanRef = ref(null);
const imgRef = ref(null);
const inputRef = ref(null);
const inputValue = ref("");
const hoverTimer = ref(null);

/** Зум и пан как в редакторе (VueFlow) */
const zoom = ref(1);
const pan = ref({ x: 0, y: 0 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });
const panStartOffset = ref({ x: 0, y: 0 });
const didPanThisGesture = ref(false);
const panningWithMiddleButton = ref(false);

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 3;
const ZOOM_STEP = 0.12;

const zoomPanStyle = computed(() => ({
	transform: `translate(${pan.value.x}px, ${pan.value.y}px) scale(${zoom.value})`,
	transformOrigin: "center center",
}));

const area = computed(() => props.selectedStep?.area);
const actionType = computed(() => props.selectedStep?.action_type);

const isPassageMode = computed(() => props.mode === "passage");

/** В прохождении область показываем только через 10 сек без верного ответа */
const HINT_AREA_DELAY_MS = 10000;
const showAreaHintAfterDelay = ref(false);
let areaHintTimeoutId = null;

/** Реально показывать область: в режиме прохождения — только после задержки */
const showAreaVisible = computed(() => {
	if (!showAreaOnImage.value || !area.value) return false;
	if (!isPassageMode.value) return true;
	return showAreaHintAfterDelay.value;
});

/** В режиме прохождения показываем область для keyPress/inputText/hover; для кликов — проверяем по координатам без отображения области */
const showAreaOnImage = computed(() => {
	if (isPassageMode.value) {
		const at = actionType.value;
		const a = area.value;
		if (!at) return false;
		if (isKeyPressType(at) || isInputTextType(at)) return true;
		// hover: показываем область и проверяем по mouseenter/mouseleave на ней
		if (at.type === "hover" && a && a.width > 0 && a.height > 0) return true;
		return false;
	}
	const at = actionType.value;
	if (!at) return false;
	if (isKeyPressType(at)) return false;
	if (isInputTextType(at)) return true;
	return eventRequiresArea(at) && area.value;
});

/** Можно ли проверять клик по области (режим прохождения, есть область и тип клика/правый/двойной/hover) */
const canClickToValidate = computed(() => {
	if (!isPassageMode.value) return false;
	const at = actionType.value;
	const a = area.value;
	if (!at || !isClickValidatedType(at)) return false;
	if (isKeyPressType(at) || isInputTextType(at)) return false;
	if (!a || a.width <= 0 || a.height <= 0) return false;
	return true;
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

/** Обёртка с aspect-ratio под изображение, чтобы overlay с % совпадал с картинкой */
const screenshotAspectStyle = computed(() => {
	const step = props.selectedStep;
	const dims = step?.photo_dimensions ?? {};
	const w = dims.width || 1;
	const h = dims.height || 1;
	return {
		width: "100%",
		maxHeight: "100%",
		aspectRatio: `${w} / ${h}`,
	};
});

function onWheel(e) {
	const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
	const next = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, zoom.value + delta));
	if (next === zoom.value) return;
	const wrap = imageWrapRef.value;
	if (!wrap) return;
	const rect = wrap.getBoundingClientRect();
	const centerX = rect.width / 2;
	const centerY = rect.height / 2;
	const mouseX = e.clientX - rect.left;
	const mouseY = e.clientY - rect.top;
	const ratio = next / zoom.value;
	pan.value = {
		x: mouseX - centerX - (mouseX - centerX - pan.value.x) * ratio,
		y: mouseY - centerY - (mouseY - centerY - pan.value.y) * ratio,
	};
	zoom.value = next;
}

function onWrapMouseDown(e) {
	// Средняя кнопка мыши — пан в любой момент (как в редакторе)
	if (e.button === 1) {
		e.preventDefault();
		panningWithMiddleButton.value = true;
		isPanning.value = true;
		panStart.value = { x: e.clientX, y: e.clientY };
		panStartOffset.value = { ...pan.value };
		return;
	}
	// Левая кнопка — пан только при зуме > 1
	if (e.button !== 0) return;
	if (zoom.value <= 1) return;
	didPanThisGesture.value = false;
	panningWithMiddleButton.value = false;
	isPanning.value = true;
	panStart.value = { x: e.clientX, y: e.clientY };
	panStartOffset.value = { ...pan.value };
}

function onDocumentMouseMove(e) {
	if (!isPanning.value) return;
	if (!panningWithMiddleButton.value) didPanThisGesture.value = true;
	pan.value = {
		x: panStartOffset.value.x + (e.clientX - panStart.value.x),
		y: panStartOffset.value.y + (e.clientY - panStart.value.y),
	};
}

function onDocumentMouseUp() {
	isPanning.value = false;
	panningWithMiddleButton.value = false;
}

const isKeyPress = computed(() => isKeyPressType(actionType.value));
const isInputText = computed(() => isInputTextType(actionType.value));

const hotkeyLabel = computed(() => {
	const kw = area.value?.metaKeywords;
	if (!kw || !kw.length) return "—";
	return kw.join(" + ");
});

/** Клик в координаты изображения: используем rect самого img (уже с учётом зума/пана) */
function getClickInImageCoords(e) {
	const img = imgRef.value;
	const step = props.selectedStep;
	if (!img || !step?.photo_dimensions || !area.value) return null;
	const rect = img.getBoundingClientRect();
	const dims = step.photo_dimensions;
	const w = dims.width || 1;
	const h = dims.height || 1;
	const x = e.clientX - rect.left;
	const y = e.clientY - rect.top;
	if (x < 0 || y < 0 || x > rect.width || y > rect.height) return null;
	return {
		x: (x / rect.width) * w,
		y: (y / rect.height) * h,
	};
}

function isPointInArea(px, py) {
	const a = area.value;
	if (!a) return false;
	return px >= a.x && px <= a.x + a.width && py >= a.y && py <= a.y + a.height;
}

function onWrapClick(e) {
	if (didPanThisGesture.value) {
		didPanThisGesture.value = false;
		return;
	}
	if (!canClickToValidate.value) return;
	if (!isClickValidatedType(actionType.value)) return;
	// Обрабатываем только левый клик; при doubleClick первый клик не считаем ошибкой
	if (actionType.value?.type !== "leftClick") return;
	const coords = getClickInImageCoords(e);
	if (!coords) return;
	if (isPointInArea(coords.x, coords.y)) {
		e.preventDefault();
		emit("action-complete");
	} else {
		emit("action-wrong");
	}
}

function onWrapContextMenu(e) {
	if (didPanThisGesture.value) {
		didPanThisGesture.value = false;
		return;
	}
	if (!canClickToValidate.value) return;
	if (actionType.value?.type !== "rightClick") return;
	const coords = getClickInImageCoords(e);
	if (!coords) return;
	if (isPointInArea(coords.x, coords.y)) {
		e.preventDefault();
		emit("action-complete");
	} else {
		emit("action-wrong");
	}
}

function onWrapDblClick(e) {
	if (didPanThisGesture.value) {
		didPanThisGesture.value = false;
		return;
	}
	if (!canClickToValidate.value) return;
	if (actionType.value?.type !== "doubleClick") return;
	const coords = getClickInImageCoords(e);
	if (!coords) return;
	if (isPointInArea(coords.x, coords.y)) {
		e.preventDefault();
		emit("action-complete");
	} else {
		emit("action-wrong");
	}
}

/** Hover при прохождении: когда область не показана, проверяем по координатам на mousemove */
function onWrapMouseMove(e) {
	if (!isPassageMode.value || actionType.value?.type !== "hover" || showAreaVisible.value) return;
	if (!canClickToValidate.value || !area.value) return;
	const coords = getClickInImageCoords(e);
	if (coords && isPointInArea(coords.x, coords.y)) {
		if (!hoverTimer.value) {
			hoverTimer.value = setTimeout(() => {
				hoverTimer.value = null;
				emit("action-complete");
			}, 800);
		}
	} else {
		if (hoverTimer.value) {
			clearTimeout(hoverTimer.value);
			hoverTimer.value = null;
		}
	}
}

function onWrapMouseEnter() {
	// hover при прохождении: если область уже показана — проверяем по ней (onAreaMouseEnter)
	if (isPassageMode.value && actionType.value?.type === "hover" && showAreaVisible.value) return;
	if (!canClickToValidate.value || actionType.value?.type !== "hover") return;
	hoverTimer.value = setTimeout(() => {
		hoverTimer.value = null;
		emit("action-complete");
	}, 800);
}

function onWrapMouseLeave() {
	if (isPassageMode.value && actionType.value?.type === "hover" && showAreaVisible.value) return;
	if (hoverTimer.value) {
		clearTimeout(hoverTimer.value);
		hoverTimer.value = null;
	}
}

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
	// Не перехватывать, если фокус в поле ввода
	const tag = e.target?.tagName?.toUpperCase();
	if (tag === "INPUT" || tag === "TEXTAREA") return;

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
		zoom.value = 1;
		pan.value = { x: 0, y: 0 };
		showAreaHintAfterDelay.value = false;
		if (areaHintTimeoutId) {
			clearTimeout(areaHintTimeoutId);
			areaHintTimeoutId = null;
		}
		if (isPassageMode.value) {
			areaHintTimeoutId = setTimeout(() => {
				areaHintTimeoutId = null;
				if (hoverTimer.value) {
					clearTimeout(hoverTimer.value);
					hoverTimer.value = null;
				}
				showAreaHintAfterDelay.value = true;
			}, HINT_AREA_DELAY_MS);
		}
	},
	{ immediate: true }
);

onMounted(() => {
	document.addEventListener("mousemove", onDocumentMouseMove);
	document.addEventListener("mouseup", onDocumentMouseUp);
	document.addEventListener("keydown", onKeyDown);
});

onUnmounted(() => {
	document.removeEventListener("mousemove", onDocumentMouseMove);
	document.removeEventListener("mouseup", onDocumentMouseUp);
	document.removeEventListener("keydown", onKeyDown);
	if (hoverTimer.value) clearTimeout(hoverTimer.value);
	if (areaHintTimeoutId) clearTimeout(areaHintTimeoutId);
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
	background: #f0f1f5;
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
	background-color: #f0f1f5;
	overflow: hidden;
	display: flex;
	align-items: center;
	justify-content: center;
}

.screenshot-aspect {
	position: relative;
	width: 100%;
	height: 100%;
	max-width: 100%;
	max-height: 100%;
}

.screenshot-wrap--clickable {
	cursor: pointer;
}

.screenshot-wrap--zoomed {
	cursor: grab;
}

.screenshot-wrap--zoomed.screenshot-wrap--panning,
.screenshot-wrap--panning {
	cursor: grabbing;
}

.screenshot-zoom-pan {
	position: absolute;
	inset: 0;
	width: 100%;
	height: 100%;
	will-change: transform;
	display: flex;
	align-items: center;
	justify-content: center;
}

.screenshot-img {
	display: block;
	width: 100%;
	height: 100%;
	object-fit: contain;
	object-position: center;
	pointer-events: none;
	user-select: none;
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

.keypress-hint-pill {
	position: absolute;
	bottom: 80px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 10;
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 18px;
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: blur(12px);
	border-radius: 12px;
	box-shadow: 0 2px 16px rgba(0, 0, 0, 0.12);
	font-size: 14px;
	font-weight: 600;
	color: #334155;
	border: 1px solid rgba(0, 0, 0, 0.06);
}

.keypress-hint-pill .q-icon {
	color: var(--q-primary);
}
</style>
