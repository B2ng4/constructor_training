<template>
	<template v-if="!isListening && displayKeys.length > 0">
		<q-btn
			no-caps
			color="primary"
			@click="startListening()"
		>
			<div class="column">
				<span>
					Выбранные клавиши
				</span>
				<span>
					{{ displayKeys }}
				</span>
			</div>
		</q-btn>
	</template>
	<template v-else>
		<q-btn
			no-caps
			color="primary"
			v-if="!isListening"
			@click="startListening()"
		>
			Отследить клавишу
		</q-btn>
		<q-btn
			v-else
			no-caps
			color="primary"
			@click="stopListening()"
		>
			Нажмите клавишу
		</q-btn>
	</template>
</template>

<script setup>
import { useMagicKeys } from "@vueuse/core";
import { ref, watch, computed } from "vue";

const { current } = useMagicKeys();
const isListening = ref(false);
const pressedKeys = ref([]);

// Вычисляемое свойство для отображения клавиш
const displayKeys = computed(() => {

	return pressedKeys.value.join('+');
});

// Функция начала отслеживания
const startListening = () => {
	isListening.value = true;
	pressedKeys.value = [];
};

// Функция остановки отслеживания
const stopListening = () => {
	isListening.value = false;
};

// Отслеживаем нажатия клавиш
watch(current, (keys) => {
	if (isListening.value && keys.size > 0) {
		// Обновляем массив нажатых клавиш
		pressedKeys.value = Array.from(keys);

		// Автоматически останавливаем отслеживание
		setTimeout(() => {
			isListening.value = false;
		}, 150);
	}
}, { deep: true });
</script>