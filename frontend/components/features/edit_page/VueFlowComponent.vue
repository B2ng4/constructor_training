<template>
	<div ref="flowContainerRef" class="fullscreen-flow">
		<div v-if="showViewportHint" class="viewport-hint" role="note" @click.stop>
			<q-icon name="open_with" size="18px" />
			<span>Масштаб: колесо мыши. Перемещение: зажмите среднюю кнопку.</span>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="close"
				color="white"
				@click="dismissViewportHint"
			/>
		</div>
		<VueFlow v-model="nodes" :default-viewport="{ zoom: 0.7 }" :node-types="nodeTypes" @node-drag-stop="onNodeDragStop">
			<template #node-screenshot>
				<ScreenshotNode />
			</template>
			<template #node-resizable="resizableNodeProps">
				<ResizableNode :node="resizableNodeProps" />
			</template>
		</VueFlow>
	</div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed, provide, nextTick } from "vue";
import { VueFlow, Position } from "@vue-flow/core";
import { eventRequiresArea } from "@utils/actionTypes.js";
import { useTrainingData } from "@store/editTraining.js";
import ResizableNode from "./ResizableNode.vue";
import ScreenshotNode from "./ScreenshotNode.vue";

const store = useTrainingData();
const nodes = ref([]);
const flowContainerRef = ref(null);
const nodeTypes = { screenshot: ScreenshotNode };
const DEFAULT_ZOOM = 0.7;
const showViewportHint = ref(true);

const eventRequiresAreaOpt = (event) => eventRequiresArea(event);

const drawingEnabled = computed(() => {
	return !!store.selectedEvent && eventRequiresAreaOpt(store.selectedEvent);
});

const hasDrawnHint = () => !!store.selectedStep?.area;

const lastDrawnArea = ref(null);

const onAreaDrawn = (area) => {
	const event = store.selectedEvent;
	if (!event) return;
	lastDrawnArea.value = { x: area.x, y: area.y, width: area.width, height: area.height };
	createNode(event, area.width, area.height, area.x, area.y);
};

const onNodeDragStop = () => {
	lastDrawnArea.value = null;
};

provide("onAreaDrawn", onAreaDrawn);
provide("drawingEnabled", drawingEnabled);
provide("hasDrawnHint", hasDrawnHint);
provide("getAreaForSave", () => {
	if (nodes.value.length < 2) return null;
	const imageNode = nodes.value[0];
	const eventNode = nodes.value[1];
	const imgPos = imageNode.computedPosition ?? imageNode.position ?? { x: 0, y: 0 };
	const evtPos = eventNode.computedPosition ?? eventNode.position ?? { x: 0, y: 0 };
	const relX = evtPos.x - imgPos.x;
	const relY = evtPos.y - imgPos.y;
	const dims = eventNode.dimensions ?? {};
	let w = dims.width ?? 0;
	let h = dims.height ?? 0;
	if (!w || !h) {
		const style = eventNode.style || {};
		if (typeof style.width === "string") w = parseInt(style.width, 10) || w;
		if (typeof style.height === "string") h = parseInt(style.height, 10) || h;
	}
	let width = Math.round(w) || 0;
	let height = Math.round(h) || 0;

	if (lastDrawnArea.value) {
		const drawn = lastDrawnArea.value;
		const dimsMatch = Math.abs((dims.width || 0) - drawn.width) < 2 && Math.abs((dims.height || 0) - drawn.height) < 2;
		if (dimsMatch) {
			return {
				x: drawn.x,
				y: drawn.y,
				width: drawn.width,
				height: drawn.height,
			};
		}
	}

	if (!width || !height) return null;
	return {
		x: Math.max(0, Math.round(relX)),
		y: Math.max(0, Math.round(relY)),
		width,
		height,
	};
});

const clearEventNode = () => {
	if (nodes.value.length > 0) {
		nodes.value = [nodes.value[0]];
	}
	lastDrawnArea.value = null;
};

