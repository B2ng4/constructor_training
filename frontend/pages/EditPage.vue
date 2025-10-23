<template>
	<div class="fullscreen-flow">
		<VueFlow :nodes="nodes" :edges="edges">
			<Background />
		</VueFlow>
	</div>
</template>

<script setup>
import { ref } from 'vue';
import { VueFlow } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';

const nodes = ref([
	{
		id: '1',
		type: 'input',
		position: { x: 100, y: 100 },
		data: { label: 'Начальный узел' }
	},
	{
		id: '2',
		position: { x: 300, y: 100 },
		data: { label: 'Второй узел' }
	}
])

const edges = ref([
	{
		id: 'e1-2',
		source: '1',
		target: '2'
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