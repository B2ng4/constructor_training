<template>
	<div
		ref="containerRef"
		class="screenshot-node"
		:style="nodeStyle"
	>
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

const drawingEnabled = computed(() =>
	typeof drawingEnabledRef === "object" && drawingEnabledRef?.value !== undefined
		? drawingEnabledRef.value
		: !!drawingEnabledRef
);

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
	const { x, y } = getRelativeCoords(e);
	currentX.value = x;
	currentY.value = y;

	const x1 = Math.min(startX.value, currentX.value);
	const y1 = Math.min(startY.value, currentY.value);
	const w = Math.abs(currentX.value - startX.value);
	const h = Math.abs(currentY.value - startY.value);

	if (w < 20 || h < 20) return;

	onAreaDrawn({ x: Math.round(x1), y: Math.round(y1), width: Math.round(w), height: Math.round(h) });
}

function onMouseLeave() {
	if (isDrawing.value) {
		isDrawing.value = false;
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
}

.draw-preview {
	position: absolute;
	border: 2px solid var(--q-primary);
	background: rgba(80, 100, 247, 0.15);
	pointer-events: none;
}
</style>
