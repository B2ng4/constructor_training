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
			@click="onTaskBodyClick"
		></div>
		<div v-else class="passage-task-panel__empty text-grey-6">
			Текст задания не заполнен. Отредактируйте шаг в конструкторе.
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue";
import { useQuasar } from "quasar";
import { renderAnnotationToSafeHtml } from "@utils/renderAnnotationHtml.js";

const props = defineProps({
	selectedStep: { type: Object, default: null },
});
const $q = useQuasar();

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

async function copyCodeFromEvent(e) {
	const btn = e?.target?.closest?.(".task-code-copy-btn");
	if (!btn) return false;
	const wrap = btn.closest(".task-code-wrap");
	const codeEl = wrap?.querySelector?.("pre code");
	const text = codeEl?.textContent ?? "";
	if (!text.trim()) return true;
	try {
		if (navigator?.clipboard?.writeText) {
			await navigator.clipboard.writeText(text);
		} else {
			const ta = document.createElement("textarea");
			ta.value = text;
			ta.style.position = "fixed";
			ta.style.left = "-9999px";
			document.body.appendChild(ta);
			ta.select();
			document.execCommand("copy");
			ta.remove();
		}
		$q.notify({ color: "positive", message: "Код скопирован", position: "top", timeout: 900 });
	} catch {
		$q.notify({ color: "negative", message: "Не удалось скопировать код", position: "top" });
	}
	return true;
}

function onTaskBodyClick(e) {
	void copyCodeFromEvent(e);
}
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
	font-size: 20px;
	font-weight: 800;
	color: #0f172a;
	line-height: 1.35;
	letter-spacing: -0.02em;
}

.passage-task-panel__body {
	padding: 22px 24px 32px;
	overflow-y: auto;
	flex: 1;
	min-height: 0;
	font-size: 20px;
	line-height: 1.75;
	color: #0f172a;
	font-weight: 400;
	letter-spacing: 0.012em;
}

.passage-task-panel__empty {
	padding: 22px 24px;
	font-size: 16px;
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
	font-size: 1.4em;
	font-weight: 800;
	margin: 0.7em 0 0.4em;
	color: #020617;
	letter-spacing: -0.02em;
}

.task-html-body :deep(h3) {
	font-size: 1.25em;
	font-weight: 700;
	margin: 0.6em 0 0.35em;
	color: #0f172a;
	letter-spacing: -0.015em;
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
		font-size: 18px;
	}

	.passage-task-panel__short {
		font-size: 18px;
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

.task-html-body :deep(.task-code-wrap) {
	margin: 0.6em 0 0.9em;
	border: 1px solid rgba(15, 23, 42, 0.15);
	border-radius: 10px;
	overflow: hidden;
	background: #0f172a;
}

.task-html-body :deep(.task-code-head) {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 6px 10px;
	background: rgba(2, 6, 23, 0.9);
	border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}

.task-html-body :deep(.task-code-lang) {
	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
	font-size: 12px;
	line-height: 1.2;
	color: #cbd5e1;
	text-transform: lowercase;
	letter-spacing: 0.03em;
}

.task-html-body :deep(.task-code-copy-btn) {
	border: 0;
	background: transparent;
	color: #e2e8f0;
	cursor: pointer;
	font-family: "Material Symbols Outlined", "Material Icons", sans-serif;
	font-size: 18px;
	line-height: 1;
	padding: 2px 4px;
	border-radius: 4px;
}

.task-html-body :deep(.task-code-copy-btn:hover) {
	background: rgba(148, 163, 184, 0.25);
}
</style>
