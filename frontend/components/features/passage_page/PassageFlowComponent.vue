<template>
	<div ref="flowRef" class="passage-flow">
		<div v-if="selectedStep?.image_url" class="flow-inner">
			<!-- Скриншот: зум + пан как в редакторе; в режиме прохождения область не показываем -->
			<div
				ref="imageWrapRef"
				class="screenshot-wrap"
				:class="{
					'screenshot-wrap--clickable': isPassageMode && canClickToValidate,
					'screenshot-wrap--zoomed': zoom > 1,
					'screenshot-wrap--panning': isPanning,
				}"
				@wheel.prevent="onWheel"
				@mousedown="onWrapMouseDown"
				@click="onWrapClick"
				@dblclick="onWrapDblClick"
				@contextmenu.prevent="onWrapContextMenu"
				@mouseenter="onWrapMouseEnter"
				@mouseleave="onWrapMouseLeave"
				@mousemove="onWrapMouseMove"
			>
				<div
					v-if="showViewportHint"
					class="viewport-hint"
					role="note"
					@click.stop
				>
					<q-icon name="open_with" size="18px" />
					<span>Масштаб: колесо мыши. Перемещение: зажмите среднюю кнопку (или ЛКМ при зуме).</span>
					<q-btn
						flat
						dense
						round
						size="sm"
						icon="close"
						color="white"
						@click="dismissViewportHint"
					/>
				</div>
				<div
					ref="screenshotAspectRef"
					class="screenshot-aspect"
					:style="screenshotAspectStyle"
				>
					<div
						ref="zoomPanRef"
						class="screenshot-zoom-pan"
						:style="zoomPanStyle"
					>
						<img
							ref="imgRef"
							:src="displayScreenshotUrl"
							alt=""
							class="screenshot-img"
							:class="{ 'screenshot-img--outcome': !!forcedAfterUrl }"
							draggable="false"
							@load="updateImageContentLayout"
						/>
					<!-- Область действия: при включённых подсказках после ошибки — подсветка / автозаполнение текста -->
					<div
						v-if="showAreaVisible && area && (area.width > 0 && area.height > 0)"
						class="action-area"
						:class="[
							areaClass,
							{
								'action-area--text-bare': isInputText && isPassageMode,
								'action-area--hint-pulse':
									isPassageMode && showHintHighlight && !isInputText,
								'action-area--text-hint-pulse':
									isPassageMode && showHintHighlight && isInputText,
							},
						]"
						:style="areaStyle"
						@click.stop="onAreaClick"
						@dblclick.stop="onAreaDblClick"
						@contextmenu.prevent.stop="onAreaContextMenu"
						@mouseenter="onAreaMouseEnter"
						@mouseleave="onAreaMouseLeave"
					>
						<div
							v-if="isInputText && isPassageMode"
							class="overlay-input-wrap"
							@click.stop
						>
							<div class="overlay-input-stack">
								<div
									class="overlay-text-mirror"
									:class="{ 'overlay-text-mirror--hint-type': isHintTyping }"
									:style="overlayInputStyle"
									aria-hidden="true"
								>
									{{ overlayDisplayValue }}<span
										v-if="isHintTyping"
										class="overlay-typewriter-caret"
									/>
								</div>
								<textarea
									ref="overlayInputRef"
									v-model="inputValue"
									class="overlay-input overlay-input--ghost-text"
									:class="{ 'overlay-input--hint-typing': isHintTyping }"
									:style="overlayInputStyle"
									wrap="off"
									autocomplete="off"
									spellcheck="false"
									aria-label="Ввод текста по заданию"
									placeholder=""
									@input="onOverlayInput"
									@scroll="onOverlayScroll"
									@paste="onOverlayPaste"
									@keydown="onOverlayKeydown"
									@blur="onOverlayBlur"
								/>
							</div>
						</div>
						<template v-else>
							<div v-if="!isPassageMode && isKeyPress" class="area-hint">
								<q-icon name="keyboard" size="20px" />
								<span>Нажмите: {{ hotkeyLabel }}</span>
							</div>
							<div v-else-if="!isPassageMode && isInputText" class="area-hint">
								<q-icon name="edit" size="20px" />
								<span>Укажите ожидаемый текст в панели и сохраните</span>
							</div>
						</template>
					</div>
					</div>
				</div>
			</div>

			<!-- Резервное поле ввода, если оверлей недоступен (не passage) -->
			<div v-if="isInputText && area && !isPassageMode" class="input-text-panel">
				<q-input
					ref="inputRef"
					v-model="inputValue"
					outlined
					dense
					placeholder="Введите текст сюда"
					class="input-field"
					@keyup.enter="checkInputText"
				>
					<template #append>
						<q-btn
							flat
							dense
							round
							icon="check"
							color="primary"
							@click="checkInputText"
						/>
					</template>
				</q-input>
			</div>

		</div>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";

const OUTCOME_FRAME_HOLD_MS = 620;

