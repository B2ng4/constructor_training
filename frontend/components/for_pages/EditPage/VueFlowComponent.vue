<template>
	<div class="fullscreen-flow">
		<VueFlow v-model="nodes" :default-viewport="{ zoom: 0.4 }" >
			<template #node-resizable="resizableNodeProps">
				<ResizableNode :data="resizableNodeProps.data" />
			</template>
		</VueFlow>
	</div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { VueFlow } from "@vue-flow/core";
import { useTrainingData } from "@store/editTraining.js";
import ResizableNode from "./ResizableNode.vue";

const store = useTrainingData();
const nodes = ref([]);

const createFullscreenNode = () => {
	const width = window.innerWidth;
	const height = window.innerHeight;

	nodes.value = [
		{
			id: "fullscreen-image",
			position: { x: width / 2, y: height / 2 },
			style: {
				backgroundImage: `url(${store.selectedStep.image_url})`,
				backgroundSize: "contain",
				backgroundPosition: "center",
				backgroundRepeat: "no-repeat",
				width: `${width}px`,
				height: `${height}px`,
			},
			connectable: false,
			data: { label: "" },
			class: "fullscreen-node",
		},
	];
};

const createNode = (event) => {
	const width = window.innerWidth;
	const height = window.innerHeight;
	nodes.value[1] = {
		id: event.id,
		type: 'resizable',
		data: { label: event.name, type: event.type },
		position: { x: width / 2, y: height / 2 },
		zIndex: 1000,
		style: { border: '2px solid black' },
	};
	// В VueFlow не меняются ноды, поэтому нужно обновить его
	nodes.value = [...nodes.value];
};

watch(
	() => store.selectedStep.image_url,
	() => {
		createFullscreenNode();
	},
);

onMounted(() => {
	createFullscreenNode();
});

defineExpose({
	createNode,
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

.fullscreen-node {
	border: none !important;
	background-color: transparent !important;
	box-shadow: none !important;
}

/* Убираем точки соединения */
.fullscreen-node .vue-flow__handle {
	display: none !important;
}
</style>
