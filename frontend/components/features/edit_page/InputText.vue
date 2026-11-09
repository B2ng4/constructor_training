<template>
	<div class="it-root" :class="{ 'it-root--focused': focused }">
		
		<!-- ═══ Floating Tool Bar ═══ -->
		<div v-show="focused || focusedToolbar" class="it-toolbar" @mouseenter="focusedToolbar = true" @mouseleave="focusedToolbar = false" @click.stop>
			<!-- ═══ Drag handle ═══ -->
			<div class="it-handle" title="Перетащить область">
				<svg class="it-handle__grip" viewBox="0 0 20 8" fill="none">
					<circle cx="4" cy="2" r="1.2" fill="currentColor"/>
					<circle cx="10" cy="2" r="1.2" fill="currentColor"/>
					<circle cx="16" cy="2" r="1.2" fill="currentColor"/>
					<circle cx="4" cy="6" r="1.2" fill="currentColor"/>
					<circle cx="10" cy="6" r="1.2" fill="currentColor"/>
					<circle cx="16" cy="6" r="1.2" fill="currentColor"/>
				</svg>
				<span class="it-handle__label">настройки ввода</span>
				<svg class="it-handle__grip" viewBox="0 0 20 8" fill="none">
					<circle cx="4" cy="2" r="1.2" fill="currentColor"/>
					<circle cx="10" cy="2" r="1.2" fill="currentColor"/>
					<circle cx="16" cy="2" r="1.2" fill="currentColor"/>
					<circle cx="4" cy="6" r="1.2" fill="currentColor"/>
					<circle cx="10" cy="6" r="1.2" fill="currentColor"/>
					<circle cx="16" cy="6" r="1.2" fill="currentColor"/>
				</svg>
			</div>

			<!-- ═══ Mode tabs ═══ -->
			<div class="it-tabs nodrag">
				<button class="it-tab" :class="{ 'it-tab--active': localMode === 'exact' }" @click.stop="setMode('exact')">
					<span class="it-tab__icon">✎</span> Точный текст
				</button>
				<button class="it-tab" :class="{ 'it-tab--active': localMode === 'regex' }" @click.stop="setMode('regex')">
					<span class="it-tab__icon">⊛</span> Паттерн
				</button>
			</div>

			<!-- ═══ Pattern mode ═══ -->
			<div v-if="localMode === 'regex'" class="it-pattern nodrag">
				<div class="it-presets">
					<button v-for="p in PRESETS" :key="p.id" class="it-preset" :class="{ 'it-preset--active': localPreset === p.id }" @click.stop="selectPreset(p)">
						<span class="it-preset__icon">{{ p.icon }}</span>
						<span class="it-preset__label">{{ p.label }}</span>
					</button>
				</div>
				<div v-if="localPreset === 'custom'" class="it-regex-wrap">
					<span class="it-regex-wrap__prefix">/ </span>
					<input v-model="localCustomPattern" class="it-regex-input nodrag" placeholder="...паттерн..." spellcheck="false" @blur="onCustomPatternBlur" />
					<span class="it-regex-wrap__suffix"> /</span>
				</div>
				<div class="it-pattern-info">
					<span class="it-pattern-info__desc">{{ activePresetObj?.description }}</span>
					<span v-if="localPreset === 'custom' && localCustomPattern" class="it-pattern-info__badge" :class="isValidRegex ? 'it-pattern-info__badge--ok' : 'it-pattern-info__badge--err'">
						{{ isValidRegex ? '✓' : '✗' }}
					</span>
				</div>
			</div>

			<!-- ═══ Font size bar ═══ -->
			<div class="it-bar nodrag">
				<button class="it-bar__btn" title="Уменьшить шрифт" @click.stop="changeFontSize(-2)">
					<span class="it-bar__a it-bar__a--sm">A</span>
				</button>
				<div class="it-bar__track">
					<div class="it-bar__fill" :style="{ width: fillPercent + '%' }" />
					<input type="range" class="it-bar__range nodrag" :min="MIN_FONT" :max="MAX_FONT" :value="fontSizePx" @input="onRangeInput" />
				</div>
				<button class="it-bar__btn" title="Увеличить шрифт" @click.stop="changeFontSize(2)">
					<span class="it-bar__a it-bar__a--lg">A</span>
				</button>
				<span class="it-bar__px">{{ fontSizePx }}px</span>
			</div>
		</div>

		<!-- ═══ Textarea (Exact or Hint) ═══ -->
		<textarea
			ref="inputRef"
			v-model="model"
			class="it-textarea nodrag"
			:style="{ fontSize: `${fontSizePx}px`, lineHeight: 1.25, height: `${Math.ceil(fontSizePx * 1.25)}px` }"
			spellcheck="false"
			autocomplete="off"
			rows="1"
			wrap="off"
			:placeholder="localMode === 'exact' ? 'Точный текст...' : 'Подсказка...'"
			@focus="focused = true"
			@blur="onBlur"
		/>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from "vue";

