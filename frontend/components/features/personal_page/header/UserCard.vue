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
				color="grey-3"
				text-color="grey-9"
			>
				{{ userInitials }}
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
				<q-item clickable v-close-popup @click="openProfile">
					<q-item-section avatar>
						<q-icon name="person" size="sm" color="grey-7" />
					</q-item-section>
					<q-item-section>Профиль</q-item-section>
				</q-item>
				<q-separator />
				<q-item clickable v-close-popup @click="logout">
					<q-item-section avatar>
						<q-icon name="logout" size="sm" color="negative" />
					</q-item-section>
					<q-item-section class="text-negative">Выйти</q-item-section>
				</q-item>
			</q-list>
		</q-menu>
	</q-btn>

	<q-dialog v-model="profileDialog" persistent>
		<q-card class="profile-card">
			<q-card-section>
				<div class="row items-center q-mb-md">
					<q-avatar size="64px" color="primary" text-color="white" icon="person" />
					<div class="q-ml-md">
						<div class="text-h6 text-weight-bold">{{ userStore.fullName }}</div>
						<div class="text-body2 text-grey-7">{{ userStore.email }}</div>
					</div>
				</div>
				<q-list bordered separator class="rounded-borders">
					<q-item>
						<q-item-section>
							<q-item-label caption>Email</q-item-label>
							<q-item-label>{{ userStore.email }}</q-item-label>
						</q-item-section>
					</q-item>
					<q-item>
						<q-item-section>
							<q-item-label caption>Телефон</q-item-label>
							<q-item-label>{{ userStore.phone_number || "—" }}</q-item-label>
						</q-item-section>
					</q-item>
				</q-list>
			</q-card-section>
			<q-card-actions align="right">
				<q-btn flat label="Закрыть" color="primary" v-close-popup />
			</q-card-actions>
		</q-card>
	</q-dialog>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useUserStore } from "@store/userData.js";

const $q = useQuasar();
const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const profileDialog = ref(false);

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

function logout() {
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

.profile-card {
	min-width: 360px;
	max-width: 90vw;
	border-radius: 16px;
	box-shadow: 0 24px 56px rgba(0, 0, 0, 0.14);
	animation: scaleIn 0.3s var(--anim-ease-spring) forwards;
}
</style>
