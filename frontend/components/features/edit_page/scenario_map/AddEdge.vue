<template>
	<g>
		<path
			v-if="!data?.startEdge"
			:d="path"
			fill="none"
			stroke="transparent"
			stroke-width="20"
			class="scenario-edge-hitarea"
			@click.stop="data?.onEdit?.(data.transition)"
		/>
		<BaseEdge :path="path" :marker-end="markerEnd" :style="style" />
		<EdgeLabelRenderer>
			<button
				v-if="!data?.startEdge"
				class="scenario-edge-label nodrag nopan"
				:style="labelStyle"
				type="button"
				@click.stop="data?.onEdit?.(data.transition)"
			>
				<span class="scenario-edge-label__dot" :style="{ background: data?.meta?.color }" />
				{{ data?.transition?.label || data?.meta?.label }}
				<q-icon name="tune" size="13px" />
			</button>
		</EdgeLabelRenderer>
	</g>
</template>

<script setup>
import { computed } from "vue";
import { BaseEdge, EdgeLabelRenderer, getSmoothStepPath } from "@vue-flow/core";

const props = defineProps({
	sourceX: Number,
	sourceY: Number,
	targetX: Number,
	targetY: Number,
	sourcePosition: String,
	targetPosition: String,
	markerEnd: [String, Object],
	style: Object,
	data: { type: Object, default: () => ({}) },
});
const pathData = computed(() => getSmoothStepPath({
	sourceX: props.sourceX,
	sourceY: props.sourceY,
	targetX: props.targetX,
	targetY: props.targetY,
	sourcePosition: props.sourcePosition,
	targetPosition: props.targetPosition,
	borderRadius: 18,
}));
const path = computed(() => pathData.value[0]);
const labelStyle = computed(() => ({
	position: "absolute",
	transform: `translate(-50%, -50%) translate(${pathData.value[1]}px, ${pathData.value[2]}px)`,
	pointerEvents: "all",
}));
</script>

<style>
.scenario-edge-hitarea { cursor: pointer; pointer-events: stroke; }
.scenario-edge-label {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	max-width: 220px;
	min-height: 28px;
	padding: 7px 10px;
	border: 1px solid rgba(15, 23, 42, .1);
	border-radius: 999px;
	background: rgba(255, 255, 255, .96);
	box-shadow: 0 4px 14px rgba(15, 23, 42, .09);
	color: #475569;
	font: 650 11px/1.2 var(--font-sans);
	white-space: nowrap;
	cursor: pointer;
}
.scenario-edge-label:hover { border-color: rgba(80, 100, 247, .4); color: #5064f7; }
.scenario-edge-label__dot { width: 7px; height: 7px; border-radius: 50%; flex: 0 0 auto; }
body.body--dark .scenario-edge-label { background: rgba(17, 24, 39, .96); border-color: rgba(148, 163, 184, .18); color: #cbd5e1; }
</style>