const MIN_FONT = 10;
const MAX_FONT = 72;

const PRESETS = [
	{
		id: 'any',
		icon: '✓',
		label: 'Любой',
		pattern: '.+',
		description: 'Принять любой непустой текст',
	},
	{
		id: 'email',
		icon: '✉',
		label: 'Email',
		pattern: '^[\\w.+\\-]+@[\\w\\-]+\\.[a-zA-Z]{2,}$',
		description: 'Адрес электронной почты',
	},
	{
		id: 'phone',
		icon: '☎',
		label: 'Телефон',
		pattern: '^[\\+\\d][\\d\\s\\-\\(\\)]{6,14}$',
		description: 'Номер телефона (любой формат)',
	},
	{
		id: 'number',
		icon: '#',
		label: 'Число',
		pattern: '^-?\\d+([.,]\\d+)?$',
		description: 'Целое или дробное число',
	},
	{
		id: 'date',
		icon: '📅',
		label: 'Дата',
		pattern: '^\\d{1,2}[./\\-]\\d{1,2}[./\\-]\\d{2,4}$',
		description: 'Дата в формате ДД.ММ.ГГГГ и подобных',
	},
	{
		id: 'custom',
		icon: '⚙',
		label: 'Свой',
		pattern: '',
		description: 'Введите своё регулярное выражение',
	},
];

const model = defineModel({ type: String, default: () => '' });

const props = defineProps({
	fontSizePx:     { type: Number, default: 16 },
	matchMode:      { type: String, default: 'exact' },  // 'exact' | 'regex'
	pattern:        { type: String, default: '' },
	patternPreset:  { type: String, default: 'any' },
});

const emit = defineEmits([
	'update:fontSizePx',
	'update:matchMode',
	'update:pattern',
	'update:patternPreset',
	'save',
]);

const inputRef = ref(null);
const focused = ref(false);
const focusedToolbar = ref(false);

// Local state mirrors props (avoids prop-mutation)
const localMode    = ref(props.matchMode);
const localPreset  = ref(props.patternPreset || 'any');
const localCustomPattern = ref(props.pattern || '');

// Sync from props when parent updates (step changed)
watch(() => props.matchMode, v => { localMode.value = v; });
watch(() => props.patternPreset, v => { localPreset.value = v || 'any'; });
watch(() => props.pattern, v => {
	if (localPreset.value === 'custom') localCustomPattern.value = v || '';
});

const activePresetObj = computed(() => PRESETS.find(p => p.id === localPreset.value));

const effectivePattern = computed(() => {
	if (localMode.value === 'exact') return '';
	if (localPreset.value === 'custom') return localCustomPattern.value;
	return activePresetObj.value?.pattern ?? '';
});

const isValidRegex = computed(() => {
	if (!localCustomPattern.value) return false;
	try { new RegExp(localCustomPattern.value); return true; } catch { return false; }
});

const fillPercent = computed(() =>
	Math.round(((props.fontSizePx - MIN_FONT) / (MAX_FONT - MIN_FONT)) * 100)
);

// ── Actions ───────────────────────────────────────────────────────────────

function setMode(mode) {
	localMode.value = mode;
	emit('update:matchMode', mode);
	emit('save');
}

function selectPreset(preset) {
	localPreset.value = preset.id;
	emit('update:patternPreset', preset.id);
	if (preset.id !== 'custom') {
		emit('update:pattern', preset.pattern);
	}
	emit('save');
}

function onCustomPatternBlur() {
	focused.value = false;
	emit('update:pattern', localCustomPattern.value);
	emit('save');
}

function changeFontSize(delta) {
	const next = Math.max(MIN_FONT, Math.min(MAX_FONT, props.fontSizePx + delta));
	emit('update:fontSizePx', next);
}

