<template>
	<div v-if="editor" class="rich-task-editor">
		<div class="rich-task-editor__toolbar">
			<q-btn-toggle
				:model-value="headingLevel"
				flat
				dense
				no-caps
				size="sm"
				toggle-color="primary"
				color="grey-7"
				:options="[
					{ value: 'p', label: 'P' },
					{ value: 'h2', label: 'H2' },
					{ value: 'h3', label: 'H3' },
				]"
				@update:model-value="setHeading"
			/>
			<q-separator vertical inset class="q-mx-xs" />
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="format_bold"
				:color="editor.isActive('bold') ? 'primary' : 'grey-7'"
				@click="editor.chain().focus().toggleBold().run()"
			/>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="format_italic"
				:color="editor.isActive('italic') ? 'primary' : 'grey-7'"
				@click="editor.chain().focus().toggleItalic().run()"
			/>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="format_underlined"
				:color="editor.isActive('underline') ? 'primary' : 'grey-7'"
				@click="editor.chain().focus().toggleUnderline().run()"
			/>
			<q-separator vertical inset class="q-mx-xs" />
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="format_list_bulleted"
				:color="editor.isActive('bulletList') ? 'primary' : 'grey-7'"
				@click="editor.chain().focus().toggleBulletList().run()"
			/>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="format_list_numbered"
				:color="editor.isActive('orderedList') ? 'primary' : 'grey-7'"
				@click="editor.chain().focus().toggleOrderedList().run()"
			/>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="check_box"
				:color="editor.isActive('taskList') ? 'primary' : 'grey-7'"
				@click="editor.chain().focus().toggleTaskList().run()"
			/>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="keyboard"
				color="grey-7"
				@click="openHotkeyCapture"
			>
				<q-tooltip>Вставить сочетание клавиш</q-tooltip>
			</q-btn>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="code"
				:color="editor.isActive('codeBlock') ? 'primary' : 'grey-7'"
				@click="editor.chain().focus().toggleCodeBlock().run()"
			>
				<q-tooltip>Блок кода (язык определяется автоматически)</q-tooltip>
			</q-btn>
			<q-separator vertical inset class="q-mx-xs" />
			<q-btn flat dense round size="sm" icon="palette" color="grey-7">
				<q-menu anchor="bottom left" self="top left">
					<div class="q-pa-sm row q-gutter-xs" style="max-width: 200px">
						<q-btn
							v-for="c in palette"
							:key="c"
							round
							size="sm"
							:style="{ background: c }"
							@click="editor.chain().focus().setColor(c).run()"
						/>
					</div>
				</q-menu>
			</q-btn>
			<q-btn
				flat
				dense
				round
				size="sm"
				icon="highlight"
				:color="editor.isActive('highlight') ? 'primary' : 'grey-7'"
				@click="editor.chain().focus().toggleHighlight({ color: '#fef08a' }).run()"
			/>
		</div>
		<editor-content class="rich-task-editor__content" :editor="editor" />
		<watch-key
			v-model="capturedHotkey"
			v-model:open="isHotkeyDialogOpen"
		/>
	</div>
</template>

<script setup>
import { Color } from "@tiptap/extension-color";
import { Highlight } from "@tiptap/extension-highlight";
import { Link } from "@tiptap/extension-link";
import { Placeholder } from "@tiptap/extension-placeholder";
import { TaskItem } from "@tiptap/extension-task-item";
import { TaskList } from "@tiptap/extension-task-list";
import { TextStyle } from "@tiptap/extension-text-style";
import { Underline } from "@tiptap/extension-underline";
import { StarterKit } from "@tiptap/starter-kit";
import { EditorContent, useEditor } from "@tiptap/vue-3";
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { all, common, createLowlight } from "lowlight";
import { CodeBlockLowlightWithUI } from "./CodeBlockLowlightWithUI.js";
import WatchKey from "./WatchKey.vue";

const props = defineProps({
	modelValue: { type: String, default: "" },
	placeholder: { type: String, default: "Опишите задание: контекст, цель, что сделать…" },
});

const emit = defineEmits(["update:modelValue"]);
const lowlight = createLowlight(all);
const codeLanguageOptions = Object.keys(common).sort((a, b) => a.localeCompare(b));
const isHotkeyDialogOpen = ref(false);
const capturedHotkey = ref([]);

const palette = [
	"#0f172a",
	"#dc2626",
	"#ea580c",
	"#ca8a04",
	"#16a34a",
	"#2563eb",
	"#7c3aed",
	"#db2777",
];

function initialContent(html) {
	const s = (html || "").trim();
	if (!s) return "<p></p>";
	return s;
}

const editor = useEditor({
	content: initialContent(props.modelValue),
	extensions: [
		StarterKit.configure({
			heading: { levels: [2, 3] },
			codeBlock: false,
		}),
		CodeBlockLowlightWithUI.configure({
			lowlight,
			defaultLanguage: null,
			languageOptions: codeLanguageOptions,
		}),
		Underline,
		TextStyle,
		Color,
		Highlight.configure({ multicolor: true }),
		Link.configure({ openOnClick: false }),
		Placeholder.configure({ placeholder: props.placeholder }),
		TaskList,
		TaskItem.configure({ nested: true }),
	],
	editorProps: {
		attributes: {
			class: "rich-task-editor-prose",
		},
	},
	onUpdate: ({ editor: ed }) => {
		autoDetectCurrentCodeLanguage(ed);
		emit("update:modelValue", ed.getHTML());
	},
});

