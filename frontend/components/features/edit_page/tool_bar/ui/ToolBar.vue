<template>
	<div class="tool-bar shadow-7">
		<div class="q-gutter-x-md">
			<q-btn
				@click="store.selectEvent(event);"
				dense
				:key="event.id"
				v-for="event in events"
				:color="store.selectedEvent?.id === event.id ? 'primary' : ''"
				:text-color="store.selectedEvent?.id === event.id ? 'white' : 'black'"
			>
				<q-tooltip class="bg-primary text-body1">
					{{event.name}}
				</q-tooltip>
				<Component :is="event.icon" />
			</q-btn>
		</div>
	</div>
</template>

<script setup>
import {
	RightClick,
	LeftClick,
	DoubleClick,
	Text,
	Mouseover,
	Keyboard,
} from "@components/features/edit_page/icons_tool_bar/index.js";
import { useTrainingData } from "@store/editTraining.js";

const store = useTrainingData();
//TODO: БРАТЬ ДЕЙСТВИЯ ИЗ БД
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
		type: "mouseover",
		name: "Наведение курсора",
		icon: Mouseover,
		id: 5,
	},
	{
		type: "text",
		name: "Ввод текста",
		icon: Text,
		id: 4,
	},
	{
		type: "keydown",
		name: "Нажатие клавиши",
		icon: Keyboard,
		id: 6,
	},
];
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