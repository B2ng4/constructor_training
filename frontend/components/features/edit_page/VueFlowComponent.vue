<template>
	<div class="fullscreen-flow">
		<VueFlow v-model="nodes" :default-viewport="{ zoom: 0.7 }">
			<template #node-resizable="resizableNodeProps">
				<ResizableNode :node="resizableNodeProps" :position="positionOnImage" />
			</template>
		</VueFlow>
	</div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { VueFlow, Position } from "@vue-flow/core";
import { useTrainingData } from "@store/editTraining.js";
import ResizableNode from "./ResizableNode.vue";

const store = useTrainingData();
const nodes = ref([]);
const eventRequiresArea = (event) => event?.type !== "keyPress";

// Computed свойство для вычисления позиции события относительно изображения
const positionOnImage = computed(() => {
	if (nodes.value.length < 2) return null;

	const imageNode = nodes.value[0];
	const eventNode = nodes.value[1];

	if (!imageNode || !eventNode) return null;

	// Вычисляем относительную позицию
	const relativeX = eventNode.position.x - imageNode.position.x;
	const relativeY = eventNode.position.y - imageNode.position.y;

	return {
		x: Math.max(0, Math.round(relativeX)),
		y: Math.max(0, Math.round(relativeY))
	};
});

// Функция для очистки ноды события
const clearEventNode = () => {
	// Оставляем только ноду с изображением
	if (nodes.value.length > 0) {
		nodes.value = [nodes.value[0]];
	}
};

const createFullscreenNode = async () => {
	const { width: imgWidth, height: imgHeight } = store.selectedStep.photo_dimensions;
	const canvasWidth = window.innerWidth;
	const canvasHeight = window.innerHeight;

	const x = (canvasWidth - imgWidth) / 2;
	const y = (canvasHeight - imgHeight) / 2;

	nodes.value[0] = {
		id: "fullscreen-image",
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

	//Если уже есть выбранное действие, то заносим его в store
	//Почему именно в этом месте? (vue flow ломается, поэтому проверяем,
	// как только создалась картинка, добавляем в store)
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

	// Проверяем, чтобы нода не выходила за пределы изображения
	const maxX = imageNode.dimensions.width - width;
	const maxY = imageNode.dimensions.height - height;

	const clampedX = Math.max(0, Math.min(relativeX, maxX));
	const clampedY = Math.max(0, Math.min(relativeY, maxY));

	const finalAbsoluteX = imageNode.position.x + clampedX;
	const finalAbsoluteY = imageNode.position.y + clampedY;

	// Проверяем, существует ли уже нода события
	if (nodes.value.length > 1) {
		// Обновляем существующую ноду
		nodes.value[1] = {
			id: event.id,
			type: "resizable",
			data: {
				label: event.name,
				type: event.type,
				toolbarPosition: Position.Top,
				toolbarVisible: true,
			},
			dimensions: {
				width: width,
				height: height,
			},
			position: {
				x: finalAbsoluteX,
				y: finalAbsoluteY
			},
			style: {
				border: "2px solid black",
				width: `${width}px`,
				height: `${height}px`,
			},
			class: "event-node",
		};
	} else {
		// Создаем новую ноду
		nodes.value.push({
			id: event.id,
			type: "resizable",
			data: {
				label: event.name,
				type: event.type,
				toolbarPosition: Position.Top,
				toolbarVisible: true,
			},
			dimensions: {
				width: width,
				height: height,
			},
			position: {
				x: finalAbsoluteX,
				y: finalAbsoluteY
			},
			style: {
				border: "2px solid black",
				width: `${width}px`,
				height: `${height}px`,
			},
			class: "event-node",
		});
	}

	// В VueFlow не меняются ноды, поэтому нужно обновить его
	nodes.value = [...nodes.value];
};

// Watcher для обновления позиции при изменении размера окна
const updateNodePositionOnResize = () => {
	if (nodes.value.length < 2) return;

	const imageNode = nodes.value[0];
	const eventNode = nodes.value[1];

	if (!imageNode || !eventNode) return;

	// Пересчитываем позицию изображения
	const canvasWidth = window.innerWidth;
	const canvasHeight = window.innerHeight;
	const imgWidth = imageNode.dimensions.width;
	const imgHeight = imageNode.dimensions.height;

	const newImageX = (canvasWidth - imgWidth) / 2;
	const newImageY = (canvasHeight - imgHeight) / 2;

	// Обновляем позицию изображения
	nodes.value[0].position = { x: newImageX, y: newImageY };

	// Обновляем позицию ноды события относительно нового положения изображения
	const relativeX = eventNode.position.x - imageNode.position.x;
	const relativeY = eventNode.position.y - imageNode.position.y;

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
			// Если событие было сброшено, очищаем ноду
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

.fullscreen-node {
	border: none !important;
	background-color: transparent !important;
	box-shadow: none !important;
}

/* Убираем точки соединения для картинки*/
.fullscreen-node .vue-flow__handle {
	display: none !important;
}
/* Убираем точки соединения для нод действий*/
.event-node .vue-flow__handle {
	display: none !important;
}
</style>