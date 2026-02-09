<template>
	<div class="tool-bar-container">
		<!-- Левая стрелка -->
		<q-btn
			v-if="hasPreviousStep"
			class="navigation-arrow left-arrow"
			round
			dense
			icon="chevron_left"
			color="primary"
			@click="goToPreviousStep"
			size="lg"
		>
			<q-tooltip>Предыдущий шаг</q-tooltip>
		</q-btn>

		<!-- Основной тулбар -->
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
						{{ event.name }}
					</q-tooltip>
					<Component :is="event.icon" />
				</q-btn>
			</div>
		</div>

		<!-- Правая стрелка -->
		<q-btn
			v-if="hasNextStep"
			class="navigation-arrow right-arrow"
			round
			dense
			icon="chevron_right"
			color="primary"
			@click="goToNextStep"
			size="lg"
		>
			<q-tooltip>Следующий шаг</q-tooltip>
		</q-btn>
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
import { computed } from "vue";

const store = useTrainingData();

// Вычисляемые свойства для навигации
const hasPreviousStep = computed(() => {
	if (!store.trainingData?.steps) return false;
	const currentIndex = store.trainingData.steps.findIndex(
		step => step.id === store.selectedStep?.id
	);
	return currentIndex > 0;
});

const hasNextStep = computed(() => {
	if (!store.trainingData?.steps) return false;
	const currentIndex = store.trainingData.steps.findIndex(
		step => step.id === store.selectedStep?.id
	);
	return currentIndex >= 0 && currentIndex < store.trainingData.steps.length - 1;
});

const goToPreviousStep = () => {
	if (!store.trainingData?.steps) return;
	const currentIndex = store.trainingData.steps.findIndex(
		step => step.id === store.selectedStep?.id
	);
	if (currentIndex > 0) {
		store.selectStep(store.trainingData.steps[currentIndex - 1]);
	}
};

const goToNextStep = () => {
	if (!store.trainingData?.steps) return;
	const currentIndex = store.trainingData.steps.findIndex(
		step => step.id === store.selectedStep?.id
	);
	if (currentIndex < store.trainingData.steps.length - 1) {
		store.selectStep(store.trainingData.steps[currentIndex + 1]);
	}
};

// TODO: БРАТЬ ДЕЙСТВИЯ ИЗ БД
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
		type: "hover",
		name: "Наведение курсора",
		icon: Mouseover,
		id: 4,
	},
	{
		type: "inputText",
		name: "Ввод текста",
		icon: Text,
		id: 5,
	},
	{
		type: "keyPress",
		name: "Нажатие клавиши",
		icon: Keyboard,
		id: 6,
	},
];
</script>

<style scoped>
.tool-bar-container {
	position: absolute;
	z-index: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 20px;
	width: 100%;
	left: 0;
	bottom: 25px;
}

.tool-bar {
	background: #ffffff;
	width: auto;
	padding: 10px;
	border-radius: 10px;
}

.navigation-arrow {
	box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.left-arrow {
	margin-right: 10px;
}

.right-arrow {
	margin-left: 10px;
}
</style>