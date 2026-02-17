<template>
	<div class="library-page">
		<div class="page-header">
			<h1 class="page-title">Библиотека тренингов</h1>
			<p class="page-subtitle">
				Каталог готовых тренингов и материалов для обучения
			</p>
		</div>

		<div class="coming-soon-container">
			<div class="coming-soon-card">
				<div class="icon-wrapper">
					<q-icon name="library_books" size="56px" />
				</div>
				
				<h2 class="coming-soon-title">Скоро здесь</h2>
				
				<p class="coming-soon-description">
					В библиотеке появятся готовые тренинги, шаблоны и материалы для быстрого старта. Вы сможете просматривать каталог, копировать тренинги и делиться ими с коллегами.
				</p>

				<div class="features-list">
					<div class="feature-item">
						<q-icon name="content_copy" size="18px" />
						<span>Копирование тренингов</span>
					</div>
					<div class="feature-item">
						<q-icon name="filter_list" size="18px" />
						<span>Фильтры и поиск</span>
					</div>
					<div class="feature-item">
						<q-icon name="share" size="18px" />
						<span>Совместная работа</span>
					</div>
				</div>

				<div class="actions">
					<q-btn
						unelevated
						no-caps
						rounded
						color="primary"
						label="Мои тренинги"
						icon="list_alt"
						to="/personal/training"
						class="action-btn action-btn--primary"
					/>
					<q-btn
						outline
						no-caps
						rounded
						color="primary"
						label="Создать тренинг"
						icon="add"
						to="/personal/training"
						class="action-btn"
					/>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
</script>

<style scoped>
.library-page {
	padding: 32px 40px 24px;
	height: calc(100vh - 56px);
	overflow: hidden;
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

/* ——— Coming Soon Container ——— */
.coming-soon-container {
	display: flex;
	justify-content: center;
	align-items: center;
	flex: 1;
	min-height: 0;
}

.coming-soon-card {
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 20px;
	padding: 48px 40px;
	text-align: center;
	max-width: 560px;
	width: 100%;
}

.icon-wrapper {
	width: 96px;
	height: 96px;
	border-radius: 24px;
	background: rgba(80, 100, 247, 0.06);
	display: flex;
	align-items: center;
	justify-content: center;
	color: rgba(80, 100, 247, 0.7);
	margin: 0 auto 28px;
}

.icon-wrapper .q-icon {
	font-size: 48px;
}

.coming-soon-title {
	font-size: 24px;
	font-weight: 600;
	color: #0f172a;
	margin: 0 0 12px 0;
	letter-spacing: -0.01em;
}

.coming-soon-description {
	font-size: 15px;
	color: #64748b;
	line-height: 1.6;
	margin: 0 0 32px 0;
	max-width: 440px;
	margin-left: auto;
	margin-right: auto;
}

/* ——— Features List ——— */
.features-list {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
	gap: 12px;
	margin-bottom: 32px;
	padding: 0 10px;
}

.feature-item {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 10px 14px;
	background: #f8fafc;
	border: 1px solid #e2e8f0;
	border-radius: 10px;
	font-size: 13px;
	color: #475569;
	font-weight: 500;
	transition: all 0.2s ease;
}

.feature-item:hover {
	background: rgba(80, 100, 247, 0.04);
	border-color: rgba(80, 100, 247, 0.2);
}

.feature-item .q-icon {
	color: rgba(80, 100, 247, 0.7);
	flex-shrink: 0;
	font-size: 16px;
}

/* ——— Actions ——— */
.actions {
	display: flex;
	justify-content: center;
	gap: 12px;
	flex-wrap: wrap;
}

.action-btn {
	padding: 10px 24px;
	font-size: 14px;
	font-weight: 500;
	border-radius: 10px;
	transition: all 0.2s ease;
}

.action-btn--primary {
	box-shadow: 0 2px 8px rgba(80, 100, 247, 0.25);
}

.action-btn--primary:hover {
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.35);
	transform: translateY(-1px);
}

.action-btn:not(.action-btn--primary):hover {
	background: rgba(80, 100, 247, 0.04);
}

/* ——— Responsive ——— */
@media (max-width: 768px) {
	.library-page {
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
	
	.coming-soon-card {
		padding: 40px 24px;
	}
	
	.icon-wrapper {
		width: 80px;
		height: 80px;
		border-radius: 20px;
		margin-bottom: 20px;
	}
	
	.icon-wrapper .q-icon {
		font-size: 40px;
	}
	
	.coming-soon-title {
		font-size: 20px;
	}
	
	.coming-soon-description {
		font-size: 14px;
	}
	
	.features-list {
		grid-template-columns: 1fr;
		padding: 0;
		gap: 10px;
		margin-bottom: 24px;
	}
	
	.actions {
		flex-direction: column;
		width: 100%;
		gap: 10px;
	}
	
	.action-btn {
		width: 100%;
	}
}
</style>
