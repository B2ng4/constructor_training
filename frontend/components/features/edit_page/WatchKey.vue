<template>
	<q-dialog
		v-model="isListening"
		no-backdrop-dismiss
		no-esc-dismiss
	>
		<q-card class="watch-key-modal">
			<q-card-section class="text-center q-pb-none">
				<div class="watch-key-icon q-mx-auto q-mb-md">
					<q-icon name="keyboard" size="32px" color="primary" />
				</div>
				<div class="text-h6 text-weight-bold">
					Ожидание нажатия
				</div>
				<div class="text-body2 text-grey-6 q-mt-xs">
					Нажмите клавишу или комбинацию
				</div>
			</q-card-section>
			<q-card-section class="text-center">
				<div class="watch-key-value" :class="{ 'text-grey-5': !displayKeys }">
					{{ displayKeys || '...' }}
				</div>
			</q-card-section>
			<q-card-actions align="center" class="q-pb-md">
				<q-btn
					flat
					no-caps
					color="grey-7"
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

const displayKeys = computed(() => pressedKeys.value?.join(' + ') || '');

watch(isListening, (value) => {
	if (value) pressedKeys.value = [];
});

watch(current, (keys) => {
	if (isListening.value && keys.size > 0) {
		pressedKeys.value = Array.from(keys);
		setTimeout(() => { isListening.value = false; }, 150);
	}
}, { deep: true });
</script>

<style scoped>
.watch-key-modal {
	min-width: 340px;
	max-width: 90vw;
	border-radius: 16px;
}

.watch-key-icon {
	width: 64px;
	height: 64px;
	border-radius: 50%;
	background: rgba(80, 100, 247, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
}

.watch-key-value {
	font-size: 1.8rem;
	font-weight: 700;
	color: var(--q-primary);
	min-height: 2.2em;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(80, 100, 247, 0.06);
	border-radius: 12px;
	padding: 12px 20px;
}
</style>
