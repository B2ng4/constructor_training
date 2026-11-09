<template>
	<VueFlow
		:id="flowId"
		v-model:nodes="nodes"
		v-model:edges="edges"
		:node-types="nodeTypes"
		:edge-types="edgeTypes"
		:default-viewport="{ zoom: 0.78 }"
		:min-zoom="0.28"
		:max-zoom="1.8"
		:nodes-connectable="true"
		:edges-updatable="true"
		:zoom-on-double-click="false"
		:zoom-on-scroll="true"
		:zoom-on-pinch="true"
		:pan-on-scroll="false"
		:delete-key-code="['Backspace', 'Delete']"
		class="scenario-map-flow"
		@connect="emit('connect', $event)"
		@node-drag-stop="emit('node-drag-stop', $event)"
		@edge-update="emit('edge-update', $event)"
		@edges-delete="emit('edges-delete', $event)"
	>
		<div class="scenario-map-controls nodrag nopan">
			<q-btn flat round dense icon="remove" @click="zoomOutView"><q-tooltip>Уменьшить</q-tooltip></q-btn>
			<button class="scenario-map-controls__zoom" type="button" @click="resetZoom">{{ zoomPercent }}%</button>
			<q-btn flat round dense icon="add" @click="zoomInView"><q-tooltip>Увеличить</q-tooltip></q-btn>
			<div class="scenario-map-controls__divider" />
			<q-btn flat round dense icon="fit_screen" @click="doFitView"><q-tooltip>Показать весь сценарий</q-tooltip></q-btn>
		</div>
		<div class="scenario-map-hint">
			<q-icon name="open_with" size="16px" />
			Перетаскивайте карточки · соединяйте цветные точки
		</div>
	</VueFlow>
</template>

<script setup>
import { computed, markRaw, onMounted, watch } from "vue";
import { VueFlow, useVueFlow } from "@vue-flow/core";
import StepNode from "./StepNode.vue";
import TerminalNode from "./TerminalNode.vue";
import ScenarioEdge from "./AddEdge.vue";

const props = defineProps({
	flowId: { type: String, required: true },
	nodes: { type: Array, required: true },
	edges: { type: Array, required: true },
});
const emit = defineEmits(["connect", "node-drag-stop", "edge-update", "edges-delete"]);
const nodes = defineModel("nodes", { type: Array, required: true });
const edges = defineModel("edges", { type: Array, required: true });
const nodeTypes = { step: markRaw(StepNode), terminal: markRaw(TerminalNode) };
const edgeTypes = { scenario: markRaw(ScenarioEdge) };
const { fitView, zoomIn, zoomOut, setViewport, viewport } = useVueFlow({ id: props.flowId });
const zoomPercent = computed(() => Math.round((viewport.value?.zoom || 1) * 100));
function doFitView() {
	void fitView({ padding: 0.2, duration: 320, minZoom: 0.55, maxZoom: 1 });
}
function zoomInView() { void zoomIn({ duration: 180 }); }
function zoomOutView() { void zoomOut({ duration: 180 }); }
function resetZoom() {
	void setViewport({ x: viewport.value?.x || 0, y: viewport.value?.y || 0, zoom: 1 }, { duration: 220 });
}
onMounted(doFitView);
watch(() => props.nodes.length, (next, previous) => {
	if (next !== previous) doFitView();
});
defineExpose({ fitView: doFitView, zoomIn: zoomInView, zoomOut: zoomOutView });
</script>

<style scoped>
.scenario-map-flow { width: 100%; height: 100%; }
.scenario-map-controls {
	position: absolute;
	top: 18px;
	right: 18px;
	z-index: 8;
	display: flex;
	align-items: center;
	gap: 2px;
	padding: 5px;
	border: 1px solid rgba(148, 163, 184, .24);
	border-radius: 14px;
	background: rgba(255, 255, 255, .92);
	box-shadow: 0 9px 28px rgba(15, 23, 42, .1);
	backdrop-filter: blur(16px);
}
.scenario-map-controls__zoom {
	min-width: 50px;
	padding: 5px 7px;
	border: 0;
	border-radius: 8px;
	background: transparent;
	color: #475569;
	font: 650 12px/1 var(--font-sans);
	cursor: pointer;
}
.scenario-map-controls__zoom:hover { background: rgba(80, 100, 247, .08); color: #5064f7; }
.scenario-map-controls__divider { width: 1px; height: 22px; margin: 0 3px; background: rgba(148, 163, 184, .24); }
.scenario-map-hint {
	position: absolute;
	left: 18px;
	bottom: 18px;
	display: flex;
	align-items: center;
	gap: 7px;
	padding: 9px 12px;
	border: 1px solid rgba(148, 163, 184, .22);
	border-radius: 12px;
	background: rgba(255, 255, 255, .88);
	box-shadow: 0 7px 22px rgba(15, 23, 42, .08);
	color: #64748b;
	font-size: 12px;
	backdrop-filter: blur(14px);
	pointer-events: none;
}
:global(body.body--dark) .scenario-map-hint,
:global(body.body--dark) .scenario-map-controls { background: rgba(17, 24, 39, .9); border-color: rgba(148, 163, 184, .18); color: #94a3b8; }
:global(body.body--dark) .scenario-map-controls__zoom { color: #cbd5e1; }
</style>

<style>
@import "@vue-flow/core/dist/style.css";
@import "@vue-flow/core/dist/theme-default.css";
.scenario-map-flow .vue-flow__pane {
	background: radial-gradient(circle at 1px 1px, rgba(148, 163, 184, .32) 1px, transparent 0) 0 0 / 22px 22px !important;
}
.scenario-map-flow .vue-flow__connection-path { stroke: #5064f7; stroke-width: 2.5; }
</style>
