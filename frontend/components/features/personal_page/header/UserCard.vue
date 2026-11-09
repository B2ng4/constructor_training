<template>
	<q-btn
		flat
		no-caps
		class="user-trigger"
		:loading="loading"
		:disable="loading"
	>
		<q-tooltip v-if="!$q.screen.gt.xs">{{ userStore.fullName }}</q-tooltip>
		<div class="user-trigger__inner row items-center no-wrap">
			<q-avatar
				size="36px"
				font-size="14px"
				class="user-avatar"
				:class="{ 'user-avatar--initials': !avatarIsImage }"
			>
				<img
					v-if="userStore.photo"
					:src="userStore.photo"
					class="user-avatar-img"
					alt=""
				/>
				<YandexMark
					v-else-if="userStore.isYandexUser"
					:size="36"
					class="user-avatar-yandex"
				/>
				<template v-else>{{ userInitials }}</template>
			</q-avatar>
			<span v-if="$q.screen.gt.xs" class="user-name q-ml-sm">{{ userStore.fullName }}</span>
			<q-icon
				v-if="$q.screen.gt.xs"
				name="expand_more"
				size="20px"
				class="user-chevron q-ml-xs"
			/>
		</div>
		<q-menu fit anchor="bottom right" self="top right" :offset="[0, 8]">
			<q-list class="user-menu-list">
				<q-item>
					<q-item-section>
						<q-item-label class="text-weight-medium">{{ userStore.fullName }}</q-item-label>
						<q-item-label caption>{{ userStore.email }}</q-item-label>
					</q-item-section>
				</q-item>
				<q-separator />
				<q-item clickable v-ripple v-close-popup @click="openProfile">
					<q-item-section avatar>
						<q-icon name="person" size="sm" color="grey-7" />
					</q-item-section>
					<q-item-section>Профиль</q-item-section>
				</q-item>
				<q-item clickable v-ripple @click="toggleDarkMode">
					<q-item-section avatar>
						<q-icon :name="settings.darkMode ? 'light_mode' : 'dark_mode'" size="sm" color="grey-7" />
					</q-item-section>
					<q-item-section>{{ settings.darkMode ? "Светлая тема" : "Тёмная тема" }}</q-item-section>
					<q-item-section side>
						<q-toggle
							:model-value="settings.darkMode"
							color="primary"
							size="sm"
							@click.stop
							@update:model-value="setDarkMode"
						/>
					</q-item-section>
				</q-item>
				<q-separator />
				<q-item clickable v-ripple v-close-popup @click="logout">
					<q-item-section avatar>
						<q-icon name="logout" size="sm" color="negative" />
					</q-item-section>
					<q-item-section class="text-negative">Выйти</q-item-section>
				</q-item>
			</q-list>
		</q-menu>
	</q-btn>

	<q-dialog v-model="profileDialog" persistent>
		<q-card class="profile-modal" flat bordered>
			<div class="profile-modal__header">
				<div class="profile-modal__avatar">
					<img v-if="userStore.photo" :src="userStore.photo" alt="" />
					<YandexMark v-else-if="userStore.isYandexUser" :size="72" class="profile-modal__avatar-yandex" />
					<span v-else>{{ userInitials }}</span>
				</div>
				<div class="profile-modal__identity">
					<div class="profile-modal__name">{{ userStore.fullName }}</div>
					<div class="profile-modal__email">{{ userStore.email }}</div>
					<div class="profile-modal__role">{{ roleLabel }}</div>
				</div>
				<q-btn flat round dense icon="close" v-close-popup />
			</div>

			<q-card-section class="profile-modal__body">
				<div class="profile-section">
					<div class="profile-section__title">Аккаунт</div>
					<div class="profile-row">
						<div class="profile-row__label">Тип входа</div>
						<div class="profile-row__value">
							<q-chip
								v-if="userStore.isYandexUser"
								dense
								class="profile-chip profile-chip--yandex"
							>
								<template #avatar>
									<YandexMark :size="16" />
								</template>
								Yandex ID
							</q-chip>
							<span v-else class="profile-chip profile-chip--basic">Базовый аккаунт</span>
						</div>
					</div>
					<div class="profile-row">
						<div class="profile-row__label">Email</div>
						<div class="profile-row__value">{{ userStore.email || "—" }}</div>
					</div>
					<div v-if="userStore.phone_number" class="profile-row">
						<div class="profile-row__label">Телефон</div>
						<div class="profile-row__value">{{ userStore.phone_number }}</div>
					</div>
					<div class="profile-row">
						<div class="profile-row__label">Роль</div>
						<div class="profile-row__value">{{ roleLabel }}</div>
					</div>
				</div>

				<div class="profile-section">
					<div class="profile-section__title">Настройки</div>
					<div class="profile-toggle">
						<div class="profile-toggle__text">
							<div class="profile-toggle__title">Уведомления по email</div>
							<div class="profile-toggle__desc">Новости, обновления и отчёты</div>
						</div>
						<q-toggle v-model="settings.emailNotif" color="primary" />
					</div>
					<div class="profile-toggle">
						<div class="profile-toggle__text">
							<div class="profile-toggle__title">Тёмная тема</div>
							<div class="profile-toggle__desc">Интерфейс в тёмном режиме</div>
						</div>
						<q-toggle
							:model-value="settings.darkMode"
							color="primary"
							@update:model-value="setDarkMode"
						/>
					</div>
				</div>
			</q-card-section>

			<q-card-actions class="profile-modal__footer">
				<q-btn
					flat
					no-caps
					color="negative"
					label="Выйти"
					class="profile-modal__logout"
					@click="logout"
				/>
				<q-btn
					unelevated
					no-caps
					color="primary"
					label="Готово"
					class="profile-modal__done"
					v-close-popup
				/>
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useUserStore } from "@store/userData.js";
import { YandexMark } from "@components/base_components";

