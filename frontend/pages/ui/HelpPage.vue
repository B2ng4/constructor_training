<template>
	<page-shell title="Помощь" subtitle="Как пользоваться платформой «Конструктор тренингов»">
		<div class="help-layout">
			<section class="page-panel help-faq">
				<div class="page-panel__head">
					<h2 class="page-panel__title">
						<q-icon name="question_answer" size="20px" class="page-panel__title-icon" />
						Частые вопросы
					</h2>
				</div>

				<div class="faq-list">
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
			</section>

			<section class="page-panel help-tips">
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
			</section>
		</div>
	</page-shell>
</template>

<script setup>
import { ref } from "vue";
import PageShell from "@components/common/PageShell.vue";

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
.help-layout {
	display: grid;
	grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.7fr);
	gap: 24px;
	align-items: start;
}

.faq-list {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.faq-item {
	background: rgba(255, 255, 255, 0.55);
	border: 1px solid rgba(0, 0, 0, 0.04);
	border-radius: 16px;
	overflow: hidden;
	transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.faq-item:hover {
	background: rgba(255, 255, 255, 0.75);
}

.faq-item[aria-expanded="true"] {
	background: rgba(255, 255, 255, 0.9);
	border-color: rgba(80, 100, 247, 0.15);
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.05);
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
	background: transparent;
	border-top: 1px solid rgba(0, 0, 0, 0.04);
}

.faq-answer :deep(.q-card__section) {
	padding: 16px 20px 20px;
	font-size: 15px;
	color: #475569;
	line-height: 1.6;
}

.help-tips {
	position: sticky;
	top: 24px;
}

.tips-icon {
	width: 52px;
	height: 52px;
	border-radius: 14px;
	background: rgba(245, 158, 11, 0.10);
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(245, 158, 11, 0.95);
	margin-bottom: 16px;
}

.tips-title {
	font-size: 18px;
	font-weight: 750;
	color: #0f172a;
	margin: 0 0 16px;
	letter-spacing: -0.01em;
}

.tips-list {
	list-style-position: outside;
	padding-left: 22px;
	margin: 0;
}

.tips-list li {
	font-size: 14px;
	color: #475569;
	line-height: 1.55;
	margin-bottom: 10px;
}

.tips-list li:last-child {
	margin-bottom: 0;
}

@media (max-width: 900px) {
	.help-layout {
		grid-template-columns: 1fr;
	}

	.help-tips {
		position: static;
	}
}
</style>
