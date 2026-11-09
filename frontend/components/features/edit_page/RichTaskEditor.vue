<template>
	<div v-if="editor" class="rich-task-editor">
		<div class="rich-task-editor__toolbar glass-pill">
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
	display: flex;
	flex-direction: column;
	border: none;
	background: transparent;
	overflow: visible; /* To allow floating toolbar */
}

.rich-task-editor__toolbar {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 6px;
	padding: 8px 18px;
	margin-bottom: 20px;
	position: sticky;
	top: 0;
	z-index: 10;
	width: fit-content;
}

.rich-task-editor__content {
	flex: 1;
	background: rgba(255, 255, 255, 0.5);
	backdrop-filter: blur(8px);
	border: 1px solid rgba(15, 23, 42, 0.08);
	border-radius: 16px;
	padding: 20px 24px;
	transition: all 0.3s ease;
	min-height: 280px;
}

.rich-task-editor__content:focus-within {
	background: rgba(255, 255, 255, 0.7);
	border-color: rgba(99, 102, 241, 0.3);
	box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.05);
}

.rich-task-editor-prose {
	outline: none;
	font-family: var(--font-sans);
	font-size: 18px;
	line-height: 1.7;
	color: #1e293b;
	letter-spacing: -0.01em;
}

.rich-task-editor-prose h2 {
	font-size: 1.5em;
	font-weight: 800;
	margin: 1.2em 0 0.5em;
	color: #0f172a;
}

.rich-task-editor-prose pre {
	background: #0f172a;
	color: #f8fafc;
	padding: 16px;
	border-radius: 12px;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rich-task-editor-prose .ProseMirror p.is-editor-empty:first-child::before {
	color: #94a3b8;
	font-style: italic;
	font-weight: 400;
}
</style>