function onRangeInput(e) {
	emit('update:fontSizePx', Number(e.target.value));
}

function onBlur(e) {
	focused.value = false;
	const el = e?.target;
	if (el) { el.scrollTop = 0; el.scrollLeft = 0; }
	emit('save');
}

onMounted(() => {
	nextTick(() => inputRef.value?.focus?.());
});

defineExpose({
	focus: () => inputRef.value?.focus?.(),
	effectivePattern,
});
</script>

<style scoped>
.it-root {
	position: absolute;
	inset: 0;
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center; /* Центрируем, как в PassageFlow */
	box-sizing: border-box;
	overflow: visible; /* Чтобы тулбар выходил за границы ноды */
	background: transparent;
	transition: box-shadow 0.18s ease;
}
.it-root--focused {
	background: rgba(99, 102, 241, 0.05);
}

/* ===== Floating Toolbar ===== */
.it-toolbar {
	position: absolute;
	bottom: 100%;
	left: 0;
	margin-bottom: 6px;
	width: 250px;
	display: flex;
	flex-direction: column;
	background: rgba(8, 12, 30, 0.85);
	backdrop-filter: blur(8px);
	border: 1px solid rgba(255, 255, 255, 0.1);
	border-radius: 8px;
	box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
	overflow: hidden;
	z-index: 100;
}
.it-root--focused {
	box-shadow:
		inset 0 0 0 1.5px rgba(99, 102, 241, 0.6),
		0 0 0 2px rgba(99, 102, 241, 0.2);
}

/* ===== Drag handle ===== */
.it-handle {
	width: 100%;
	height: 22px;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 6px;
	background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(56, 189, 248, 0.18));
	border-bottom: 1px solid rgba(99, 102, 241, 0.4);
	cursor: grab;
	flex-shrink: 0;
	user-select: none;
	transition: background 0.15s, border-color 0.15s;
}
.it-handle:hover {
	background: linear-gradient(135deg, rgba(99, 102, 241, 0.5), rgba(56, 189, 248, 0.32));
	border-bottom-color: rgba(99, 102, 241, 0.75);
}
.it-handle:active { cursor: grabbing; }
.it-handle__grip {
	width: 22px; height: 9px;
	color: rgba(255, 255, 255, 0.55);
	transition: color 0.15s;
	flex-shrink: 0;
}
.it-handle:hover .it-handle__grip { color: rgba(255, 255, 255, 0.95); }
.it-handle__label {
	font-size: 9px; font-weight: 700; letter-spacing: 0.09em;
	text-transform: uppercase; color: rgba(255,255,255,0.45);
	transition: color 0.15s; pointer-events: none;
}
.it-handle:hover .it-handle__label { color: rgba(255,255,255,0.9); }

/* ===== Mode tabs ===== */
.it-tabs {
	display: flex;
	flex-shrink: 0;
	border-bottom: 1px solid rgba(255,255,255,0.07);
}
.it-tab {
	flex: 1;
	padding: 4px 6px;
	border: none;
	background: transparent;
	color: rgba(255,255,255,0.45);
	font-size: 9.5px;
	font-weight: 600;
	letter-spacing: 0.03em;
	cursor: pointer;
	transition: background 0.15s, color 0.15s;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 4px;
}
.it-tab:hover { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.7); }
.it-tab--active {
	background: rgba(99,102,241,0.18);
	color: #a5b4fc;
	border-bottom: 2px solid #6366f1;
}
.it-tab__icon { font-size: 11px; }

/* ===== Exact & Hint Textarea ===== */
.it-textarea {
	width: 100%;
	margin: 0;
	padding: 0 2px;
	border: none;
	background: transparent;
	color: #f1f5f9;
	outline: none;
	resize: none;
	box-sizing: border-box;
	font-family: ui-monospace, "Cascadia Code", "Segoe UI Mono", monospace;
	font-weight: 500;
	letter-spacing: 0.01em;
	caret-color: #818cf8;
	white-space: pre;
	overflow: hidden;
	text-shadow: 0 0 8px rgba(0,0,0,0.9), 0 1px 2px rgba(0,0,0,1);
}

.it-textarea::placeholder { color: rgba(241,245,249,0.35); font-style: italic; text-shadow: none; }
.it-textarea::selection { background: rgba(99,102,241,0.35); }
.it-textarea:focus { outline: none; }