const $q = useQuasar();
const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const profileDialog = ref(false);

const settings = ref({
	emailNotif: true,
	darkMode: $q.dark.isActive,
});

const userInitials = computed(() => {
	const fn = (userStore.first_name || "").trim();
	const ln = (userStore.last_name || "").trim();
	if (fn || ln) {
		const a = fn.charAt(0).toUpperCase();
		const b = ln.charAt(0).toUpperCase();
		return (a + b) || a || "?";
	}
	const name = userStore.fullName;
	if (name && name !== "Пользователь") {
		const parts = name.split(/\s+/).filter(Boolean);
		if (parts.length >= 2) {
			return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase();
		}
		return parts[0]?.slice(0, 2).toUpperCase() || "?";
	}
	return "?";
});

const avatarIsImage = computed(
	() => !!(userStore.photo || userStore.isYandexUser)
);

const roleLabel = computed(() => {
	if (userStore.isEmployee) return "Сотрудник";
	if (userStore.role === "creator") return "Создатель тренингов";
	if (userStore.role === "admin") return "Администратор";
	return userStore.role || "Пользователь";
});

async function loadUser() {
	loading.value = true;
	try {
		await userStore.fetchUser();
	} finally {
		loading.value = false;
	}
}

function openProfile() {
	profileDialog.value = true;
}

function setDarkMode(enabled) {
	settings.value.darkMode = enabled;
	$q.dark.set(enabled);
	localStorage.setItem("skillsnap-theme", enabled ? "dark" : "light");
	document.documentElement.style.colorScheme = enabled ? "dark" : "light";
}

function toggleDarkMode() {
	setDarkMode(!settings.value.darkMode);
}

function logout() {
	profileDialog.value = false;
	localStorage.removeItem("tokenAuth");
	userStore.clearUser();
	router.push("/login");
}

onMounted(() => {
	if (!userStore.isLoaded) {
		loadUser();
	}
});
</script>