function delay(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

function preloadImage(src) {
	if (!src) return Promise.resolve();
	return new Promise((resolve) => {
		const im = new Image();
		im.onload = () => resolve();
		im.onerror = () => resolve();
		im.src = src;
	});
}

function stepAfterImageUrl(step) {
	const m = step?.meta;
	if (m && typeof m === "object" && typeof m.image_url_after === "string") {
		const u = m.image_url_after.trim();
		return u || "";
	}
	return "";
}
import {
	eventRequiresArea,
	isKeyPressType,
	isInputTextType,
	isClickValidatedType,
} from "@utils/actionTypes.js";

const props = defineProps({
	selectedStep: { type: Object, default: null },
	mode: { type: String, default: "passage" }, // passage | edit
	/** После нескольких ошибок: подсветка области или автоподстановка текста */
	showHintHighlight: { type: Boolean, default: false },
});

const emit = defineEmits(["action-complete", "action-wrong"]);

const flowRef = ref(null);
const imageWrapRef = ref(null);
const screenshotAspectRef = ref(null);
const zoomPanRef = ref(null);
const imgRef = ref(null);
const inputRef = ref(null);
const overlayInputRef = ref(null);
const inputValue = ref("");
const hintMaskValue = ref("");
/** Идёт анимация печати подсказки */
const isHintTyping = ref(false);
let hintTypewriterTimer = null;
/** Чтобы @input не отменял печать подсказки при программной подстановке */
let inputFromTypewriter = false;
const hoverTimer = ref(null);
const showViewportHint = ref(true);
/** После верного действия: кадр «после» из AI до перехода на следующий шаг */
const forcedAfterUrl = ref(null);
const outcomeBusy = ref(false);

const displayScreenshotUrl = computed(
	() => forcedAfterUrl.value || props.selectedStep?.image_url || ""
);

/** Зум и пан как в редакторе (VueFlow) */
const zoom = ref(1);
const pan = ref({ x: 0, y: 0 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });
const panStartOffset = ref({ x: 0, y: 0 });
const didPanThisGesture = ref(false);
const panningWithMiddleButton = ref(false);

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 3;
const ZOOM_STEP = 0.12;
const AUTO_ZOOM_MIN = 1.35;
const AUTO_ZOOM_MAX = 2.6;
const AUTO_ZOOM_ANIM_MS = 760;
let autoZoomAnimRaf = null;

const zoomPanStyle = computed(() => ({
	transform: `translate(${pan.value.x}px, ${pan.value.y}px) scale(${zoom.value})`,
	transformOrigin: "center center",
}));

const area = computed(() => props.selectedStep?.area);
const actionType = computed(() => props.selectedStep?.action_type);

const isPassageMode = computed(() => props.mode === "passage");

const passageInteractionLocked = computed(
	() => isPassageMode.value && !!forcedAfterUrl.value
);

/** В прохождении область видна только при подсказке (кроме невидимого поля ввода) */
const showAreaVisible = computed(() => {
	if (!showAreaOnImage.value || !area.value) return false;
	if (!isPassageMode.value) return true;
	if (isInputTextType(actionType.value)) return true;
	return props.showHintHighlight;
});

/** В прохождении: для ввода всегда есть слой; для key/hover — только при подсказке (подсветка) */
const showAreaOnImage = computed(() => {
	if (isPassageMode.value) {
		const at = actionType.value;
		const a = area.value;
		if (!at) return false;
		if (isInputTextType(at)) return !!(a && a.width > 0 && a.height > 0);
		if (isKeyPressType(at)) {
			return !!(a?.width > 0 && a?.height > 0) && props.showHintHighlight;
		}
		if (at.type === "hover" && a && a.width > 0 && a.height > 0)
			return props.showHintHighlight;
		if (isClickValidatedType(at) && a?.width > 0 && a?.height > 0)
			return props.showHintHighlight;
		return false;
	}
	const at = actionType.value;
	if (!at) return false;
	if (isKeyPressType(at)) return false;
	if (isInputTextType(at)) return true;
	return eventRequiresArea(at) && area.value;
});

/** Можно ли проверять клик по области (режим прохождения, есть область и тип клика/правый/двойной/hover) */
const canClickToValidate = computed(() => {
	if (!isPassageMode.value || passageInteractionLocked.value) return false;
	const at = actionType.value;
	const a = area.value;
	if (!at || !isClickValidatedType(at)) return false;
	if (isKeyPressType(at) || isInputTextType(at)) return false;
	if (!a || a.width <= 0 || a.height <= 0) return false;
	return true;
});

/**
 * Доля прямоугольника img, где реально рисуется картинка при object-fit: contain
 * (координаты редактора — в photo_dimensions, они же логические пиксели).
 */
const imageContentFracs = ref(null);

function updateImageContentLayout() {
	const img = imgRef.value;
	const step = props.selectedStep;
	if (!img || !step?.photo_dimensions) {
		imageContentFracs.value = null;
		return;
	}
	const w = step.photo_dimensions.width || 1;
	const h = step.photo_dimensions.height || 1;
	const rect = img.getBoundingClientRect();
	const bw = rect.width;
	const bh = rect.height;
	if (bw <= 0 || bh <= 0) {
		imageContentFracs.value = null;
		return;
	}
	const scale = Math.min(bw / w, bh / h);
	const dw = w * scale;
	const dh = h * scale;
	imageContentFracs.value = {
		ox: (bw - dw) / (2 * bw),
		oy: (bh - dh) / (2 * bh),
		sw: dw / bw,
		sh: dh / bh,
		logicalW: w,
		logicalH: h,
	};
}

const areaStyle = computed(() => {
	const a = area.value;
	const step = props.selectedStep;
	const fr = imageContentFracs.value;
	if (!a || !a.width || !a.height || !step?.photo_dimensions) return {};
	const imgW = step.photo_dimensions.width || 1;
	const imgH = step.photo_dimensions.height || 1;
	if (fr && Math.round(fr.logicalW) === Math.round(imgW) && Math.round(fr.logicalH) === Math.round(imgH)) {
		return {
			left: `${(fr.ox + (a.x / imgW) * fr.sw) * 100}%`,
			top: `${(fr.oy + (a.y / imgH) * fr.sh) * 100}%`,
			width: `${(a.width / imgW) * fr.sw * 100}%`,
			height: `${(a.height / imgH) * fr.sh * 100}%`,
		};
	}
	return {
		left: `${(a.x / imgW) * 100}%`,
		top: `${(a.y / imgH) * 100}%`,
		width: `${(a.width / imgW) * 100}%`,
		height: `${(a.height / imgH) * 100}%`,
	};
});

const areaClass = computed(() => {
	const at = actionType.value;
	if (!at) return "";
	return `action-${at.type}`;
});

/** Обёртка с aspect-ratio под изображение, чтобы overlay с % совпадал с картинкой */
const screenshotAspectStyle = computed(() => {
	const step = props.selectedStep;
	const dims = step?.photo_dimensions ?? {};
	const w = dims.width || 1;
	const h = dims.height || 1;
	return {
		width: "100%",
		maxHeight: "100%",
		aspectRatio: `${w} / ${h}`,
	};
});

function onWheel(e) {
	if (showViewportHint.value) showViewportHint.value = false;
	stopAutoZoomAnimation();
	const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
	const next = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, zoom.value + delta));
	if (next === zoom.value) return;
	const wrap = imageWrapRef.value;
	if (!wrap) return;
	const rect = wrap.getBoundingClientRect();
	const centerX = rect.width / 2;
	const centerY = rect.height / 2;
	const mouseX = e.clientX - rect.left;
	const mouseY = e.clientY - rect.top;
	const ratio = next / zoom.value;
	pan.value = {
		x: mouseX - centerX - (mouseX - centerX - pan.value.x) * ratio,
		y: mouseY - centerY - (mouseY - centerY - pan.value.y) * ratio,
	};
	zoom.value = next;
}

