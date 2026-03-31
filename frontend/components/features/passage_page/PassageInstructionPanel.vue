<template>
	<div v-if="selectedStep" class="passage-instruction-panel">
		<div class="passage-instruction-panel__head">
			<q-icon name="assignment" size="18px" class="head-icon" />
			<span class="head-title">Задание</span>
		</div>
		<div
			v-if="sanitizedHtml"
			class="passage-instruction-panel__body instruction-html"
			v-html="sanitizedHtml"
		/>
		<div v-else-if="fallbackPlain" class="passage-instruction-panel__body passage-instruction-panel__body--plain">
			{{ fallbackPlain }}
		</div>
		<div v-else class="passage-instruction-panel__body text-grey-6">
			Задание не задано.
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { sanitizeInstructionHtml } from "@utils/sanitizeHtml.js";

const props = defineProps({
	selectedStep: { type: Object, default: null },
});

const sanitizedHtml = computed(() => {
	const raw = props.selectedStep?.instruction_html;
	if (!raw || typeof raw !== "string" || !raw.trim()) return "";
	return sanitizeInstructionHtml(raw);
});

function plainFromAnnotation(html) {
	if (!html || typeof html !== "string") return "";
	const t = html.trim();
	if (!t) return "";
	if (typeof document === "undefined") {
		return t.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
	}
	const d = document.createElement("div");
	d.innerHTML = t;
	return (d.textContent || "").replace(/\s+/g, " ").trim();
}

/** Если нет instruction_html — показываем текст из задания (annotation), не поля hint */
const fallbackPlain = computed(() => {
	if (sanitizedHtml.value) return "";
	return plainFromAnnotation(props.selectedStep?.annotation);
});
</script>

<style scoped>
.passage-instruction-panel {
	position: absolute;
	top: 72px;
	left: 16px;
	z-index: 6;
	width: min(360px, calc(100vw - 48px));
	max-height: min(42vh, 340px);
	display: flex;
	flex-direction: column;
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: blur(12px);
	-webkit-backdrop-filter: blur(12px);
	border-radius: 12px;
	box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
	border: 1px solid rgba(0, 0, 0, 0.06);
	overflow: hidden;
}

.passage-instruction-panel__head {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 12px;
	border-bottom: 1px solid rgba(0, 0, 0, 0.06);
	flex-shrink: 0;
}

.head-icon {
	color: var(--q-primary);
	opacity: 0.9;
}

.head-title {
	font-size: 13px;
	font-weight: 600;
	color: #1a1a2e;
}

.passage-instruction-panel__body {
	padding: 10px 12px;
	overflow-y: auto;
	font-size: 13px;
	line-height: 1.45;
	color: #334155;
}

.passage-instruction-panel__body--plain {
	white-space: pre-wrap;
}

.instruction-html :deep(h1),
.instruction-html :deep(h2),
.instruction-html :deep(h3) {
	margin: 0.4em 0 0.25em;
	font-weight: 600;
}

.instruction-html :deep(p) {
	margin: 0.35em 0;
}

.instruction-html :deep(ul),
.instruction-html :deep(ol) {
	margin: 0.35em 0;
	padding-left: 1.25rem;
}
</style>
