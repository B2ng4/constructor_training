<template>
	<div class="fullscreen-flow">
		<VueFlow  fit-view-on-init :nodes="nodes">
		</VueFlow>
	</div>
</template>

<script setup>
import { ref } from 'vue';
import { VueFlow } from '@vue-flow/core';

const nodes = ref([
	{
		id: '1',
		type: 'resizable',
		position: { x: 100, y: 100 },
	},
	{
		id: '2',
		type: 'resizable',
		position: { x: 300, y: 100 },
	}
])
</script>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';

.fullscreen-flow {
	width: 100vw;
	height: 100vh;
	margin: 0;
	padding: 0;
}

/* Или если нужно внутри другого контейнера */
.flow-container {
	width: 100%;
	height: 100%;
	min-height: 500px;
}
</style>