function onWrapMouseDown(e) {
	if (showViewportHint.value) showViewportHint.value = false;
	stopAutoZoomAnimation();
	// Средняя кнопка мыши — пан в любой момент (как в редакторе)
	if (e.button === 1) {
		e.preventDefault();
		panningWithMiddleButton.value = true;
		isPanning.value = true;
		panStart.value = { x: e.clientX, y: e.clientY };
		panStartOffset.value = { ...pan.value };
		return;
	}
	// Левая кнопка — пан только при зуме > 1
	if (e.button !== 0) return;
	if (zoom.value <= 1) return;
	didPanThisGesture.value = false;
	panningWithMiddleButton.value = false;
	isPanning.value = true;
	panStart.value = { x: e.clientX, y: e.clientY };
	panStartOffset.value = { ...pan.value };
}

function dismissViewportHint() {
	showViewportHint.value = false;
}

function onDocumentMouseMove(e) {
	if (!isPanning.value) return;
	if (!panningWithMiddleButton.value) didPanThisGesture.value = true;
	pan.value = {
		x: panStartOffset.value.x + (e.clientX - panStart.value.x),
		y: panStartOffset.value.y + (e.clientY - panStart.value.y),
	};
}

function onDocumentMouseUp() {
	isPanning.value = false;
	panningWithMiddleButton.value = false;
}

const isKeyPress = computed(() => isKeyPressType(actionType.value));
const isInputText = computed(() => isInputTextType(actionType.value));

const hotkeyLabel = computed(() => {
	const kw = area.value?.metaKeywords;
	if (!kw || !kw.length) return "—";
	return kw.join(" + ");
});

/** Для визуализации в оверлее: сначала ввод пользователя, иначе маска подсказки */
const overlayDisplayValue = computed(() => {
	const userText = String(inputValue.value ?? "");
	if (userText.length > 0) return userText;
	return String(hintMaskValue.value ?? "");
});

/** Размер шрифта в поле поверх скрина — от высоты области в логических пикселях */
const overlayInputStyle = computed(() => {
	const a = area.value;
	const step = props.selectedStep;
	const dims = step?.photo_dimensions;
	if (!a || !dims?.height) {
		return { fontSize: "14px", lineHeight: 1.25 };
	}
	const lh = Number(a.height) || 24;
	const scale = Math.max(0.7, Math.min(1.6, Number(a.metaTextScale) || 1));
	const fs = Math.round(Math.max(11, Math.min(38, lh * 0.38 * scale)));
	return {
		fontSize: `${fs}px`,
		lineHeight: 1.2,
	};
});

