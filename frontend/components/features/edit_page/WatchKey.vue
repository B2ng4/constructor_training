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
import { computed, onBeforeUnmount, watch } from "vue";

const isListening = defineModel('open', { default: false });
const pressedKeys = defineModel({ default: () => [] });

const displayKeys = computed(() => pressedKeys.value?.join(' + ') || '');

const MODIFIER_KEYS = new Set(["ctrl", "control", "shift", "alt", "meta"]);
let finalizeTimer = null;

function normalizeKeyName(raw) {
	const s = String(raw ?? "").trim().toLowerCase();
	const aliases = {
		control: "ctrl",
		" ": "space",
		arrowup: "up",
		arrowdown: "down",
		arrowleft: "left",
		arrowright: "right",
		escape: "esc",
	};
	return aliases[s] ?? s;
}

function buildComboFromEvent(e) {
	const parts = [];
	if (e.ctrlKey) parts.push("ctrl");
	if (e.altKey) parts.push("alt");
	if (e.shiftKey) parts.push("shift");
	if (e.metaKey) parts.push("meta");

	const main = normalizeKeyName(e.key);
	if (main && !MODIFIER_KEYS.has(main)) {
		parts.push(main);
	}
	return parts;
}

function onKeyDown(e) {
	if (!isListening.value) return;
	e.preventDefault();
	e.stopPropagation();

	const combo = buildComboFromEvent(e);
	if (!combo.length) return;
	pressedKeys.value = combo;

	const hasMainKey = combo.some((k) => !MODIFIER_KEYS.has(k));
	if (!hasMainKey) return;

	if (finalizeTimer) clearTimeout(finalizeTimer);
	finalizeTimer = setTimeout(() => {
		finalizeTimer = null;
		isListening.value = false;
	}, 220);
}

function onKeyUp(e) {
	if (!isListening.value) return;
	e.preventDefault();
	e.stopPropagation();
}

watch(isListening, (value) => {
	if (value) {
		pressedKeys.value = [];
		window.addEventListener("keydown", onKeyDown, true);
		window.addEventListener("keyup", onKeyUp, true);
		return;
	}
	window.removeEventListener("keydown", onKeyDown, true);
	window.removeEventListener("keyup", onKeyUp, true);
	if (finalizeTimer) {
		clearTimeout(finalizeTimer);
		finalizeTimer = null;
	}
});

onBeforeUnmount(() => {
	window.removeEventListener("keydown", onKeyDown, true);
	window.removeEventListener("keyup", onKeyUp, true);
	if (finalizeTimer) {
		clearTimeout(finalizeTimer);
		finalizeTimer = null;
	}
});
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
