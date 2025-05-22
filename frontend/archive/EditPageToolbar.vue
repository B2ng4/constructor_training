<template>
	<div class="toolbar">
		<q-btn class="toolbar-btn">
			<div class="btn-content">
				<q-icon name="mouse" size="24px"/>
				<span class="btn-label">ЛКМ</span>
			</div>
		</q-btn>
		<q-btn class="toolbar-btn">
			<div class="btn-content">
				<q-icon name="mouse" size="24px"/>
				<span class="btn-label">ПКМ</span>
			</div>
		</q-btn>
		<q-btn class="toolbar-btn">
			<div class="btn-content">
				<q-icon name="mouse" size="24px"/>
				<span class="btn-label">Двойной</span>
			</div>
		</q-btn>
		<q-btn class="toolbar-btn">
			<div class="btn-content">
				<q-icon name="title" size="24px"/>
				<span class="btn-label">Текст</span>
			</div>
		</q-btn>
		<q-btn class="toolbar-btn">
			<div class="btn-content">
				<q-icon name="mouse" size="24px"/>
				<span class="btn-label">Навести</span>
			</div>
		</q-btn>
		<q-btn class="toolbar-btn">
			<div class="btn-content">
				<q-icon name="keyboard" size="24px"/>
				<span class="btn-label">Клавиатура</span>
			</div>
		</q-btn>
	</div>
</template>

<script>
export default {
	name: "EditPageToolbar"
};
</script>

<style scoped>
.toolbar {
	display: flex;
	flex-direction: column;
}

.toolbar-btn {
	height: auto;
	min-height: 48px;
	padding: 16px;
}

.toolbar-btn:first-child {
	border-radius: 12px 12px 0 0;
}

.toolbar-btn:last-child {
	border-radius: 0 0 12px 12px;
}

.btn-content {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	width: 100%;
}

.btn-label {
	font-size: 12px;
	line-height: 1;
}
</style>