const createFullscreenNode = async () => {
	const { width: imgWidth, height: imgHeight } = store.selectedStep.photo_dimensions;
	const el = flowContainerRef.value;
	const canvasWidth = el ? el.clientWidth : window.innerWidth;
	const canvasHeight = el ? el.clientHeight : window.innerHeight;
	const viewFlowW = canvasWidth / DEFAULT_ZOOM;
	const viewFlowH = canvasHeight / DEFAULT_ZOOM;
	const x = (viewFlowW - imgWidth) / 2;
	const y = (viewFlowH - imgHeight) / 2;

	nodes.value[0] = {
		id: "fullscreen-image",
		type: "screenshot",
		position: { x, y },
		style: {
			backgroundImage: `url(${store.selectedStep.image_url})`,
			backgroundSize: "contain",
			backgroundRepeat: "no-repeat",
			width: `${imgWidth}px`,
			height: `${imgHeight}px`,
		},
		dimensions: {
			width: imgWidth,
			height: imgHeight,
		},
		connectable: false,
		data: { label: "" },
		class: "fullscreen-node",
		draggable: false,
		selectable: false,
	};

	/* Не трогаем selectedEvent здесь: иначе при смене действия в тулбаре watch пересобирает сцену
	   и снова подставляет action_type с сервера, сбрасывая выбор пользователя. */
};

const createNode = (
	event,
	width = 200,
	height = 200,
	relativeX = 0,
	relativeY = 0,
) => {
	const imageNode = nodes.value[0];

	if (!imageNode) {
		return;
	}

	const maxX = imageNode.dimensions.width - width;
	const maxY = imageNode.dimensions.height - height;

	const clampedX = Math.max(0, Math.min(relativeX, maxX));
	const clampedY = Math.max(0, Math.min(relativeY, maxY));

	const finalAbsoluteX = imageNode.position.x + clampedX;
	const finalAbsoluteY = imageNode.position.y + clampedY;

	const nodeData = {
		id: `event-${event.id}`,
		type: "resizable",
		draggable: true,
		data: {
			label: event.name,
			type: event.type,
			toolbarPosition: Position.Top,
			toolbarVisible: true,
		},
		dimensions: {
			width: Math.round(width),
			height: Math.round(height),
		},
		position: {
			x: finalAbsoluteX,
			y: finalAbsoluteY
		},
		style: {
			border: "2px solid var(--q-primary)",
			borderRadius: "4px",
			background: "rgba(80, 100, 247, 0.06)",
			width: `${Math.round(width)}px`,
			height: `${Math.round(height)}px`,
		},
		class: "event-node",
	};

	if (nodes.value.length > 1) {
		nodes.value[1] = nodeData;
	} else {
		nodes.value.push(nodeData);
	}

	nodes.value = [...nodes.value];
};

/** Пересборка сцены при смене шага, картинки или выбранного действия в тулбаре */
async function syncFlowFromStep() {
	const step = store.selectedStep;
	if (!step?.image_url || !step.photo_dimensions) {
		nodes.value = [];
		return;
	}
	lastDrawnArea.value = null;
	clearEventNode();
	await createFullscreenNode();
	await nextTick();
	await nextTick();
	const ev = store.selectedEvent;
	if (!ev || !eventRequiresAreaOpt(ev)) return;
	const a = step.area;
	const savedMatchesToolbar = step.action_type?.id === ev.id;
	if (savedMatchesToolbar && a?.width > 0 && a?.height > 0) {
		createNode(ev, a.width, a.height, a.x, a.y);
	} else {
		createNode(ev);
	}
}

