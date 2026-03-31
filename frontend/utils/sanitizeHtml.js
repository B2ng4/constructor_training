import DOMPurify from "dompurify";

const CONFIG = {
	ALLOWED_TAGS: [
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
	],
	ALLOWED_ATTR: [
		"href",
		"title",
		"target",
		"rel",
		"style",
		"class",
		"color",
		"face",
		"size",
		"start",
		"type",
		"value",
	],
	ADD_ATTR: ["target"],
};

/**
 * Двойная защита при отображении задания (сервер уже чистит через nh3).
 */
export function sanitizeInstructionHtml(html) {
	if (html == null || typeof html !== "string") return "";
	const trimmed = html.trim();
	if (!trimmed) return "";
	return DOMPurify.sanitize(trimmed, CONFIG);
}
