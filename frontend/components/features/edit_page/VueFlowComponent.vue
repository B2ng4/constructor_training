<template>
	<div ref="flowContainerRef" class="fullscreen-flow">
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
import { ref, watch, onMounted, computed, provide } from "vue";
import { VueFlow, Position } from "@vue-flow/core";
import { useTrainingData } from "@store/editTraining.js";
import ResizableNode from "./ResizableNode.vue";
import ScreenshotNode from "./ScreenshotNode.vue";

const store = useTrainingData();
const nodes = ref([]);
const flowContainerRef = ref(null);
const nodeTypes = { screenshot: ScreenshotNode };
const DEFAULT_ZOOM = 0.7;

const eventRequiresArea = (event) => event?.type !== "keyPress";

const drawingEnabled = computed(() => {
	return !!store.selectedEvent && eventRequiresArea(store.selectedEvent);
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

	if (store.selectedStep.action_type) {
		store.selectEvent(store.selectedStep.action_type);
	}
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

const updateNodePositionOnResize = () => {
	if (nodes.value.length < 2) return;

	const imageNode = nodes.value[0];
	const eventNode = nodes.value[1];

	if (!imageNode || !eventNode) return;

	const el = flowContainerRef.value;
	const canvasWidth = el ? el.clientWidth : window.innerWidth;
	const canvasHeight = el ? el.clientHeight : window.innerHeight;
	const imgWidth = imageNode.dimensions.width;
	const imgHeight = imageNode.dimensions.height;
	const viewFlowW = canvasWidth / DEFAULT_ZOOM;
	const viewFlowH = canvasHeight / DEFAULT_ZOOM;
	const newImageX = (viewFlowW - imgWidth) / 2;
	const newImageY = (viewFlowH - imgHeight) / 2;

	const relativeX = eventNode.position.x - imageNode.position.x;
	const relativeY = eventNode.position.y - imageNode.position.y;

	nodes.value[0].position = { x: newImageX, y: newImageY };
	nodes.value[1].position = {
		x: newImageX + relativeX,
		y: newImageY + relativeY
	};

	nodes.value = [...nodes.value];
};

watch(
	() => store.selectedStep.image_url,
	() => {
		clearEventNode();
		createFullscreenNode();
		if (store.selectedStep.action_type && eventRequiresArea(store.selectedStep.action_type) && store.selectedStep.area) {
			createNode(
				store.selectedStep.action_type,
				store.selectedStep.area.width,
				store.selectedStep.area.height,
				store.selectedStep.area.x,
				store.selectedStep.area.y,
			);
		}
	},
);

watch(
	() => store.selectedEvent,
	() => {
		if (!store.selectedEvent) {
			clearEventNode();
			return;
		}

		if (!eventRequiresArea(store.selectedEvent)) {
			clearEventNode();
			return;
		}

		if (store.selectedStep.action_type && store.selectedStep.area && eventRequiresArea(store.selectedEvent)) {
			createNode(
				store.selectedEvent,
				store.selectedStep.area.width,
				store.selectedStep.area.height,
				store.selectedStep.area.x,
				store.selectedStep.area.y
			);
		} else {
			createNode(store.selectedEvent);
		}
	}
);

onMounted(() => {
	createFullscreenNode();
	window.addEventListener('resize', updateNodePositionOnResize);
});
</script>

<style>
@import "@vue-flow/core/dist/style.css";
@import "@vue-flow/core/dist/theme-default.css";
.fullscreen-flow {
	width: 100vw;
	height: 100vh;
	margin: 0;
	padding: 0;
	overflow: hidden;
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