function hasValidArea(a) {
	return !!(a && a.width > 0 && a.height > 0);
}

function stopAutoZoomAnimation() {
	if (autoZoomAnimRaf != null) {
		cancelAnimationFrame(autoZoomAnimRaf);
		autoZoomAnimRaf = null;
	}
}

function easeInOutCubic(t) {
	return t < 0.5
		? 4 * t * t * t
		: 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function animateViewportTo(targetZoom, targetPan) {
	stopAutoZoomAnimation();
	const startZoom = zoom.value;
	const startPan = { ...pan.value };
	const dz = targetZoom - startZoom;
	const dx = targetPan.x - startPan.x;
	const dy = targetPan.y - startPan.y;
	if (Math.abs(dz) < 0.0001 && Math.abs(dx) < 0.5 && Math.abs(dy) < 0.5) return;

	const startTs = performance.now();
	const step = (now) => {
		const t = Math.min(1, (now - startTs) / AUTO_ZOOM_ANIM_MS);
		const k = easeInOutCubic(t);
		zoom.value = startZoom + dz * k;
		pan.value = {
			x: startPan.x + dx * k,
			y: startPan.y + dy * k,
		};
		if (t < 1) {
			autoZoomAnimRaf = requestAnimationFrame(step);
		} else {
			autoZoomAnimRaf = null;
		}
	};
	autoZoomAnimRaf = requestAnimationFrame(step);
}

function autoZoomToActionArea() {
	if (!isPassageMode.value) return;
	const step = props.selectedStep;
	const a = area.value;
	const at = actionType.value;
	if (!step?.photo_dimensions || !at || !eventRequiresArea(at) || !hasValidArea(a)) return;

	const wrapEl = imageWrapRef.value;
	const aspectEl = screenshotAspectRef.value;
	if (!wrapEl || !aspectEl) return;

	const wrapRect = wrapEl.getBoundingClientRect();
	const aspectRect = aspectEl.getBoundingClientRect();
	if (wrapRect.width <= 0 || wrapRect.height <= 0 || aspectRect.width <= 0 || aspectRect.height <= 0) return;

	const imgW = step.photo_dimensions.width || 1;
	const imgH = step.photo_dimensions.height || 1;
	const areaW = Math.max(1, Number(a.width) || 1);
	const areaH = Math.max(1, Number(a.height) || 1);
	const targetZoom = Math.min(
		AUTO_ZOOM_MAX,
		Math.max(
			AUTO_ZOOM_MIN,
			Math.min(imgW / (areaW * 2.2), imgH / (areaH * 1.9))
		)
	);

	const centerXLogical = (Number(a.x) || 0) + areaW / 2;
	const centerYLogical = (Number(a.y) || 0) + areaH / 2;

	const targetPointXInWrap =
		(aspectRect.left - wrapRect.left) + (centerXLogical / imgW) * aspectRect.width;
	const targetPointYInWrap =
		(aspectRect.top - wrapRect.top) + (centerYLogical / imgH) * aspectRect.height;

	const wrapCenterX = wrapRect.width / 2;
	const wrapCenterY = wrapRect.height / 2;

	animateViewportTo(targetZoom, {
		x: -(targetPointXInWrap - wrapCenterX) * targetZoom,
		y: -(targetPointYInWrap - wrapCenterY) * targetZoom,
	});
}

/**
 * Клик → координаты в системе photo_dimensions (как в редакторе).
 * Учитываем object-fit: contain: не весь getBoundingClientRect img — это «логическое» изображение.
 */
function getClickInImageCoords(e) {
	const img = imgRef.value;
	const step = props.selectedStep;
	if (!img || !step?.photo_dimensions) return null;
	const dims = step.photo_dimensions;
	const w = dims.width || 1;
	const h = dims.height || 1;
	const rect = img.getBoundingClientRect();
	const bw = rect.width;
	const bh = rect.height;
	const scale = Math.min(bw / w, bh / h);
	const dw = w * scale;
	const dh = h * scale;
	const ox = rect.left + (bw - dw) / 2;
	const oy = rect.top + (bh - dh) / 2;
	const lx = e.clientX - ox;
	const ly = e.clientY - oy;
	if (lx < 0 || ly < 0 || lx > dw || ly > dh) return null;
	return {
		x: (lx / dw) * w,
		y: (ly / dh) * h,
	};
}

function isPointInArea(px, py) {
	const a = area.value;
	if (!a) return false;
	const ax = Number(a.x);
	const ay = Number(a.y);
	const aw = Number(a.width);
	const ah = Number(a.height);
	return px >= ax && px <= ax + aw && py >= ay && py <= ay + ah;
}

async function emitActionComplete() {
	if (outcomeBusy.value) return;
	outcomeBusy.value = true;
	try {
		const afterUrl = stepAfterImageUrl(props.selectedStep);
		if (!isPassageMode.value || !afterUrl) {
			emit("action-complete");
			return;
		}
		await preloadImage(afterUrl);
		forcedAfterUrl.value = afterUrl;
		await nextTick();
		updateImageContentLayout();
		await delay(OUTCOME_FRAME_HOLD_MS);
		emit("action-complete");
	} finally {
		outcomeBusy.value = false;
	}
}

function onWrapClick(e) {
	if (passageInteractionLocked.value) return;
	if (didPanThisGesture.value) {
		didPanThisGesture.value = false;
		return;
	}
	if (!canClickToValidate.value) return;
	if (!isClickValidatedType(actionType.value)) return;
	// Только левый клик (правый — contextmenu, двойной — dblclick)
	if (actionType.value?.type !== "leftClick") return;
	const coords = getClickInImageCoords(e);
	if (!coords) return;
	if (isPointInArea(coords.x, coords.y)) {
		e.preventDefault();
		void emitActionComplete();
	} else {
		emit("action-wrong");
	}
}

function onWrapContextMenu(e) {
	if (passageInteractionLocked.value) return;
	if (didPanThisGesture.value) {
		didPanThisGesture.value = false;
		return;
	}
	if (!canClickToValidate.value) return;
	if (actionType.value?.type !== "rightClick") return;
	const coords = getClickInImageCoords(e);
	if (!coords) return;
	if (isPointInArea(coords.x, coords.y)) {
		e.preventDefault();
		void emitActionComplete();
	} else {
		emit("action-wrong");
	}
}

function onWrapDblClick(e) {
	if (passageInteractionLocked.value) return;
	if (didPanThisGesture.value) {
		didPanThisGesture.value = false;
		return;
	}
	if (!canClickToValidate.value) return;
	if (actionType.value?.type !== "doubleClick") return;
	const coords = getClickInImageCoords(e);
	if (!coords) return;
	if (isPointInArea(coords.x, coords.y)) {
		e.preventDefault();
		void emitActionComplete();
	} else {
		emit("action-wrong");
	}
}

/** Hover при прохождении: когда область не показана, проверяем по координатам на mousemove */
function onWrapMouseMove(e) {
	if (passageInteractionLocked.value) return;
	if (!isPassageMode.value || actionType.value?.type !== "hover" || showAreaVisible.value) return;
	if (!canClickToValidate.value || !area.value) return;
	const coords = getClickInImageCoords(e);
	if (coords && isPointInArea(coords.x, coords.y)) {
		if (!hoverTimer.value) {
			hoverTimer.value = setTimeout(() => {
				hoverTimer.value = null;
				void emitActionComplete();
			}, 800);
		}
	} else {
		if (hoverTimer.value) {
			clearTimeout(hoverTimer.value);
			hoverTimer.value = null;
		}
	}
}

function onWrapMouseEnter() {
	// Для hover не завершаем шаг при входе на весь скриншот — только над областью
	// (координаты: onWrapMouseMove + isPointInArea; если область видна — onAreaMouseEnter)
}

function onWrapMouseLeave() {
	if (isPassageMode.value && actionType.value?.type === "hover" && showAreaVisible.value) return;
	if (hoverTimer.value) {
		clearTimeout(hoverTimer.value);
		hoverTimer.value = null;
	}
}

function onAreaClick(e) {
	if (passageInteractionLocked.value) return;
	if (actionType.value?.type === "leftClick") {
		e.preventDefault();
		void emitActionComplete();
	}
}

function onAreaDblClick(e) {
	if (passageInteractionLocked.value) return;
	if (actionType.value?.type === "doubleClick") {
		e.preventDefault();
		void emitActionComplete();
	}
}

function onAreaContextMenu(e) {
	if (passageInteractionLocked.value) return;
	if (actionType.value?.type === "rightClick") {
		e.preventDefault();
		void emitActionComplete();
	}
}

function onAreaMouseEnter() {
	if (passageInteractionLocked.value) return;
	if (actionType.value?.type !== "hover") return;
	hoverTimer.value = setTimeout(() => {
		hoverTimer.value = null;
		void emitActionComplete();
	}, 800);
}

function onAreaMouseLeave() {
	if (hoverTimer.value) {
		clearTimeout(hoverTimer.value);
		hoverTimer.value = null;
	}
}

/** Совпадение с ожидаемой строкой — сразу переход (без ожидания Enter), если задан непустой эталон */
function normalizeTextForValidation(raw) {
	return String(raw ?? "")
		.normalize("NFKC")
		.replace(/\r\n/g, "\n")
		.replace(/\r/g, "\n")
		.replace(/[\u200B-\u200D\uFEFF]/g, "")
		.replace(/\u00a0/g, " ")
		.replace(/[“”«»„‟]/g, "\"")
		.replace(/[‘’‚‛`]/g, "'")
		.split("\n")
		.map((line) => line.replace(/[ \t]+$/g, ""))
		.join("\n")
		.trim();
}

function tryCompleteInputIfMatch() {
	if (passageInteractionLocked.value) return;
	if (!isInputTextType(actionType.value)) return;
	const expected = normalizeTextForValidation(area.value?.metaText);
	if (!expected) return;
	const actual = normalizeTextForValidation(inputValue.value);
	if (actual === expected) {
		inputValue.value = "";
		void emitActionComplete();
	}
}

function cancelHintTypewriter() {
	if (hintTypewriterTimer != null) {
		clearTimeout(hintTypewriterTimer);
		hintTypewriterTimer = null;
	}
	isHintTyping.value = false;
}

function clearHintOverlay() {
	cancelHintTypewriter();
	hintMaskValue.value = "";
}

/** Подсказка: «печатающийся» неактивный текст, без автозачёта шага */
function runHintTypewriter(full) {
	cancelHintTypewriter();
	const text = String(full ?? "");
	if (!text.length) {
		hintMaskValue.value = "";
		return;
	}
	isHintTyping.value = true;
	let i = 0;
	function setMaskProgrammatic(v) {
		inputFromTypewriter = true;
		hintMaskValue.value = v;
		setTimeout(() => {
			inputFromTypewriter = false;
		}, 0);
	}
	// При показе подсказки очищаем ошибочный ввод, чтобы пользователь набирал заново.
	inputValue.value = "";
	setMaskProgrammatic("");
	const tick = () => {
		if (i >= text.length) {
			hintTypewriterTimer = null;
			isHintTyping.value = false;
			hintMaskValue.value = text;
			nextTick(() => {
				overlayInputRef.value?.focus?.();
			});
			return;
		}
		setMaskProgrammatic(text.slice(0, i + 1));
		i += 1;
		const delay = 26 + Math.round(Math.random() * 38);
		hintTypewriterTimer = setTimeout(tick, delay);
	};
	hintTypewriterTimer = setTimeout(tick, 140);
}

function onOverlayKeydown() {
	if (!isInputTextType(actionType.value)) return;
	if (!inputFromTypewriter && (hintTypewriterTimer != null || isHintTyping.value)) {
		clearHintOverlay();
	}
}

function onOverlayInput() {
	if (!inputFromTypewriter && (hintTypewriterTimer != null || isHintTyping.value)) {
		clearHintOverlay();
	}
	if (hintMaskValue.value) hintMaskValue.value = "";
	tryCompleteInputIfMatch();
}

function onOverlayPaste() {
	if (hintTypewriterTimer != null || isHintTyping.value) {
		clearHintOverlay();
	}
	if (hintMaskValue.value) hintMaskValue.value = "";
}

function onOverlayScroll(e) {
	const el = e.target;
	const mirror = el?.previousElementSibling;
	if (!mirror) return;
	mirror.scrollLeft = el.scrollLeft;
	mirror.scrollTop = el.scrollTop;
}

function onOverlayBlur(e) {
	const el = e?.target ?? overlayInputRef.value;
	if (!el) return;
	el.scrollLeft = 0;
	el.scrollTop = 0;
}

function checkInputText() {
	if (passageInteractionLocked.value) return;
	const expected = normalizeTextForValidation(area.value?.metaText);
	const actual = normalizeTextForValidation(inputValue.value);
	if (actual === expected) {
		inputValue.value = "";
		void emitActionComplete();
	} else {
		emit("action-wrong");
	}
}

const KEY_ALIASES = {
	control: "ctrl",
	ctrlleft: "ctrl",
	ctrlright: "ctrl",
	shiftleft: "shift",
	shiftright: "shift",
	altleft: "alt",
	altright: "alt",
	altgraph: "alt",
	metaleft: "meta",
	metaright: "meta",
	" ": "space",
	escape: "esc",
	arrowup: "up",
	arrowdown: "down",
	arrowleft: "left",
	arrowright: "right",
};

function normalizeKey(k) {
	const s = String(k).toLowerCase();
	return KEY_ALIASES[s] ?? s;
}

function buildPressedKeysFromEvent(e) {
	const parts = [];
	if (e.ctrlKey) parts.push("ctrl");
	if (e.altKey) parts.push("alt");
	if (e.shiftKey) parts.push("shift");
	if (e.metaKey) parts.push("meta");

	let main = normalizeKey(e.key ?? "");
	const code = String(e.code ?? "").toLowerCase();

	// Для функциональных клавиш и части спецклавиш code стабильнее, чем key.
	if (/^f\d{1,2}$/.test(code)) main = code;
	if (code.startsWith("digit") && code.length > 5) main = code.slice(5);
	if (code.startsWith("key") && code.length === 4) main = code.slice(3).toLowerCase();
	if (code === "space") main = "space";

	const isModifierOnly = ["ctrl", "alt", "shift", "meta"].includes(main);
	if (main && !isModifierOnly) parts.push(main);
	return Array.from(new Set(parts.map(normalizeKey)));
}

function sameKeyCombo(a, b) {
	const aa = Array.from(new Set((a || []).map(normalizeKey))).sort();
	const bb = Array.from(new Set((b || []).map(normalizeKey))).sort();
	if (aa.length !== bb.length) return false;
	return aa.every((v, i) => v === bb[i]);
}

function onKeyDown(e) {
	if (passageInteractionLocked.value) return;
	if (!isKeyPress.value) return;
	const kw = area.value?.metaKeywords || [];
	if (!kw.length) return;
	// Не перехватывать, если фокус в поле ввода
	const tag = e.target?.tagName?.toUpperCase();
	if (tag === "INPUT" || tag === "TEXTAREA") return;

	const pressed = buildPressedKeysFromEvent(e);
	const expected = kw.map(normalizeKey);

	if (sameKeyCombo(pressed, expected)) {
		e.preventDefault();
		void emitActionComplete();
	}
}

watch(
	() => props.selectedStep?.id,
	() => {
		forcedAfterUrl.value = null;
		outcomeBusy.value = false;
		cancelHintTypewriter();
		inputValue.value = "";
		hintMaskValue.value = "";
		zoom.value = 1;
		pan.value = { x: 0, y: 0 };
		imageContentFracs.value = null;
		showViewportHint.value = true;
		nextTick(() => {
			updateImageContentLayout();
			if (isInputTextType(actionType.value)) {
				autoZoomToActionArea();
			}
			if (isPassageMode.value && isInputTextType(actionType.value)) {
				overlayInputRef.value?.focus?.();
			}
		});
	},
	{ immediate: true }
);

watch(
	() => [props.showHintHighlight, props.selectedStep?.id],
	([hint]) => {
		if (!isPassageMode.value) return;
		if (hint) {
			nextTick(() => autoZoomToActionArea());
		}
	},
	{ flush: "post" }
);

/** Подсказка: эффект печати вместо мгновенной подстановки */
watch(
	() => [props.showHintHighlight, props.selectedStep?.id],
	([hint]) => {
		if (!isPassageMode.value || !isInputTextType(actionType.value)) return;
		if (!hint) {
			cancelHintTypewriter();
			hintMaskValue.value = "";
			return;
		}
		if (area.value?.metaText != null) {
			runHintTypewriter(String(area.value.metaText).trim());
		}
	}
);

watch([zoom, pan], () => nextTick(() => updateImageContentLayout()), { deep: true });

const imgResizeObserver =
	typeof ResizeObserver !== "undefined"
		? new ResizeObserver(() => nextTick(() => updateImageContentLayout()))
		: null;

watch(
	imgRef,
	(el, prev) => {
		if (prev && imgResizeObserver) imgResizeObserver.unobserve(prev);
		if (el && imgResizeObserver) imgResizeObserver.observe(el);
		nextTick(() => updateImageContentLayout());
	},
	{ flush: "post" }
);

onMounted(() => {
	document.addEventListener("mousemove", onDocumentMouseMove);
	document.addEventListener("mouseup", onDocumentMouseUp);
	document.addEventListener("keydown", onKeyDown);
});

onUnmounted(() => {
	stopAutoZoomAnimation();
	cancelHintTypewriter();
	document.removeEventListener("mousemove", onDocumentMouseMove);
	document.removeEventListener("mouseup", onDocumentMouseUp);
	document.removeEventListener("keydown", onKeyDown);
	if (hoverTimer.value) clearTimeout(hoverTimer.value);
	if (imgRef.value && imgResizeObserver) imgResizeObserver.unobserve(imgRef.value);
	imgResizeObserver?.disconnect();
});
</script>

<style scoped>
.passage-flow {
	width: 100%;
	height: 100%;
	overflow: hidden;
	display: flex;
	align-items: stretch;
	justify-content: stretch;
	background: #f0f1f5;
}

.flow-inner {
	position: relative;
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: stretch;
	min-width: 0;
	min-height: 0;
}

.screenshot-wrap {
	position: relative;
	flex: 1;
	min-height: 0;
	background-color: #f0f1f5;
	overflow: hidden;
	display: flex;
	align-items: center;
	justify-content: center;
}

.viewport-hint {
	position: absolute;
	top: 10px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 20;
	display: inline-flex;
	align-items: center;
	gap: 8px;
	max-width: min(94%, 760px);
	padding: 8px 10px;
	background: rgba(15, 23, 42, 0.82);
	backdrop-filter: blur(8px);
	border: 1px solid rgba(148, 163, 184, 0.28);
	border-radius: 10px;
	color: #e2e8f0;
	font-size: 12px;
	line-height: 1.35;
}

.screenshot-aspect {
	position: relative;
	width: 100%;
	height: 100%;
	max-width: 100%;
	max-height: 100%;
}

.screenshot-wrap--clickable {
	cursor: pointer;
}

.screenshot-wrap--zoomed {
	cursor: grab;
}

.screenshot-wrap--zoomed.screenshot-wrap--panning,
.screenshot-wrap--panning {
	cursor: grabbing;
}

.screenshot-zoom-pan {
	position: absolute;
	inset: 0;
	width: 100%;
	height: 100%;
	will-change: transform;
	display: flex;
	align-items: center;
	justify-content: center;
}

.screenshot-img {
	display: block;
	width: 100%;
	height: 100%;
	object-fit: contain;
	object-position: center;
	pointer-events: none;
	user-select: none;
	transition: opacity 0.35s ease;
}

.screenshot-img--outcome {
	opacity: 0.97;
}

.action-area {
	position: absolute;
	cursor: pointer;
	border: 2px solid rgba(80, 100, 247, 0.6);
	background: rgba(80, 100, 247, 0.15);
	border-radius: 6px;
	transition: background 0.2s, border-color 0.2s;
	display: flex;
	align-items: center;
	justify-content: center;
}

.action-area:hover:not(.action-area--text-bare) {
	background: rgba(80, 100, 247, 0.25);
	border-color: var(--q-primary);
}

.action-area--text-bare:hover {
	border: none !important;
	background: transparent !important;
}

.action-area.action-hover {
	cursor: default;
}

.action-area .area-hint {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 13px;
	font-weight: 500;
	color: var(--q-primary);
	pointer-events: none;
}

.action-area--text-bare {
	border: none !important;
	background: transparent !important;
	box-shadow: none !important;
}

.action-area--text-hint-pulse {
	border: 2px solid rgba(234, 179, 8, 0.9) !important;
	background: rgba(234, 179, 8, 0.1) !important;
	box-shadow: 0 0 0 1px rgba(234, 179, 8, 0.35) !important;
	animation: passage-hint-pulse 1.1s ease-in-out infinite;
}

.action-area--hint-pulse {
	animation: passage-hint-pulse 1.1s ease-in-out infinite;
	border-color: rgba(234, 179, 8, 0.95) !important;
	background: rgba(234, 179, 8, 0.14) !important;
}

@keyframes passage-hint-pulse {
	0%,
	100% {
		opacity: 1;
	}
	50% {
		opacity: 0.45;
	}
}

.overlay-input-wrap {
	position: absolute;
	inset: 0;
	display: flex;
	align-items: stretch;
	justify-content: stretch;
	padding: 0 2px;
	box-sizing: border-box;
}

.overlay-input-stack {
	position: relative;
	flex: 1;
	min-height: 0;
	min-width: 0;
	width: 100%;
	z-index: 1;
	font-family: ui-monospace, "Cascadia Code", "Segoe UI", system-ui, sans-serif;
}

.overlay-text-mirror {
	position: absolute;
	inset: 0;
	display: block;
	padding: 0 2px;
	box-sizing: border-box;
	overflow: auto hidden;
	pointer-events: none;
	z-index: 0;
	font-family: inherit;
	font-weight: 500;
	letter-spacing: 0.01em;
	white-space: pre;
	color: #f8fafc;
	text-shadow:
		0 0 1px rgba(0, 0, 0, 1),
		0 0 4px rgba(0, 0, 0, 0.95),
		0 1px 2px rgba(0, 0, 0, 1),
		0 0 14px rgba(0, 0, 0, 0.85);
	transition: filter 0.12s ease;
}

.overlay-text-mirror--hint-type {
	color: #fef9c3;
	text-shadow:
		0 0 2px rgba(0, 0, 0, 1),
		0 0 8px rgba(251, 191, 36, 0.45),
		0 1px 2px rgba(0, 0, 0, 1);
}

.overlay-typewriter-caret {
	display: inline-block;
	width: 0.12em;
	min-width: 2px;
	height: 0.95em;
	margin-left: 1px;
	vertical-align: -0.1em;
	background: rgba(97, 240, 255, 0.95);
	border-radius: 1px;
	box-shadow: 0 0 6px rgba(97, 240, 255, 0.9);
	animation: passage-typewriter-caret 0.95s steps(1) infinite;
}

@keyframes passage-typewriter-caret {
	0%,
	45% {
		opacity: 1;
	}
	50%,
	100% {
		opacity: 0.15;
	}
}

.overlay-input {
	position: relative;
	z-index: 1;
	width: 100%;
	height: 100%;
	min-height: 0;
	border: none;
	border-radius: 0;
	background: transparent !important;
	outline: none;
	padding: 0 2px;
	box-sizing: border-box;
	font-family: inherit;
	font-weight: inherit;
	letter-spacing: inherit;
	box-shadow: none;
	resize: none;
	overflow: auto;
	white-space: pre;
}

/* Текст рисуется в .overlay-text-mirror; здесь только нативный курсор */
.overlay-input--ghost-text {
	color: transparent !important;
	-webkit-text-fill-color: transparent !important;
	text-shadow: none !important;
	caret-color: #61f0ff;
}

.overlay-input--ghost-text::selection {
	background: rgba(97, 240, 255, 0.35);
}

.overlay-input:focus {
	outline: none;
	box-shadow: none;
}

/* Печать подсказки: курсор скрыт, мигающий маркер в зеркале */
.overlay-input--hint-typing {
	caret-color: transparent !important;
}

.input-text-panel {
	flex-shrink: 0;
	width: 100%;
	max-width: 400px;
	padding: 0 16px 16px;
}

.input-field {
	background: white;
	border-radius: 12px;
}

.keypress-hint-pill {
	position: absolute;
	bottom: 80px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 10;
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 18px;
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: blur(12px);
	border-radius: 12px;
	box-shadow: 0 2px 16px rgba(0, 0, 0, 0.12);
	font-size: 14px;
	font-weight: 600;
	color: #334155;
	border: 1px solid rgba(0, 0, 0, 0.06);
}

.keypress-hint-pill .q-icon {
	color: var(--q-primary);
}
</style>
