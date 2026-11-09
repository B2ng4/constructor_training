<template>
	<div
		class="scenario-step-node"
		:class="{ 'scenario-step-node--selected': data.selected }"
		@click="onCardClick"
	>
		<Handle type="target" :position="Position.Left" class="scenario-step-node__handle scenario-step-node__handle--target" />
		<Handle type="source" :position="Position.Right" class="scenario-step-node__handle scenario-step-node__handle--source" />
		<span class="scenario-step-node__port-label scenario-step-node__port-label--in">Вход</span>
		<span class="scenario-step-node__port-label scenario-step-node__port-label--out">Связать</span>

		<div class="scenario-step-node__header">
			<q-icon name="drag_indicator" size="18px" class="scenario-step-node__drag-icon" />
			<span class="scenario-step-node__badge">{{ data.step?.step_number }}</span>
			<span class="scenario-step-node__title">{{ label }}</span>
			<q-btn
				v-if="data.onDelete"
				flat
				dense
				round
				size="xs"
				icon="delete_outline"
				color="grey-7"
				class="scenario-step-node__delete"
				@click.stop="onDeleteClick"
			>
				<q-tooltip>Удалить шаг</q-tooltip>
			</q-btn>
		</div>

		<div class="scenario-step-node__thumb">
			<img
				v-if="data.step?.image_url"
				:src="data.step.image_url"
				:alt="label"
				loading="lazy"
			/>
			<div v-else class="scenario-step-node__thumb-placeholder">
				<q-icon name="image_not_supported" size="28px" color="grey-5" />
			</div>
		</div>

		<div class="scenario-step-node__footer">
			<q-icon name="touch_app" size="14px" color="primary" />
			<span>{{ actionLabel }}</span>
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { Handle, Position } from "@vue-flow/core";
import { stepActionLabel, stepLabel } from "@utils/scenarioMapLayout.js";

const props = defineProps({
	id: { type: String, required: true },
	data: { type: Object, required: true },
});

const label = computed(() => stepLabel(props.data?.step));
const actionLabel = computed(() => stepActionLabel(props.data?.step));

function onCardClick() {
	props.data?.onSelect?.(props.data.step);
}

function onDeleteClick() {
	props.data?.onDelete?.(props.data.step);
}
</script>

<style scoped>
.scenario-step-node {
	width: 224px;
	border-radius: 16px;
	background: rgba(255, 255, 255, 0.96);
	border: 1px solid rgba(15, 23, 42, 0.1);
	box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
	overflow: visible;
	cursor: grab;
	transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.scenario-step-node:active {
	cursor: grabbing;
}

.scenario-step-node:hover {
	box-shadow: 0 12px 28px rgba(80, 100, 247, 0.16);
	border-color: rgba(80, 100, 247, 0.35);
}

.scenario-step-node--selected {
	border-color: rgba(80, 100, 247, 0.65);
	box-shadow: 0 0 0 3px rgba(80, 100, 247, 0.18);
}

.scenario-step-node__handle {
	width: 17px;
	height: 17px;
	background: var(--q-primary);
	border: 3px solid #fff;
	box-shadow: 0 0 0 1px rgba(80, 100, 247, .35), 0 4px 10px rgba(80, 100, 247, .28);
	opacity: .82;
	transition: opacity .18s ease, scale .18s ease, box-shadow .18s ease;
	z-index: 4;
}

.scenario-step-node__handle--target {
	background: #94a3b8;
	box-shadow: 0 0 0 1px rgba(100, 116, 139, .3), 0 4px 10px rgba(15, 23, 42, .14);
}

.scenario-step-node:hover .scenario-step-node__handle,
.scenario-step-node--selected .scenario-step-node__handle {
	opacity: 1;
	scale: 1.12;
}

.scenario-step-node__handle--source:hover {
	scale: 1.3;
	box-shadow: 0 0 0 6px rgba(80, 100, 247, .13), 0 5px 14px rgba(80, 100, 247, .35);
}

.scenario-step-node__port-label {
	position: absolute;
	top: 50%;
	z-index: 3;
	padding: 3px 6px;
	border-radius: 7px;
	background: rgba(15, 23, 42, .78);
	color: #fff;
	font-size: 9px;
	font-weight: 700;
	line-height: 1;
	opacity: 0;
	pointer-events: none;
	transition: opacity .18s ease, transform .18s ease;
}

.scenario-step-node__port-label--in { left: -12px; transform: translate(-100%, -50%); }
.scenario-step-node__port-label--out { right: -12px; transform: translate(100%, -50%); }
.scenario-step-node:hover .scenario-step-node__port-label { opacity: 1; }
.scenario-step-node:hover .scenario-step-node__port-label--in { transform: translate(-100%, -50%) translateX(-2px); }
.scenario-step-node:hover .scenario-step-node__port-label--out { transform: translate(100%, -50%) translateX(2px); }

.scenario-step-node__header {
	display: flex;
	align-items: center;
	gap: 7px;
	min-height: 42px;
	padding: 9px 10px 7px;
	border-radius: 16px 16px 0 0;
	cursor: grab;
}

.scenario-step-node__header:active { cursor: grabbing; }
.scenario-step-node__drag-icon { flex: 0 0 auto; color: #cbd5e1; }
.scenario-step-node:hover .scenario-step-node__drag-icon { color: #5064f7; }

.scenario-step-node__badge {
	flex-shrink: 0;
	min-width: 22px;
	height: 22px;
	border-radius: 999px;
	background: rgba(80, 100, 247, 0.12);
	color: var(--q-primary);
	font-size: 11px;
	font-weight: 700;
	display: inline-flex;
	align-items: center;
	justify-content: center;
}

.scenario-step-node__title {
	flex: 1;
	min-width: 0;
	font-size: 13px;
	font-weight: 680;
	color: #1e293b;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.scenario-step-node__delete {
	opacity: 0;
	transition: opacity 0.15s ease;
}

.scenario-step-node:hover .scenario-step-node__delete,
.scenario-step-node--selected .scenario-step-node__delete {
	opacity: 0.75;
}

.scenario-step-node__thumb {
	height: 118px;
	margin: 0 10px;
	border-radius: 10px;
	overflow: hidden;
	background: #f1f5f9;
	border: 1px solid rgba(15, 23, 42, 0.06);
}

.scenario-step-node__thumb img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	display: block;
}

.scenario-step-node__thumb-placeholder {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.scenario-step-node__footer {
	display: flex;
	align-items: center;
	gap: 4px;
	padding: 8px;
	font-size: 11px;
	color: #64748b;
}

:global(body.body--dark) .scenario-step-node {
	background: rgba(17, 24, 39, 0.96);
	border-color: rgba(148, 163, 184, 0.18);
	box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28);
}

:global(body.body--dark) .scenario-step-node__title {
	color: #f1f5f9;
}

:global(body.body--dark) .scenario-step-node__thumb {
	background: #0b1220;
	border-color: rgba(148, 163, 184, 0.14);
}

:global(body.body--dark) .scenario-step-node__footer {
	color: #94a3b8;
}
</style>
