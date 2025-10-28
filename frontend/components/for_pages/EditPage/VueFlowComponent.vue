<template>
	<div class="fullscreen-flow">
		<VueFlow
			:nodes="nodes"
		>
		</VueFlow>
	</div>
</template>

<script setup>
import { ref } from "vue";
import { VueFlow } from "@vue-flow/core";

const nodes = ref([
	{
		id: "1",
		type: "resizable",
		position: { x: 100, y: 100 },
	},
	{
		id: "2",
		type: "resizable",
		position: { x: 300, y: 100 },
	},
]);
</script>

<style>
@import "@vue-flow/core/dist/style.css";
@import "@vue-flow/core/dist/theme-default.css";

.fullscreen-flow {
	width: 100vw;
	height: 100vh;
	margin: 0;
	padding: 0;
}

</style>
