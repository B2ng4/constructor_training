<template>
	<header class="edit-editor-header glass-panel">
		<div class="edit-editor-header__left">
			<q-btn flat round dense color="grey-8" icon="apps" class="edit-editor-header__nav-btn">
				<q-tooltip>Разделы</q-tooltip>
				<q-menu anchor="bottom left" self="top left">
					<q-list dense style="min-width: 220px">
						<q-item-label header class="text-grey-7">Разделы</q-item-label>
						<q-item
							v-for="nav in navItems"
							:key="nav.url"
							clickable
							v-ripple
							:to="nav.url"
						>
							<q-item-section avatar>
								<q-icon :name="nav.icon" size="18px" />
							</q-item-section>
							<q-item-section>{{ nav.name }}</q-item-section>
						</q-item>
					</q-list>
				</q-menu>
			</q-btn>
			<group-steps />
		</div>

		<div class="edit-editor-header__center">
			<step-title />
			<step-readiness-badge />
		</div>

		<div class="edit-editor-header__right">
			<editor-save-indicator />

			<div class="edit-editor-header__actions">
				<q-btn
					flat
					round
					dense
					color="primary"
					icon="play_circle"
					@click="emit('preview')"
				>
					<q-tooltip>Превью (Пробел)</q-tooltip>
				</q-btn>
				<q-btn
					flat
					round
					dense
					color="primary"
					icon="account_tree"
					@click="emit('map')"
				>
					<q-tooltip>Карта сценария</q-tooltip>
				</q-btn>
				<q-btn
					v-if="showCrop"
					flat
					round
					dense
					color="primary"
					icon="crop"
					@click="emit('crop')"
				>
					<q-tooltip>Обрезать скриншот</q-tooltip>
				</q-btn>

				<q-btn flat round dense color="grey-8" icon="more_vert">
					<q-tooltip>Действия со шагом</q-tooltip>
					<q-menu anchor="bottom right" self="top right">
						<q-list dense style="min-width: 200px">
							<q-item clickable v-ripple @click="emit('detect')">
								<q-item-section avatar>
									<q-icon name="select_all" size="18px" />
								</q-item-section>
								<q-item-section>Найти элементы (AI)</q-item-section>
							</q-item>
							<q-item clickable v-ripple @click="emit('duplicate')">
								<q-item-section avatar>
									<q-icon name="content_copy" size="18px" />
								</q-item-section>
								<q-item-section>Дублировать шаг</q-item-section>
								<q-item-section side class="text-grey-6 text-caption">Ctrl+D</q-item-section>
							</q-item>
							<q-separator />
							<q-item clickable v-ripple @click="emit('home')">
								<q-item-section avatar>
									<q-icon name="home" size="18px" />
								</q-item-section>
								<q-item-section>На главную</q-item-section>
							</q-item>
						</q-list>
					</q-menu>
				</q-btn>
			</div>
		</div>
	</header>
</template>

<script setup>
import { GroupSteps } from "@components/features/edit_page/drop_down_list_steps";
import StepTitle from "@components/features/edit_page/StepTitle.vue";
import StepReadinessBadge from "@components/features/edit_page/StepReadinessBadge.vue";
import EditorSaveIndicator from "@components/features/edit_page/EditorSaveIndicator.vue";

defineProps({
	showCrop: { type: Boolean, default: false },
});

const navItems = [
	{ name: "Главная", icon: "home", url: "/personal/home" },
	{ name: "Библиотека", icon: "menu_book", url: "/personal/library" },
	{ name: "Мои тренинги", icon: "list_alt", url: "/personal/training" },
	{ name: "Мои курсы", icon: "school", url: "/personal/courses" },
	{ name: "Мои организации", icon: "business", url: "/personal/organizations" },
	{ name: "Поддержка", icon: "help", url: "/personal/help" },
];

const emit = defineEmits(["preview", "map", "crop", "home", "duplicate", "detect"]);
</script>

<style scoped>
.edit-editor-header {
	display: grid;
	grid-template-columns: auto 1fr auto;
	align-items: center;
	gap: 12px;
	padding: 8px 12px;
	margin: 10px 12px 0;
	border-radius: 16px;
	flex-shrink: 0;
	z-index: 30;
}

.edit-editor-header__left {
	display: flex;
	align-items: center;
	gap: 4px;
	min-width: 0;
}

.edit-editor-header__nav-btn {
	flex-shrink: 0;
}

.edit-editor-header__left :deep(.steps-dropdown) {
	position: static !important;
	margin: 0 !important;
}

.edit-editor-header__center {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	min-width: 0;
	flex-wrap: wrap;
}

.edit-editor-header__right {
	display: flex;
	align-items: center;
	gap: 8px;
	flex-shrink: 0;
}

.edit-editor-header__actions {
	display: flex;
	align-items: center;
	gap: 2px;
	padding-left: 4px;
	border-left: 1px solid rgba(15, 23, 42, 0.08);
}

@media (max-width: 760px) {
	.edit-editor-header {
		grid-template-columns: 1fr;
		gap: 8px;
	}

	.edit-editor-header__center {
		order: -1;
	}

	.edit-editor-header__right {
		justify-content: space-between;
		width: 100%;
	}
}
</style>