const updateNodePositionOnResize = () => {
	if (nodes.value.length < 1) return;

	const imageNode = nodes.value[0];
	if (!imageNode) return;

	const el = flowContainerRef.value;
	const canvasWidth = el ? el.clientWidth : window.innerWidth;
	const canvasHeight = el ? el.clientHeight : window.innerHeight;
	if (canvasWidth < 80 || canvasHeight < 80) return;

	const imgWidth = imageNode.dimensions.width;
	const imgHeight = imageNode.dimensions.height;
	const viewFlowW = canvasWidth / DEFAULT_ZOOM;
	const viewFlowH = canvasHeight / DEFAULT_ZOOM;
	const newImageX = (viewFlowW - imgWidth) / 2;
	const newImageY = (viewFlowH - imgHeight) / 2;

	if (nodes.value.length < 2) {
		nodes.value[0].position = { x: newImageX, y: newImageY };
		nodes.value = [...nodes.value];
		return;
	}

	const eventNode = nodes.value[1];
	const relativeX = eventNode.position.x - imageNode.position.x;
	const relativeY = eventNode.position.y - imageNode.position.y;

	nodes.value[0].position = { x: newImageX, y: newImageY };
	nodes.value[1].position = {
		x: newImageX + relativeX,
		y: newImageY + relativeY,
	};

	nodes.value = [...nodes.value];
};

function dismissViewportHint() {
	showViewportHint.value = false;
}

function markViewportHintSeen() {
	if (showViewportHint.value) showViewportHint.value = false;
}

/** При смене шага или картинки — восстановить выбранное действие из сохранённых данных шага */
watch(
	() => [store.selectedStep?.id, store.selectedStep?.image_url],
	() => {
		showViewportHint.value = true;
		const st = store.selectedStep;
		if (st?.action_type) {
			store.selectEvent(st.action_type);
		} else {
			store.selectEvent(null);
		}
	},
	{ flush: "pre", immediate: true },
);

watch(
	() => [store.selectedStep?.id, store.selectedStep?.image_url, store.selectedEvent?.id],
	() => {
		syncFlowFromStep();
	},
	{ flush: "post" },
);

let flowResizeObserver = null;

onMounted(() => {
	void syncFlowFromStep();
	flowContainerRef.value?.addEventListener("wheel", markViewportHintSeen, { passive: true });
	flowContainerRef.value?.addEventListener("mousedown", markViewportHintSeen, { passive: true });
	window.addEventListener("resize", updateNodePositionOnResize);
	nextTick(() => {
		nextTick(() => {
			updateNodePositionOnResize();
			if (typeof ResizeObserver !== "undefined" && flowContainerRef.value) {
				flowResizeObserver = new ResizeObserver(() => {
					updateNodePositionOnResize();
				});
				flowResizeObserver.observe(flowContainerRef.value);
			}
		});
	});
});

onUnmounted(() => {
	flowContainerRef.value?.removeEventListener("wheel", markViewportHintSeen);
	flowContainerRef.value?.removeEventListener("mousedown", markViewportHintSeen);
	window.removeEventListener("resize", updateNodePositionOnResize);
	flowResizeObserver?.disconnect();
});
</script>

<style>
@import "@vue-flow/core/dist/style.css";
@import "@vue-flow/core/dist/theme-default.css";
.fullscreen-flow {
	flex: 1;
	min-height: 0;
	width: 100%;
	height: 100%;
	margin: 0;
	padding: 0;
	overflow: hidden;
	display: flex;
	flex-direction: column;
	position: relative;
}

.viewport-hint {
	position: absolute;
	top: 10px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 50;
	display: inline-flex;
	align-items: center;
	gap: 8px;
	max-width: min(94%, 760px);
	padding: 8px 10px;
	background: rgba(15, 23, 42, 0.82);
	backdrop-filter: blur(8px);
	border: 1px solid rgba(148, 163, 184, 0.28);
	border-radius: 10px;
	color: #e2e8f0;
	font-size: 12px;
	line-height: 1.35;
}

.fullscreen-flow .vue-flow {
	flex: 1;
	min-height: 0;
	height: 100%;
}

.fullscreen-flow .vue-flow__pane {
	background: #f0f1f5;
}

.fullscreen-node {
	border: none !important;
	background-color: transparent !important;
	box-shadow: none !important;
}

.fullscreen-node .vue-flow__handle {
	display: none !important;
}

.event-node .vue-flow__handle {
	display: none !important;
}

.event-node {
	transition: box-shadow 0.2s ease;
}

.event-node:hover {
	box-shadow: 0 0 0 3px rgba(80, 100, 247, 0.2);
}
</style>
