<template>
	<div v-if="selectedStep" class="passage-task-panel">
		<div class="passage-task-panel__head">
			<q-icon name="assignment" size="18px" class="passage-task-panel__icon" />
			<span class="passage-task-panel__short">{{ shortTitle }}</span>
		</div>
		<div
			v-if="htmlContent"
			class="passage-task-panel__body task-html-body"
			v-html="htmlContent"
		/>
		<div v-else class="passage-task-panel__empty text-grey-6">
			Текст задания не заполнен. Отредактируйте шаг в конструкторе.
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { renderAnnotationToSafeHtml } from "@utils/renderAnnotationHtml.js";

const props = defineProps({
	selectedStep: { type: Object, default: null },
});

const shortTitle = computed(() => {
	const s = props.selectedStep;
	if (!s) return "";
	const n = (s.meta?.name ?? "").trim();
	if (n && n !== "Шаг без названия") return n;
	return `Шаг ${s.step_number ?? ""}`.trim();
});

const htmlContent = computed(() => {
	const raw = props.selectedStep?.annotation;
	return renderAnnotationToSafeHtml(raw);
});
</script>

<style scoped>
.passage-task-panel {
	display: flex;
	flex-direction: column;
	min-height: 0;
	flex: 1;
	background: #fafbfc;
	border-left: 1px solid rgba(15, 23, 42, 0.08);
	overflow: hidden;
}

.passage-task-panel__head {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 16px 18px 12px;
	flex-shrink: 0;
	border-bottom: 1px solid rgba(0, 0, 0, 0.06);
	background: #fff;
}

.passage-task-panel__icon {
	color: var(--q-primary);
	opacity: 0.85;
	flex-shrink: 0;
}

.passage-task-panel__short {
	font-size: 17px;
	font-weight: 700;
	color: #0f172a;
	line-height: 1.4;
}

.passage-task-panel__body {
	padding: 20px 22px 28px;
	overflow-y: auto;
	flex: 1;
	min-height: 0;
	font-size: 18px;
	line-height: 1.72;
	color: #1e293b;
	letter-spacing: 0.005em;
}

.passage-task-panel__empty {
	padding: 20px 22px;
	font-size: 15px;
	line-height: 1.55;
}

.task-html-body :deep(p) {
	margin: 0 0 0.75em;
}

.task-html-body :deep(p:last-child) {
	margin-bottom: 0;
}

.task-html-body :deep(ul),
.task-html-body :deep(ol) {
	margin: 0.5em 0 0.75em;
	padding-left: 1.35em;
}

.task-html-body :deep(li) {
	margin: 0.25em 0;
}

.task-html-body :deep(h2) {
	font-size: 1.35em;
	font-weight: 700;
	margin: 0.75em 0 0.4em;
	color: #0f172a;
}

.task-html-body :deep(h3) {
	font-size: 1.2em;
	font-weight: 700;
	margin: 0.65em 0 0.35em;
	color: #0f172a;
}

.task-html-body :deep(strong) {
	font-weight: 700;
	color: #0f172a;
}

.task-html-body :deep(code) {
	font-family: ui-monospace, monospace;
	font-size: 0.9em;
	background: rgba(15, 23, 42, 0.06);
	padding: 0.1em 0.35em;
	border-radius: 4px;
}

.task-html-body :deep(pre) {
	background: #0f172a;
	color: #e2e8f0;
	padding: 10px 12px;
	border-radius: 8px;
	overflow-x: auto;
	font-size: 0.9em;
	margin: 0.5em 0;
}

@media (max-width: 1200px) {
	.passage-task-panel__body {
		font-size: 17px;
	}
}

.task-html-body :deep(pre code) {
	background: none;
	padding: 0;
	color: inherit;
}

.task-html-body :deep(mark) {
	background: rgba(254, 240, 138, 0.85);
	padding: 0.05em 0.15em;
	border-radius: 2px;
}

.task-html-body :deep(a) {
	color: var(--q-primary);
	text-decoration: underline;
	text-underline-offset: 2px;
}

.task-html-body :deep(ul[data-type="taskList"]) {
	list-style: none;
	padding-left: 0;
}

.task-html-body :deep(ul[data-type="taskList"] li) {
	display: flex;
	align-items: flex-start;
	gap: 8px;
}
</style>
