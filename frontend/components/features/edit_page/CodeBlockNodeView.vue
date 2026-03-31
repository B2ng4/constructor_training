<template>
	<NodeViewWrapper class="tt-codeblock">
		<div class="tt-codeblock__head" contenteditable="false">
			<select
				class="tt-codeblock__lang-select"
				:value="selectedLanguage"
				@change="onLanguageChange"
			>
				<option value="">auto</option>
				<option v-for="lang in languages" :key="lang" :value="lang">
					{{ lang }}
				</option>
			</select>
			<div class="tt-codeblock__actions">
				<button
					type="button"
					class="tt-codeblock__copy-btn"
					title="Скопировать код"
					aria-label="Скопировать код"
					@click="copyCode"
				>
					content_copy
				</button>
				<button
					type="button"
					class="tt-codeblock__delete-btn"
					title="Удалить блок кода"
					aria-label="Удалить блок кода"
					@click="removeCodeBlock"
				>
					delete
				</button>
			</div>
		</div>
		<pre class="tt-codeblock__pre"><NodeViewContent as="code" class="tt-codeblock__code" /></pre>
	</NodeViewWrapper>
</template>

<script setup>
import { computed } from "vue";
import { NodeViewContent, NodeViewWrapper } from "@tiptap/vue-3";

const props = defineProps({
	node: { type: Object, required: true },
	updateAttributes: { type: Function, required: true },
	extension: { type: Object, required: true },
	deleteNode: { type: Function, required: true },
});

const languages = computed(() =>
	Array.isArray(props.extension?.options?.languageOptions)
		? props.extension.options.languageOptions
		: []
);

const selectedLanguage = computed(() => String(props.node?.attrs?.language ?? ""));

function onLanguageChange(e) {
	const lang = String(e?.target?.value ?? "").trim();
	props.updateAttributes({ language: lang || null });
}

async function copyCode() {
	const text = String(props.node?.textContent ?? "");
	if (!text.trim()) return;
	try {
		if (navigator?.clipboard?.writeText) {
			await navigator.clipboard.writeText(text);
			return;
		}
		const ta = document.createElement("textarea");
		ta.value = text;
		ta.style.position = "fixed";
		ta.style.left = "-9999px";
		document.body.appendChild(ta);
		ta.select();
		document.execCommand("copy");
		ta.remove();
	} catch {
		// intentionally silent in node view
	}
}

function removeCodeBlock() {
	props.deleteNode();
}
</script>

<style scoped>
.tt-codeblock {
	margin: 0.6em 0 0.9em;
	border: 1px solid rgba(15, 23, 42, 0.15);
	border-radius: 10px;
	overflow: hidden;
	background: #0f172a;
}

.tt-codeblock__head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 8px;
	padding: 6px 10px;
	background: rgba(2, 6, 23, 0.9);
	border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}

.tt-codeblock__actions {
	display: inline-flex;
	align-items: center;
	gap: 2px;
}

.tt-codeblock__lang-select {
	border: 1px solid rgba(148, 163, 184, 0.3);
	border-radius: 6px;
	background: rgba(15, 23, 42, 0.8);
	color: #cbd5e1;
	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
	font-size: 12px;
	line-height: 1.2;
	padding: 2px 8px;
	outline: none;
}

.tt-codeblock__copy-btn {
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

.tt-codeblock__copy-btn:hover {
	background: rgba(148, 163, 184, 0.25);
}

.tt-codeblock__delete-btn {
	border: 0;
	background: transparent;
	color: #fca5a5;
	cursor: pointer;
	font-family: "Material Symbols Outlined", "Material Icons", sans-serif;
	font-size: 18px;
	line-height: 1;
	padding: 2px 4px;
	border-radius: 4px;
}

.tt-codeblock__delete-btn:hover {
	background: rgba(248, 113, 113, 0.2);
	color: #fecaca;
}

.tt-codeblock__pre {
	margin: 0;
	padding: 12px 14px;
	overflow-x: auto;
}

.tt-codeblock__code {
	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
	font-size: 14px;
	line-height: 1.5;
}
</style>