/* ===== Pattern mode ===== */
.it-pattern {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 0;
	min-height: 0;
	overflow: hidden;
}

.it-presets {
	display: flex;
	flex-wrap: wrap;
	gap: 4px;
	padding: 6px 6px 4px;
	flex-shrink: 0;
}

.it-preset {
	display: flex;
	align-items: center;
	gap: 3px;
	padding: 3px 8px;
	border: 1px solid rgba(255,255,255,0.12);
	border-radius: 20px;
	background: rgba(255,255,255,0.05);
	color: rgba(255,255,255,0.6);
	font-size: 10px;
	font-weight: 600;
	cursor: pointer;
	transition: all 0.15s;
	line-height: 1;
}
.it-preset:hover {
	background: rgba(99,102,241,0.2);
	border-color: rgba(99,102,241,0.5);
	color: #c7d2fe;
}
.it-preset--active {
	background: rgba(99,102,241,0.35);
	border-color: rgba(99,102,241,0.8);
	color: #e0e7ff;
	box-shadow: 0 0 0 1px rgba(99,102,241,0.4);
}
.it-preset__icon { font-size: 11px; }
.it-preset__label { font-size: 9.5px; }

/* Custom regex input */
.it-regex-wrap {
	display: flex;
	align-items: center;
	margin: 2px 6px 4px;
	background: rgba(0,0,0,0.3);
	border: 1px solid rgba(99,102,241,0.35);
	border-radius: 6px;
	padding: 3px 7px;
	flex-shrink: 0;
}
.it-regex-wrap__prefix,
.it-regex-wrap__suffix {
	color: rgba(99,102,241,0.8);
	font-family: ui-monospace, monospace;
	font-size: 12px;
	font-weight: 700;
	flex-shrink: 0;
}
.it-regex-input {
	flex: 1;
	border: none;
	background: transparent;
	color: #c7d2fe;
	font-family: ui-monospace, "Cascadia Code", monospace;
	font-size: 11px;
	outline: none;
	min-width: 0;
}
.it-regex-input::placeholder { color: rgba(199,210,254,0.3); font-style: italic; }

/* Pattern description */
.it-pattern-info {
	padding: 2px 8px 4px;
	display: flex;
	align-items: center;
	gap: 6px;
	flex-shrink: 0;
}
.it-pattern-info__desc {
	font-size: 9px;
	color: rgba(255,255,255,0.35);
	flex: 1;
}
.it-pattern-info__badge {
	font-size: 9px;
	font-weight: 700;
	padding: 1px 5px;
	border-radius: 4px;
	flex-shrink: 0;
}
.it-pattern-info__badge--ok { background: rgba(34,197,94,0.2); color: #4ade80; }
.it-pattern-info__badge--err { background: rgba(239,68,68,0.2); color: #f87171; }



/* ===== Font size bar ===== */
.it-bar {
	display: flex;
	align-items: center;
	gap: 4px;
	padding: 2px 5px;
	background: rgba(0,0,0,0.4);
	border-top: 1px solid rgba(255,255,255,0.06);
	flex-shrink: 0;
	user-select: none;
}
.it-bar__btn {
	border: none;
	background: rgba(255,255,255,0.06);
	border-radius: 3px;
	padding: 1px 4px;
	cursor: pointer;
	display: flex; align-items: center; justify-content: center;
	transition: background 0.15s; line-height: 1;
}
.it-bar__btn:hover { background: rgba(255,255,255,0.14); }
.it-bar__a { font-family: Arial, sans-serif; font-weight: 700; color: #cbd5e1; line-height: 1; }
.it-bar__a--sm { font-size: 9px; }
.it-bar__a--lg { font-size: 13px; }

.it-bar__track {
	flex: 1; position: relative;
	height: 6px; background: rgba(255,255,255,0.1);
	border-radius: 10px; overflow: hidden;
}
.it-bar__fill {
	position: absolute; left: 0; top: 0; height: 100%;
	background: linear-gradient(90deg, #6366f1, #38bdf8);
	border-radius: 10px; pointer-events: none; transition: width 0.08s;
}
.it-bar__range {
	position: absolute; inset: 0; width: 100%; height: 100%;
	opacity: 0; cursor: pointer; margin: 0;
}
.it-bar__px {
	font-size: 9px; font-weight: 700; color: #94a3b8;
	min-width: 26px; text-align: right;
	font-family: ui-monospace, monospace;
}
</style>
