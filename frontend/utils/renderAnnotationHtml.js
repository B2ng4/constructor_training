import DOMPurify from "dompurify";
import { renderMarkdownToSafeHtml } from "./renderMarkdown.js";

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
		return DOMPurify.sanitize(s, {
			ADD_TAGS: [
				"mark",
				"span",
				"s",
				"u",
				"label",
				"input",
			],
			ADD_ATTR: [
				"style",
				"class",
				"data-type",
				"data-checked",
				"type",
			],
			ALLOW_DATA_ATTR: true,
		});
	}

	return renderMarkdownToSafeHtml(s);
}
