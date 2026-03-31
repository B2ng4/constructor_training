import DOMPurify from "dompurify";
import hljs from "highlight.js";
import { renderMarkdownToSafeHtml } from "./renderMarkdown.js";

const ANNOTATION_ALLOWED_TAGS = [
	"a",
	"b",
	"blockquote",
	"br",
	"code",
	"div",
	"em",
	"font",
	"h1",
	"h2",
	"h3",
	"h4",
	"h5",
	"h6",
	"hr",
	"i",
	"li",
	"mark",
	"ol",
	"p",
	"pre",
	"s",
	"span",
	"strong",
	"sub",
	"sup",
	"u",
	"ul",
	"label",
	"input",
];

const ANNOTATION_ALLOWED_ATTR = [
	"href",
	"title",
	"target",
	"rel",
	"style",
	"class",
	"color",
	"data-type",
	"data-checked",
	"type",
	"value",
];

function detectCodeLanguage(codeEl) {
	const cls = String(codeEl?.getAttribute("class") ?? "");
	const langFromPrefix = cls.match(/(?:^|\s)language-([a-z0-9_+-]+)/i)?.[1];
	if (langFromPrefix) return langFromPrefix.toLowerCase();
	const classParts = cls
		.split(/\s+/)
		.map((x) => x.trim().toLowerCase())
		.filter(Boolean);
	for (const part of classParts) {
		if (part !== "hljs") return part;
	}
	return "text";
}

function decorateCodeBlocks(html) {
	if (!html || typeof html !== "string") return "";
	if (typeof document === "undefined") return html;
	const root = document.createElement("div");
	root.innerHTML = html;
	const codeNodes = root.querySelectorAll("pre > code");

	codeNodes.forEach((codeEl) => {
		const pre = codeEl.parentElement;
		if (!pre) return;
		if (pre.parentElement?.classList?.contains("task-code-wrap")) return;
		let lang = detectCodeLanguage(codeEl);
		const source = String(codeEl.textContent ?? "");

		// Подсветка в preview/прохождении: приближаем внешний вид к редактору
		try {
			const langProvided = lang && lang !== "text";
			if (langProvided && hljs.getLanguage(lang)) {
				const res = hljs.highlight(source, { language: lang, ignoreIllegals: true });
				codeEl.innerHTML = res.value;
				codeEl.className = `hljs language-${lang}`;
			} else {
				const auto = hljs.highlightAuto(source);
				lang = auto.language || "text";
				codeEl.innerHTML = auto.value;
				codeEl.className = lang === "text" ? "hljs" : `hljs language-${lang}`;
			}
		} catch {
			// Если подсветка не сработала, оставляем исходный текст без падения рендера.
		}

		const wrap = document.createElement("div");
		wrap.className = "task-code-wrap";
		wrap.setAttribute("data-language", lang);

		const head = document.createElement("div");
		head.className = "task-code-head";

		const label = document.createElement("span");
		label.className = "task-code-lang";
		label.textContent = lang;

		const btn = document.createElement("button");
		btn.type = "button";
		btn.className = "task-code-copy-btn";
		btn.setAttribute("aria-label", "Скопировать код");
		btn.setAttribute("title", "Скопировать код");
		btn.textContent = "content_copy";

		head.append(label, btn);
		pre.replaceWith(wrap);
		wrap.append(head, pre);
	});

	return root.innerHTML;
}

/**
 * Рендер поля annotation: HTML из TipTap или устаревший Markdown.
 */
export function renderAnnotationToSafeHtml(raw) {
	if (raw == null) return "";
	const s = String(raw).trim();
	if (!s) return "";

	const looksLikeHtml =
		s.startsWith("<") &&
		(/<\/(p|h[1-6]|ul|ol|li|div|blockquote|pre)>/i.test(s) ||
			s.includes('data-type="taskList"') ||
			s.includes("<strong") ||
			s.includes("<br"));

	if (looksLikeHtml) {
		const safeHtml = DOMPurify.sanitize(s, {
			ALLOWED_TAGS: ANNOTATION_ALLOWED_TAGS,
			ALLOWED_ATTR: ANNOTATION_ALLOWED_ATTR,
			ALLOW_DATA_ATTR: true,
		});
		return decorateCodeBlocks(safeHtml);
	}

	return decorateCodeBlocks(renderMarkdownToSafeHtml(s));
}
