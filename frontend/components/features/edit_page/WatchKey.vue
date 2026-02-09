<template>
	<div
		class="cursor-pointer card text-center q-pa-md"
		:class="{ 'text-primary': isListening }"
		style="
		background: rgba(255,255,255,0.68);
		backdrop-filter: blur(10px);
		-webkit-backdrop-filter: blur(10px);
		height: 100%;"
		@click="handleClick"
	>
		<div
			v-if="!isListening && displayKeys"
			class="column items-center justify-center full-height"
		>
			<span class="text-caption text-grey-7">
				Выбранные клавиши
			</span>
			<span style="font-size: 1.1rem; font-weight: 500;">
				{{ displayKeys }}
			</span>
		</div>

		<div
			v-else
			class="full-height flex items-center justify-center"
		>
			<span style="font-size: 1.1rem;">
				{{ isListening ? 'Нажмите клавишу...' : 'Отследить клавишу' }}
			</span>
		</div>
	</div>
</template>

<script setup>
import { useMagicKeys } from "@vueuse/core";
import { ref, watch, computed } from "vue";

const { current } = useMagicKeys();
const isListening = ref(false);
const pressedKeys = defineModel();

// Вычисляемое свойство для отображения клавиш
const displayKeys = computed(() => {
	return pressedKeys.value?.join('+') || '';
});

// Обработчик клика
const handleClick = () => {
	if (isListening.value) {
		isListening.value = false;
	} else {
		startListening();
	}
};

// Функция начала отслеживания
const startListening = () => {
	isListening.value = true;
	pressedKeys.value = [];
};

// Отслеживаем нажатия клавиш
watch(current, (keys) => {
	if (isListening.value && keys.size > 0) {
		pressedKeys.value = Array.from(keys);
		setTimeout(() => {
			isListening.value = false;
		}, 150);
	}
}, { deep: true });
</script>

<style scoped>
.full-height {
	height: 100%;
	min-height: 30px;
}
</style>