const headingLevel = computed(() => {
	if (!editor.value) return "p";
	if (editor.value.isActive("heading", { level: 2 })) return "h2";
	if (editor.value.isActive("heading", { level: 3 })) return "h3";
	return "p";
});

function setHeading(v) {
	if (!editor.value) return;
	const chain = editor.value.chain().focus();
	if (v === "h2") chain.toggleHeading({ level: 2 }).run();
	else if (v === "h3") chain.toggleHeading({ level: 3 }).run();
	else chain.setParagraph().run();
}

function normalizeHotkeyKeys(keys) {
	const aliases = {
		control: "Ctrl",
		ctrl: "Ctrl",
		shift: "Shift",
		alt: "Alt",
		meta: "Meta",
		cmd: "Meta",
		command: "Meta",
		enter: "Enter",
		escape: "Esc",
		esc: "Esc",
		arrowup: "Up",
		arrowdown: "Down",
		arrowleft: "Left",
		arrowright: "Right",
		" ": "Space",
		space: "Space",
	};
	return (keys || [])
		.map((k) => String(k || "").trim())
		.filter(Boolean)
		.map((k) => aliases[k.toLowerCase()] ?? (k.length === 1 ? k.toUpperCase() : k))
		.join(" + ");
}

function openHotkeyCapture() {
	isHotkeyDialogOpen.value = true;
}

function insertCapturedHotkey(keys) {
	if (!editor.value || !keys?.length) return;
	const label = normalizeHotkeyKeys(keys);
	if (!label) return;
	editor.value
		.chain()
		.focus()
		.insertContent(`<code>${label}</code>`)
		.insertContent(" ")
		.run();
}

let isUpdatingCodeAttrs = false;

function autoDetectCurrentCodeLanguage(ed) {
	if (isUpdatingCodeAttrs) return;
	const { $from } = ed.state.selection;
	const parent = $from.parent;
	if (!parent || parent.type.name !== "codeBlock") return;
	const currentLang = parent.attrs?.language;
	if (currentLang) return;
	const code = String(parent.textContent ?? "").trim();
	if (code.length < 2) return;

	const result = lowlight.highlightAuto(code);
	const detected = result?.data?.language;
	if (!detected) return;

	isUpdatingCodeAttrs = true;
	ed.chain().focus().updateAttributes("codeBlock", { language: detected }).run();
	isUpdatingCodeAttrs = false;
}

watch(
	() => props.modelValue,
	(val) => {
		if (!editor.value) return;
		const current = editor.value.getHTML();
		const next = initialContent(val);
		if (next === current || val === current) return;
		editor.value.commands.setContent(next, false);
	}
);

watch(
	() => isHotkeyDialogOpen.value,
	(isOpen, wasOpen) => {
		if (wasOpen && !isOpen && capturedHotkey.value?.length) {
			insertCapturedHotkey(capturedHotkey.value);
			capturedHotkey.value = [];
		}
	}
);

onBeforeUnmount(() => {
	editor.value?.destroy();
});
</script>

<style>
.rich-task-editor {
	border: 1px solid rgba(15, 23, 42, 0.12);
	border-radius: 12px;
	overflow: hidden;
	background: #fff;
}

.rich-task-editor__toolbar {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 2px;
	padding: 8px 10px;
	border-bottom: 1px solid rgba(15, 23, 42, 0.08);
	background: #f8fafc;
}

.rich-task-editor__content {
	max-height: min(48vh, 420px);
	min-height: 220px;
	overflow-y: auto;
	padding: 16px 18px;
}

.rich-task-editor-prose {
	outline: none;
	min-height: 180px;
	font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
	font-size: 18px;
	line-height: 1.65;
	font-weight: 400;
	color: #0f172a;
	letter-spacing: 0.01em;
}

.rich-task-editor-prose p {
	margin: 0 0 0.7em;
}

.rich-task-editor-prose h2 {
	font-size: 1.35em;
	font-weight: 700;
	margin: 0.65em 0 0.4em;
	letter-spacing: -0.02em;
}

.rich-task-editor-prose h3 {
	font-size: 1.2em;
	font-weight: 700;
	margin: 0.55em 0 0.35em;
	letter-spacing: -0.015em;
}

.rich-task-editor-prose ul,
.rich-task-editor-prose ol {
	padding-left: 1.35em;
	margin: 0.4em 0 0.65em;
}

.rich-task-editor-prose li {
	margin: 0.2em 0;
}

.rich-task-editor-prose ul[data-type="taskList"] {
	list-style: none;
	padding-left: 0;
}

.rich-task-editor-prose ul[data-type="taskList"] li {
	display: flex;
	align-items: flex-start;
	gap: 8px;
}

.rich-task-editor-prose pre {
	background: #0f172a;
	color: #e2e8f0;
	padding: 12px 14px;
	border-radius: 8px;
	font-size: 14px;
	line-height: 1.5;
	overflow-x: auto;
}

.rich-task-editor-prose code {
	background: rgba(15, 23, 42, 0.06);
	padding: 0.12em 0.4em;
	border-radius: 4px;
	font-size: 0.88em;
}

.rich-task-editor-prose .ProseMirror p.is-editor-empty:first-child::before {
	color: #94a3b8;
	content: attr(data-placeholder);
	float: left;
	height: 0;
	pointer-events: none;
}
</style>
