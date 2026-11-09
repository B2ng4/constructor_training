<template>
	<div
		ref="containerRef"
		class="screenshot-node"
		:style="nodeStyle"
	>
		<!-- Кликабельные области, найденные YOLO-детектором -->
		<template v-if="boxesVisible">
			<div
				v-for="(det, i) in uiDetections"
				:key="i"
				class="det-box"
				:style="detBoxStyle(det)"
				@mousedown.stop.prevent="onDetectionSelect(det)"
			>
				<span class="det-box__label">{{ det.class_ru }}</span>
			</div>
		</template>

		<!-- Область для рисования (прозрачный оверлей) -->
		<div
			v-if="drawingEnabled"
			class="draw-overlay"
			@mousedown="onMouseDown"
			@mousemove="onMouseMove"
			@mouseup="onMouseUp"
			@mouseleave="onMouseLeave"
		>
			<!-- Превью прямоугольника при рисовании -->
			<div
				v-if="isDrawing"
				class="draw-preview"
				:style="previewStyle"
			/>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, inject } from "vue";
import { useVueFlow } from "@vue-flow/core";
import { useTrainingData } from "@store/editTraining.js";
import { eventRequiresArea } from "@utils/actionTypes.js";
import { findToolbarEventById } from "@utils/stepActionSequence.js";

const props = defineProps({
	id: { type: String, default: '' },
	type: { type: String, default: '' },
	data: { type: Object, default: () => ({}) },
	position: { type: Object, default: () => ({ x: 0, y: 0 }) },
	dimensions: { type: Object, default: () => ({ width: 0, height: 0 }) },
});

const vueFlow = useVueFlow();
const project = vueFlow?.screenToFlowCoordinate ?? vueFlow?.project;

const containerRef = ref(null);
const isDrawing = ref(false);
const startX = ref(0);
const startY = ref(0);
const currentX = ref(0);
const currentY = ref(0);

const onAreaDrawn = inject("onAreaDrawn", null);
const drawingEnabledRef = inject("drawingEnabled", ref(false));
const setIsCurrentlyDrawing = inject("setIsCurrentlyDrawing", () => {});

const drawingEnabled = computed(() =>
	typeof drawingEnabledRef === "object" && drawingEnabledRef?.value !== undefined
		? drawingEnabledRef.value
		: !!drawingEnabledRef
);

const store = useTrainingData();

/** Детекции UI-элементов (YOLO) в пикселях исходного скриншота */
const uiDetections = computed(() => {
	const list = store.selectedStep?.meta?.ui_detections;
	return Array.isArray(list) ? list : [];
});

/**
 * Боксы видны всегда, пока выбранное действие не исключает область
 * (для «Нажатие клавиши» и т.п. область не нужна — боксы прячем).
 */
const boxesVisible = computed(() => {
	if (!uiDetections.value.length) return false;
	const ev = store.selectedEvent;
	if (!ev) return true;
	return eventRequiresArea(ev);
});

function detBoxStyle(det) {
	return {
		left: `${Number(det.x) || 0}px`,
		top: `${Number(det.y) || 0}px`,
		width: `${Math.max(4, Number(det.width) || 0)}px`,
		height: `${Math.max(4, Number(det.height) || 0)}px`,
	};
}

function onDetectionSelect(det) {
	if (!onAreaDrawn) return;
	// Если действие не выбрано — подставляем «Левый клик», клик по боксу сразу назначает область.
	if (!drawingEnabled.value) {
		const ev = store.selectedEvent;
		if (ev && !eventRequiresArea(ev)) return;
		store.selectEvent({ ...findToolbarEventById(1) });
	}
	const x = Math.round(Number(det.x) || 0);
	const y = Math.round(Number(det.y) || 0);
	const w = Math.round(Number(det.width) || 0);
	const h = Math.round(Number(det.height) || 0);
	if (w < 2 || h < 2) return;
	onAreaDrawn({ x, y, width: w, height: h });
}

function getImageNode() {
	return vueFlow.findNode?.('fullscreen-image') ?? null;
}

const nodeStyle = computed(() => {
	const imageNode = getImageNode();
	const dims = imageNode?.dimensions ?? props.dimensions;
	const style = imageNode?.style || {};
	const w = dims?.width ?? 0;
	const h = dims?.height ?? 0;
	return {
		backgroundImage: style.backgroundImage || "none",
		backgroundSize: style.backgroundSize || "contain",
		backgroundRepeat: style.backgroundRepeat || "no-repeat",
		width: `${w}px`,
		height: `${h}px`,
	};
});

