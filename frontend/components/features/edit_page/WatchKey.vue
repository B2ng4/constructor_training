<template>
	<q-dialog
		v-model="isListening"
		no-backdrop-dismiss
		no-esc-dismiss
	>
		<q-card class="watch-key-modal">
			<q-card-section class="text-center">
				<div class="text-subtitle1">
					Ожидание нажатия клавиши
				</div>
				<div class="text-caption text-grey-7 q-mt-xs">
					Нажмите нужную клавишу или комбинацию
				</div>
				<div class="watch-key-value q-mt-md">
					{{ displayKeys || '...' }}
				</div>
			</q-card-section>
			<q-card-actions align="right">
				<q-btn
					flat
					color="primary"
					label="Отмена"
					@click="isListening = false"
				/>
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { useMagicKeys } from "@vueuse/core";
import { computed, watch } from "vue";

const { current } = useMagicKeys();
const isListening = defineModel('open', { default: false });
const pressedKeys = defineModel({ default: () => [] });

const displayKeys = computed(() => {
	return pressedKeys.value?.join('+') || '';
});

watch(isListening, (value) => {
	if (value) {
		pressedKeys.value = [];
	}
});

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
.watch-key-modal {
	min-width: 340px;
	max-width: 90vw;
}

.watch-key-value {
	font-size: 1.4rem;
	font-weight: 600;
}
</style>