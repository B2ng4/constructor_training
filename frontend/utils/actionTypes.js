/**
 * Единые правила по типам действий для редактирования и прохождения.
 * Типы должны совпадать с backend scripts/create_initial_actions.py
 */
export const ACTION_TYPES = {
	LEFT_CLICK: "leftClick",
	RIGHT_CLICK: "rightClick",
	DOUBLE_CLICK: "doubleClick",
	HOVER: "hover",
	INPUT_TEXT: "inputText",
	KEY_PRESS: "keyPress",
};

/** Действия, для которых нужно рисовать область на скриншоте (x, y, width, height) */
const TYPES_REQUIRING_AREA_COORDS = [
	ACTION_TYPES.LEFT_CLICK,
	ACTION_TYPES.RIGHT_CLICK,
	ACTION_TYPES.DOUBLE_CLICK,
	ACTION_TYPES.HOVER,
	ACTION_TYPES.INPUT_TEXT,
];

/** Действия, которые проверяются кликом/движением мыши по области */
const TYPES_VALIDATED_BY_CLICK = [
	ACTION_TYPES.LEFT_CLICK,
	ACTION_TYPES.RIGHT_CLICK,
	ACTION_TYPES.DOUBLE_CLICK,
	ACTION_TYPES.HOVER,
];

/**
 * Нужно ли для данного типа действия рисовать область на изображении.
 * keyPress — только метаданные (metaKeywords), без координат.
 */
export function eventRequiresArea(event) {
	if (!event?.type) return false;
	return TYPES_REQUIRING_AREA_COORDS.includes(event.type);
}

/**
 * Нужны ли для сохранения координаты области (x, y, width, height).
 * keyPress — нет, только metaKeywords.
 */
export function eventRequiresAreaCoordinates(event) {
	if (!event?.type) return false;
	return TYPES_REQUIRING_AREA_COORDS.includes(event.type);
}

/** Является ли тип «нажатие клавиши» (сохраняем только metaKeywords) */
export function isKeyPressType(event) {
	return event?.type === ACTION_TYPES.KEY_PRESS;
}

/** Является ли тип «ввод текста» (область + metaText) */
export function isInputTextType(event) {
	return event?.type === ACTION_TYPES.INPUT_TEXT;
}

/** Проверяется ли в прохождении по клику/движению мыши по области */
export function isClickValidatedType(event) {
	return event && TYPES_VALIDATED_BY_CLICK.includes(event.type);
}
