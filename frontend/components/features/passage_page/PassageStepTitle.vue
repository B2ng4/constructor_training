<template>
	<div v-if="selectedStep" class="passage-step-title">
		<q-icon name="description" size="18px" class="title-icon" />
		<span>{{ displayName }}</span>
	</div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
	selectedStep: { type: Object, default: null },
});

const displayName = computed(
	() => props.selectedStep?.meta?.name ?? "Шаг без названия"
);
</script>

<style scoped>
.passage-step-title {
	position: absolute;
	top: 16px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 5;
	display: flex;
	align-items: center;
	gap: 8px;
	background: rgba(255, 255, 255, 0.9);
	backdrop-filter: blur(16px);
	padding: 10px 18px;
	border-radius: 12px;
	box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(255, 255, 255, 0.6);
	font-size: 14px;
	font-weight: 600;
	color: #1a1a2e;
}

.title-icon {
	color: var(--q-primary);
	opacity: 0.8;
}
</style>
