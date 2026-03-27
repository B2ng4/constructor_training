import DOMPurify from "dompurify";
import MarkdownIt from "markdown-it";

const md = new MarkdownIt({
	html: false,
	linkify: true,
	breaks: true,
	typographer: true,
});

function normalizeMarkdownLikeText(src) {
	let s = String(src ?? "").trim();
	if (!s) return "";
	// Экранированные переносы из AI-ответов.
	s = s.replace(/\\r\\n/g, "\n").replace(/\\n/g, "\n");
	// Заголовки, склеенные в одну строку.
	s = s.replace(/\s*(##\s+)/g, "\n\n$1");
	s = s.replace(/(##\s*(?:Цель|Действие|Контекст|Результат|Шаг))\s+/g, "$1\n\n");
	// Пункты списка, склеенные в строку.
	s = s.replace(/\s-\s/g, "\n- ");
	// Частые HTML-break от моделей.
	s = s.replace(/<br\s*\/?>/gi, "\n");
	s = s.replace(/\n{3,}/g, "\n\n").trim();
	return s;
}

/**
 * Рендер Markdown в безопасный HTML для v-html.
 */
export function renderMarkdownToSafeHtml(src) {
	if (src == null) return "";
	const s = normalizeMarkdownLikeText(src);
	if (!s) return "";
	return DOMPurify.sanitize(md.render(s));
}
