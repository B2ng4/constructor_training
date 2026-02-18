<template>
	<q-btn rounded color="primary" text-color="white" class="user-btn" :loading="loading">
		<q-icon class="q-mr-sm" name="person" size="20px" />
		<span class="user-name">{{ userStore.fullName }}</span>
		<q-menu fit anchor="bottom right" self="top right" :offset="[0, 8]">
			<q-list class="user-menu-list">
				<q-item>
					<q-item-section>
						<q-item-label class="text-weight-medium">{{ userStore.fullName }}</q-item-label>
						<q-item-label caption>{{ userStore.email }}</q-item-label>
					</q-item-section>
				</q-item>
				<q-separator />
				<q-item clickable v-close-popup @click="$router.push('/personal/home')">
					<q-item-section avatar>
						<q-icon name="home" size="sm" />
					</q-item-section>
					<q-item-section>Главная</q-item-section>
				</q-item>
				<q-item clickable v-close-popup @click="openProfile">
					<q-item-section avatar>
						<q-icon name="person" size="sm" />
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@store/userData.js";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const profileDialog = ref(false);

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
.user-btn {
	min-width: 120px;
	transition: transform 0.25s var(--anim-ease-spring), box-shadow 0.25s ease, opacity 0.2s ease;
}
.user-btn:hover {
	transform: translateY(-1px);
	box-shadow: 0 4px 12px rgba(98, 116, 248, 0.25);
}
.user-btn:active {
	transform: translateY(0);
}

.user-name {
	max-width: 140px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
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
