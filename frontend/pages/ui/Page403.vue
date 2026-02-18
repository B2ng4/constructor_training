<template>
	<div class="page-403">
		<div class="page-403__content animate-scale-in">
			<q-icon name="block" size="80px" color="grey-6" class="page-403__icon" />
			<h1 class="page-403__title">403</h1>
			<p class="page-403__text">Доступ запрещён</p>
			<q-btn
				unelevated
				no-caps
				rounded
				color="primary"
				label="На главную"
				to="/"
				class="page-403__btn"
			/>
		</div>
	</div>
</template>

<script>
export default {
	name: "Page403",
};
</script>

<style scoped>
.page-403 {
	min-height: 100vh;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 24px;
	background: #f5f6fa;
}
.page-403__content {
	text-align: center;
	max-width: 360px;
}
.page-403__icon {
	opacity: 0.7;
	margin-bottom: 16px;
	transition: transform 0.35s var(--anim-ease-spring);
}
.page-403:hover .page-403__icon {
	transform: scale(1.05);
}
.page-403__title {
	font-size: 4rem;
	font-weight: 700;
	color: #1a1a2e;
	margin: 0 0 8px 0;
	letter-spacing: -0.03em;
}
.page-403__text {
	font-size: 1.1rem;
	color: #64748b;
	margin: 0 0 24px 0;
}
.page-403__btn {
	transition: transform 0.25s var(--anim-ease-spring), box-shadow 0.25s ease;
}
.page-403__btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.3);
}
</style>