const previewStyle = computed(() => {
	const x = Math.min(startX.value, currentX.value);
	const y = Math.min(startY.value, currentY.value);
	const w = Math.abs(currentX.value - startX.value);
	const h = Math.abs(currentY.value - startY.value);
	return {
		left: `${x}px`,
		top: `${y}px`,
		width: `${Math.max(w, 2)}px`,
		height: `${Math.max(h, 2)}px`,
	};
});

function getRelativeCoords(e) {
	const imageNode = getImageNode();
	const nodePos = (imageNode?.computedPosition ?? imageNode?.position) ?? { x: 0, y: 0 };

	if (project) {
		const flowPoint = project({ x: e.clientX, y: e.clientY });
		return {
			x: flowPoint.x - nodePos.x,
			y: flowPoint.y - nodePos.y,
		};
	}

	// fallback: getBoundingClientRect
	const el = containerRef.value;
	if (!el) return { x: 0, y: 0 };
	const rect = el.getBoundingClientRect();
	const dims = imageNode?.dimensions ?? {};
	const imgW = dims.width || rect.width;
	const imgH = dims.height || rect.height;
	const scaleX = imgW / rect.width;
	const scaleY = imgH / rect.height;
	return {
		x: (e.clientX - rect.left) * scaleX,
		y: (e.clientY - rect.top) * scaleY,
	};
}

function onMouseDown(e) {
	if (!onAreaDrawn || !drawingEnabled.value) return;
	e.preventDefault();
	isDrawing.value = true;
	setIsCurrentlyDrawing(true);
	const { x, y } = getRelativeCoords(e);
	startX.value = x;
	startY.value = y;
	currentX.value = x;
	currentY.value = y;
}

function onMouseMove(e) {
	if (!isDrawing.value) return;
	const { x, y } = getRelativeCoords(e);
	currentX.value = x;
	currentY.value = y;
}

function onMouseUp(e) {
	if (!isDrawing.value) return;
	isDrawing.value = false;
	setIsCurrentlyDrawing(false);
	const { x, y } = getRelativeCoords(e);
	currentX.value = x;
	currentY.value = y;

	const x1 = Math.min(startX.value, currentX.value);
	const y1 = Math.min(startY.value, currentY.value);
	const w = Math.abs(currentX.value - startX.value);
	const h = Math.abs(currentY.value - startY.value);

	const MIN = 6;
	if (w < MIN || h < MIN) return;

	onAreaDrawn({ x: Math.round(x1), y: Math.round(y1), width: Math.round(w), height: Math.round(h) });
}

function onMouseLeave() {
	if (isDrawing.value) {
		isDrawing.value = false;
		setIsCurrentlyDrawing(false);
	}
}
</script>

<style scoped>
.screenshot-node {
	position: relative;
	border: none;
	background-color: transparent;
}

.draw-overlay {
	position: absolute;
	inset: 0;
	cursor: crosshair;
	z-index: 1;
	/* обёртка .vue-flow__node имеет pointer-events: none для non-selectable нод */
	pointer-events: auto;
}

.draw-preview {
	position: absolute;
	border: 2px solid var(--q-primary);
	background: rgba(80, 100, 247, 0.15);
	pointer-events: none;
}

.det-box {
	position: absolute;
	border: 1.5px dashed rgba(34, 197, 94, 0.85);
	background: rgba(34, 197, 94, 0.06);
	cursor: pointer;
	z-index: 2;
	pointer-events: auto;
	transition: background-color 0.12s ease, border-color 0.12s ease;
}

.det-box:hover {
	background: rgba(34, 197, 94, 0.22);
	border-style: solid;
	border-color: rgb(22, 163, 74);
}

.det-box__label {
	position: absolute;
	top: -18px;
	left: -1px;
	padding: 0 4px;
	font-size: 11px;
	line-height: 16px;
	color: #fff;
	background: rgba(22, 163, 74, 0.9);
	border-radius: 3px;
	white-space: nowrap;
	opacity: 0;
	transition: opacity 0.12s ease;
	pointer-events: none;
}

.det-box:hover .det-box__label {
	opacity: 1;
}
</style>
