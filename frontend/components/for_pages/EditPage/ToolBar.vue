<template>
	<div class="tool-bar shadow-7">
		<div class="q-gutter-x-md">
			<q-btn
				@click="selectEvent(event)"
				dense
				:key="event.id"
				v-for="event in events"
				:color="selectedEvent?.id === event.id ? 'primary' : ''"
				:text-color="selectedEvent?.id === event.id ? 'white' : 'black'"
			>
				<Component :is="event.icon" />
			</q-btn>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue";
import {
	RightClick,
	LeftClick,
	DoubleClick,
	Text
} from "@components/for_pages/EditPage/IconsToolBar/index.js";

const selectedEvent = ref(null);
const events = [
	{
		type: "leftClick",
		name: "Левый клик",
		icon: LeftClick,
		id: 1,
	},
	{
		type: "rightClick",
		name: "Правый клик",
		icon: RightClick,
		id: 2,
	},
	{
		type: "doubleClick",
		name: "Двойной клик",
		icon: DoubleClick,
		id: 3,
	},
	{
		type: "text",
		name: "Ввод текста",
		icon: Text,
		id: 4,
	},
	{
		type: "mouseover",
		name: "Наведение курсора",
		icon: "",
		id: 5,
	},
	{
		type: "keydown",
		name: "Нажатие клавиши",
		icon: "",
		id: 6,
	},
];

const emit = defineEmits(["selectEvent"]);
const selectEvent = (event) => {
	selectedEvent.value = event;
	emit("selectEvent", selectedEvent.value);
};
</script>

<style scoped>
.tool-bar {
	position: absolute;
	z-index: 1;
	background: #ffffff;
	width: auto;
	left: 50%;
	transform: translateX(-50%);
	bottom: 25px;
	padding: 10px;
	border-radius: 10px;
}
</style>