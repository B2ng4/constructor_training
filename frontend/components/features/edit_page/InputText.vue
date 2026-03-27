<template>
	<div
		ref="rootRef"
		class="input-text-stack"
		:class="{ 'input-text-stack--focused': focused }"
		@click="focusInput"
	>
		<q-tooltip
			anchor="center right"
			self="center left"
			:offset="[10, 0]"
			max-width="280px"
		>
			Ожидаемый текст в этом месте — укажите точную строку.
		</q-tooltip>
		<textarea
			ref="inputRef"
			v-model="model"
			class="input-text-field"
			:style="fontStyle"
			spellcheck="false"
			autocomplete="off"
			aria-label="Ожидаемый текст для проверки при прохождении"
			placeholder="Введите ожидаемый текст…"
			@focus="focused = true"
			@blur="onBlurInput"
		/>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue";

const model = defineModel({ type: String, default: () => "" });

const rootRef = ref(null);
const inputRef = ref(null);
const focused = ref(false);

const fontSizePx = ref(14);

const fontStyle = computed(() => ({
	fontSize: `${fontSizePx.value}px`,
	lineHeight: 1.2,
}));

let resizeObserver = null;

function measureFont() {
	const el = rootRef.value;
	if (!el) return;
	const h = el.getBoundingClientRect().height || 0;
	const fs = Math.round(Math.max(11, Math.min(26, h * 0.38)));
	fontSizePx.value = fs || 14;
}

function focusInput() {
	inputRef.value?.focus?.();
}

function onBlurInput(e) {
	focused.value = false;
	const el = e?.target ?? inputRef.value;
	if (!el) return;
	// После завершения ввода показываем текст с начала,
	// чтобы была видна вся строка/первые строки, а не «хвост».
	el.scrollLeft = 0;
	el.scrollTop = 0;
}

onMounted(() => {
	measureFont();
	if (typeof ResizeObserver !== "undefined" && rootRef.value) {
		resizeObserver = new ResizeObserver(() => measureFont());
		resizeObserver.observe(rootRef.value);
	}
	nextTick(() => {
		measureFont();
		inputRef.value?.focus?.();
	});
});

onUnmounted(() => {
	resizeObserver?.disconnect();
});

defineExpose({ focus: focusInput });
</script>

<style scoped>
.input-text-stack {
	position: relative;
	width: 100%;
	height: 100%;
	min-height: 0;
	min-width: 0;
	box-sizing: border-box;
	cursor: text;
}

.input-text-stack::before {
	content: "";
	position: absolute;
	inset: 0;
	border-radius: 4px;
	background: rgba(0, 0, 0, 0.32);
	pointer-events: none;
	z-index: 0;
	transition: background 0.2s ease, box-shadow 0.2s ease;
}

.input-text-stack--focused::before {
	background: rgba(0, 0, 0, 0.42);
	box-shadow:
		inset 0 0 0 1px rgba(255, 255, 255, 0.22),
		0 0 0 2px rgba(97, 240, 255, 0.45);
}

.input-text-field {
	position: relative;
	z-index: 1;
	width: 100%;
	height: 100%;
	min-height: 0;
	margin: 0;
	border: none;
	border-radius: 0;
	background: transparent !important;
	color: #f8fafc;
	outline: none;
	padding: 2px 4px;
	box-sizing: border-box;
	font-family: ui-monospace, "Cascadia Code", "Segoe UI", system-ui, sans-serif;
	font-weight: 500;
	letter-spacing: 0.01em;
	caret-color: #61f0ff;
	text-shadow:
		0 0 1px rgba(0, 0, 0, 1),
		0 0 4px rgba(0, 0, 0, 0.95),
		0 1px 2px rgba(0, 0, 0, 1),
		0 0 14px rgba(0, 0, 0, 0.85);
	overflow: auto;
	resize: none;
	white-space: pre-wrap;
	word-break: break-word;
}

.input-text-field::placeholder {
	color: rgba(248, 250, 252, 0.55);
	font-style: italic;
	text-shadow: none;
}

.input-text-field::selection {
	background: rgba(97, 240, 255, 0.35);
}

.input-text-field:focus {
	outline: none;
}
</style>
