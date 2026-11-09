<template>
	<div class="scenario-terminal" :class="`scenario-terminal--${data.kind}`">
		<Handle v-if="data.kind === 'finish'" type="target" :position="Position.Left" class="scenario-terminal__handle" />
		<div class="scenario-terminal__icon">
			<q-icon :name="data.kind === 'start' ? 'play_arrow' : 'flag'" size="22px" />
		</div>
		<div>
			<div class="scenario-terminal__eyebrow">{{ data.kind === "start" ? "Точка входа" : "Результат" }}</div>
			<div class="scenario-terminal__label">{{ data.label }}</div>
		</div>
		<Handle v-if="data.kind === 'start'" type="source" :position="Position.Right" class="scenario-terminal__handle" />
	</div>
</template>

<script setup>
import { Handle, Position } from "@vue-flow/core";

defineProps({ data: { type: Object, required: true } });
</script>

<style scoped>
.scenario-terminal {
	min-width: 154px;
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 14px 16px;
	border-radius: 16px;
	background: rgba(255, 255, 255, 0.96);
	border: 1px solid rgba(15, 23, 42, 0.1);
	box-shadow: 0 10px 28px rgba(15, 23, 42, 0.09);
}
.scenario-terminal--start { border-color: rgba(80, 100, 247, 0.35); }
.scenario-terminal--finish { border-color: rgba(34, 197, 94, 0.35); }
.scenario-terminal__icon {
	width: 38px;
	height: 38px;
	display: grid;
	place-items: center;
	border-radius: 12px;
	color: #fff;
	background: #5064f7;
}
.scenario-terminal--finish .scenario-terminal__icon { background: #16a34a; }
.scenario-terminal__handle {
	width: 17px;
	height: 17px;
	border: 3px solid #fff;
	background: #5064f7;
	box-shadow: 0 0 0 1px rgba(80, 100, 247, .35), 0 4px 12px rgba(80, 100, 247, .3);
}
.scenario-terminal--finish .scenario-terminal__handle { background: #16a34a; box-shadow: 0 0 0 1px rgba(22, 163, 74, .35), 0 4px 12px rgba(22, 163, 74, .25); }
.scenario-terminal__eyebrow { color: #94a3b8; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; }
.scenario-terminal__label { color: #0f172a; font-size: 14px; font-weight: 750; }
:global(body.body--dark) .scenario-terminal { background: rgba(17, 24, 39, .96); border-color: rgba(148, 163, 184, .18); }
:global(body.body--dark) .scenario-terminal__label { color: #f1f5f9; }
</style>
