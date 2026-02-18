<template>
	<div class="help-page">
		<div class="page-header animate-fade-in-up">
			<h1 class="page-title">Помощь</h1>
			<p class="page-subtitle">
				Как пользоваться платформой «Конструктор тренингов»
			</p>
		</div>

		<div class="help-content">
			<div class="faq-section animate-stagger-children">
				<q-expansion-item
					v-for="(item, i) in faq"
					:key="i"
					:label="item.question"
					header-class="faq-header"
					class="faq-item"
				>
					<q-card flat class="faq-answer">
						<q-card-section>
							{{ item.answer }}
						</q-card-section>
					</q-card>
				</q-expansion-item>
			</div>

			<div class="quick-tips animate-fade-in-up animate-stagger-5">
				<div class="tips-icon">
					<q-icon name="lightbulb" size="24px" />
				</div>
				<h3 class="tips-title">Быстрый старт</h3>
				<ol class="tips-list">
					<li>Создайте тренинг в разделе «Мои тренинги»</li>
					<li>Добавьте шаги — загрузите скриншоты или видео</li>
					<li>Выберите действие для каждого шага (клик, ввод текста, хоткей)</li>
					<li>Выделите область на скриншоте и сохраните</li>
					<li>Опубликуйте тренинг и поделитесь ссылкой</li>
				</ol>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue";

const faq = ref([
	{
		question: "Как создать тренинг?",
		answer:
			"Перейдите в раздел «Создание тренинга», нажмите «Создать тренинг» и заполните название и описание. Затем добавьте шаги — загрузите скриншоты или запишите видео, которое автоматически разобьётся на кадры.",
	},
	{
		question: "Как добавить шаги из видео?",
		answer:
			"Создайте тренинг и перейдите в режим редактирования. Загрузите видеофайл — система автоматически определит значимые кадры (по стабильности и изменению изображения) и создаст из них шаги. Поддерживается форматы mp4 и аналогичные.",
	},
	{
		question: "Какие типы действий поддерживаются?",
		answer:
			"Левый клик, правый клик, двойной клик, наведение курсора, ввод текста и нажатие клавиш. Для каждого шага можно указать область на скриншоте, где пользователь должен выполнить действие.",
	},
	{
		question: "Как опубликовать тренинг?",
		answer:
			"В карточке тренинга откройте меню (три точки) и выберите «Опубликовать». Система сгенерирует публичную ссылку, которой можно поделиться. Любой, у кого есть ссылка, сможет пройти тренинг без авторизации.",
	},
]);
</script>

<style scoped>
.help-page {
	padding: 32px 40px 24px;
	height: calc(100vh - 56px);
	overflow-y: auto;
	display: flex;
	flex-direction: column;
}

/* ——— Header ——— */
.page-header {
	margin-bottom: 32px;
	flex-shrink: 0;
}

.page-title {
	font-size: 28px;
	font-weight: 600;
	color: #0f172a;
	margin: 0 0 6px 0;
	letter-spacing: -0.02em;
}

.page-subtitle {
	font-size: 15px;
	color: #64748b;
	margin: 0;
	font-weight: 400;
}

/* ——— Help Content ——— */
.help-content {
	max-width: 800px;
	flex: 1;
	min-height: 0;
}

/* ——— FAQ Section ——— */
.faq-section {
	display: flex;
	flex-direction: column;
	gap: 12px;
	margin-bottom: 32px;
}

.faq-item {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 14px;
	overflow: hidden;
	transition: border-color 0.25s ease, box-shadow 0.25s var(--anim-ease-out);
}
.faq-item:hover {
	border-color: #cbd5e1;
	box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}
.faq-item :deep(.q-expansion-item__container) {
	transition: background 0.2s ease;
}
.faq-item :deep(.q-item__label) {
	transition: color 0.2s ease;
}
.faq-item[aria-expanded="true"] {
	border-color: rgba(80, 100, 247, 0.3);
	box-shadow: 0 2px 12px rgba(80, 100, 247, 0.06);
}

.faq-item :deep(.faq-header) {
	font-weight: 600;
	font-size: 15px;
	color: #0f172a;
	padding: 18px 20px;
}

.faq-item :deep(.q-expansion-item__toggle-icon) {
	color: rgba(80, 100, 247, 0.7);
	transition: transform 0.3s var(--anim-ease-spring);
}
.faq-item[aria-expanded="true"] :deep(.q-expansion-item__toggle-icon) {
	transform: rotate(180deg);
}

.faq-answer {
	background: #f8fafc;
	border-top: 1px solid #e2e8f0;
}

.faq-answer :deep(.q-card__section) {
	padding: 18px 20px;
	font-size: 14px;
	color: #475569;
	line-height: 1.6;
}

/* ——— Quick Tips ——— */
.quick-tips {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 16px;
	padding: 28px 32px;
	position: relative;
	transition: border-color 0.25s ease, box-shadow 0.25s var(--anim-ease-out);
}
.quick-tips:hover {
	border-color: rgba(245, 158, 11, 0.3);
	box-shadow: 0 4px 20px rgba(245, 158, 11, 0.08);
}

.tips-icon {
	width: 48px;
	height: 48px;
	border-radius: 12px;
	background: rgba(245, 158, 11, 0.12);
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(245, 158, 11, 0.95);
	margin-bottom: 16px;
	transition: transform 0.35s var(--anim-ease-spring);
}
.quick-tips:hover .tips-icon {
	transform: scale(1.08);
}

.tips-title {
	font-size: 18px;
	font-weight: 600;
	color: #0f172a;
	margin: 0 0 16px 0;
}

.tips-list {
	list-style-position: outside;
	padding-left: 24px;
	margin: 0;
}

.tips-list li {
	font-size: 14px;
	color: #475569;
	line-height: 1.6;
	margin-bottom: 10px;
}

.tips-list li:last-child {
	margin-bottom: 0;
}

/* ——— Responsive ——— */
@media (max-width: 768px) {
	.help-page {
		padding: 24px 16px 20px;
	}
	
	.page-header {
		margin-bottom: 24px;
	}
	
	.page-title {
		font-size: 24px;
	}
	
	.page-subtitle {
		font-size: 14px;
	}
	
	.faq-section {
		gap: 10px;
		margin-bottom: 24px;
	}
	
	.faq-item :deep(.faq-header) {
		font-size: 14px;
		padding: 16px;
	}
	
	.faq-answer :deep(.q-card__section) {
		padding: 16px;
		font-size: 13px;
	}
	
	.quick-tips {
		padding: 24px;
	}
	
	.tips-icon {
		width: 44px;
		height: 44px;
	}
	
	.tips-title {
		font-size: 16px;
	}
	
	.tips-list {
		padding-left: 20px;
	}
	
	.tips-list li {
		font-size: 13px;
	}
}
</style>
