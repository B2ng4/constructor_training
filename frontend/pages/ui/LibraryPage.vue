<template>
	<page-shell title="Библиотека" subtitle="Каталог готовых тренингов и шаблонов для быстрого старта">
		<div class="page-panel library-card">
			<div class="library-hero">
				<div class="library-hero__icon">
					<q-icon name="auto_stories" size="40px" />
				</div>
				<h2 class="library-hero__title">Скоро здесь</h2>
				<p class="library-hero__desc">
					В библиотеке появятся готовые тренинги, шаблоны и материалы для быстрого старта.
					Вы сможете просматривать каталог, копировать тренинги и делиться ими с коллегами.
				</p>
			</div>

			<div class="library-features">
				<div class="library-feature" v-ripple>
					<q-icon name="content_copy" size="20px" class="library-feature__icon" />
					<span class="library-feature__text">Копирование тренингов</span>
				</div>
				<div class="library-feature" v-ripple>
					<q-icon name="filter_list" size="20px" class="library-feature__icon" />
					<span class="library-feature__text">Фильтры и поиск</span>
				</div>
				<div class="library-feature" v-ripple>
					<q-icon name="share" size="20px" class="library-feature__icon" />
					<span class="library-feature__text">Совместная работа</span>
				</div>
			</div>

			<div class="library-actions">
				<q-btn
					unelevated
					no-caps
					color="primary"
					icon="list_alt"
					label="Мои тренинги"
					to="/personal/training"
					class="page-cta"
				/>
				<q-btn
					outline
					no-caps
					color="primary"
					icon="add"
					label="Создать тренинг"
					to="/personal/training"
					class="page-cta page-cta--outline"
				/>
			</div>
		</div>
	</page-shell>
</template>

<script setup>
import PageShell from "@components/common/PageShell.vue";
</script>

<style scoped>
.library-card {
	text-align: center;
	max-width: 640px;
	margin: 0 auto;
	padding: 52px 40px;
}

.library-hero__icon {
	width: 88px;
	height: 88px;
	border-radius: 24px;
	background: rgba(80, 100, 247, 0.10);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #5064f7;
	margin: 0 auto 24px;
	box-shadow: 0 8px 24px rgba(80, 100, 247, 0.12);
}

.library-hero__title {
	font-size: 24px;
	font-weight: 750;
	color: #0f172a;
	margin: 0 0 10px;
	letter-spacing: -0.02em;
}

.library-hero__desc {
	font-size: 15px;
	color: #64748b;
	line-height: 1.6;
	max-width: 480px;
	margin: 0 auto 32px;
}

.library-features {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 12px;
	margin-bottom: 36px;
}

.library-feature {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	padding: 12px 16px;
	background: rgba(255, 255, 255, 0.65);
	border: 1px solid rgba(0, 0, 0, 0.05);
	border-radius: 14px;
	font-size: 14px;
	font-weight: 600;
	color: #475569;
	transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.library-feature:hover {
	background: rgba(80, 100, 247, 0.06);
	border-color: rgba(80, 100, 247, 0.2);
	transform: translateY(-1px);
}

.library-feature__icon {
	color: #5064f7;
	flex-shrink: 0;
}

.library-actions {
	display: flex;
	justify-content: center;
	gap: 12px;
	flex-wrap: wrap;
}

.page-cta--outline {
	box-shadow: none !important;
}

@media (max-width: 640px) {
	.library-card {
		padding: 36px 24px;
	}

	.library-features {
		grid-template-columns: 1fr;
	}

	.library-actions {
		flex-direction: column;
		width: 100%;
	}

	.page-cta {
		width: 100%;
	}
}
</style>