<style scoped>
.user-trigger {
	min-height: 44px;
	padding: 4px 10px 4px 6px;
	border-radius: 12px;
	border: 1px solid rgba(0, 0, 0, 0.08);
	background: #fff;
	transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.user-trigger:hover {
	background: #f9fafb;
	border-color: rgba(0, 0, 0, 0.1);
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.user-trigger__inner {
	min-width: 0;
}

.user-avatar {
	font-weight: 700;
	flex-shrink: 0;
}

.user-avatar--initials {
	background: #e5e7eb;
	color: #1a1a2e;
}

.user-avatar-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	border-radius: inherit;
}

.user-avatar-yandex {
	display: block;
	margin: auto;
	padding: 5px;
	background: #fff;
	border-radius: inherit;
}

.user-name {
	max-width: 140px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	font-size: 14px;
	font-weight: 600;
	color: #1a1a2e;
}

.user-chevron {
	color: #64748b;
	opacity: 0.85;
}

.user-menu-list {
	min-width: 220px;
	border-radius: 12px;
	overflow: hidden;
	box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.user-menu-list .q-item {
	transition: background 0.2s ease;
}

/* Profile modal */
.profile-modal {
	width: 480px;
	max-width: 95vw;
	border-radius: 24px;
	overflow: hidden;
	background: #fff;
	box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
}

.profile-modal__header {
	display: flex;
	align-items: flex-start;
	gap: 18px;
	padding: 28px 24px 24px;
	border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.profile-modal__avatar {
	width: 80px;
	height: 80px;
	border-radius: 22px;
	overflow: hidden;
	flex-shrink: 0;
	background: linear-gradient(135deg, rgba(80, 100, 247, 0.10) 0%, rgba(168, 85, 247, 0.08) 100%);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 26px;
	font-weight: 750;
	color: #0f172a;
	border: 2px solid rgba(0, 0, 0, 0.04);
}

.profile-modal__avatar img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.profile-modal__avatar-yandex {
	background: #fff;
	padding: 10px;
}

.profile-modal__identity {
	flex: 1;
	min-width: 0;
	padding-top: 4px;
}

.profile-modal__name {
	font-size: 20px;
	font-weight: 750;
	color: #0f172a;
	letter-spacing: -0.02em;
	line-height: 1.25;
	margin-bottom: 4px;
}

.profile-modal__email {
	font-size: 14px;
	color: #64748b;
	margin-bottom: 8px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.profile-modal__role {
	display: inline-flex;
	font-size: 12px;
	font-weight: 650;
	color: #5064f7;
	background: rgba(80, 100, 247, 0.08);
	padding: 4px 10px;
	border-radius: 20px;
}

.profile-modal__body {
	padding: 24px;
}

.profile-section {
	margin-bottom: 28px;
}

.profile-section:last-child {
	margin-bottom: 0;
}

.profile-section__title {
	font-size: 13px;
	font-weight: 650;
	color: #94a3b8;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	margin-bottom: 14px;
}

.profile-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 12px;
	padding: 12px 0;
	border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.profile-row:last-child {
	border-bottom: none;
}

.profile-row__label {
	font-size: 14px;
	color: #64748b;
}

.profile-row__value {
	font-size: 14px;
	font-weight: 600;
	color: #0f172a;
	text-align: right;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.profile-chip {
	font-size: 12px;
	font-weight: 600;
	border-radius: 8px;
	padding: 3px 10px;
}

.profile-chip--yandex {
	background: rgba(239, 68, 68, 0.08);
	color: #dc2626;
}

.profile-chip--basic {
	background: rgba(80, 100, 247, 0.08);
	color: #5064f7;
}

.profile-toggle {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 16px;
	padding: 14px 0;
	border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.profile-toggle:last-child {
	border-bottom: none;
}

.profile-toggle__title {
	font-size: 14px;
	font-weight: 650;
	color: #0f172a;
	margin-bottom: 2px;
}

.profile-toggle__desc {
	font-size: 13px;
	color: #64748b;
}

.profile-modal__footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16px 24px;
	border-top: 1px solid rgba(0, 0, 0, 0.05);
	background: #fafbfc;
}

.profile-modal__logout {
	font-weight: 600;
	border-radius: 10px;
}

.profile-modal__done {
	border-radius: 12px;
	padding: 8px 24px;
	font-weight: 600;
	box-shadow: 0 4px 12px rgba(80, 100, 247, 0.25);
}

@media (max-width: 560px) {
	.profile-modal {
		width: 100%;
		max-width: 100%;
		border-radius: 0;
	}

	.profile-modal__header {
		padding: 20px 16px;
	}

	.profile-modal__body {
		padding: 20px 16px;
	}

	.profile-modal__footer {
		padding: 16px;
	}
}
</style>
