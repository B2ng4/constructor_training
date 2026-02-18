<template>
	<BaseCard class="registration-card" width="500px">
		<template v-slot:title>
			<div class="column content-center items-center auth-title">
				<h5 class="q-mb-xs auth-heading">Добро пожаловать</h5>
				<div class="auth-sub">Регистрация</div>
				<div class="auth-switch">
					Есть аккаунт?
					<router-link class="auth-link" to="/login">Вход</router-link>
				</div>
			</div>
		</template>
		<template v-slot:body>
			<div class="column justify-center items-center content-center auth-body">
				<q-input
					filled
					v-model="user.name"
					label="Имя *"
					lazy-rules
					class="full-width auth-input"
					color="primary"
				/>
				<q-input
					filled
					v-model="user.surname"
					label="Фамилия *"
					lazy-rules
					class="full-width q-mt-lg auth-input"
					color="primary"
				/>
				<q-input
					filled
					v-model="user.phone"
					label="Телефон *"
					lazy-rules
					class="full-width q-mt-lg auth-input"
					color="primary"
				/>
				<q-input
					filled
					v-model="user.email"
					label="Логин *"
					lazy-rules
					class="full-width q-mt-lg auth-input"
					color="primary"
				/>
				<q-input
					filled
					:type="isPwd ? 'password' : 'text'"
					v-model="user.password"
					label="Пароль *"
					lazy-rules
					class="full-width q-mt-lg auth-input"
					color="primary"
				>
					<template v-slot:append>
						<q-icon
							:name="isPwd ? 'visibility_off' : 'visibility'"
							class="cursor-pointer"
							@click="isPwd = !isPwd"
						/>
					</template>
				</q-input>
				<q-btn
					unelevated
					rounded
					class="q-mt-lg size-button-70 auth-btn"
					color="primary"
					@click="onSubmit()"
				>
					<q-spinner-bars v-if="loader === true" color="white" size="2em" />
					<span v-else>Регистрация</span>
				</q-btn>
			</div>
		</template>
	</BaseCard>
</template>

<script>
import { BaseCard } from "@components/base_components";
import axios from "axios";
export default {
	name: "RegistrationForm",
	components: { BaseCard },
	data() {
		return {
			user: {
				surname: "",
				name: "",
				phone: "",
				email: "",
				password: "",
			},

			isPwd: true,
			loader: false,
		};
	},
	methods: {
		async onSubmit() {
			this.loader = true;
			axios
				.post(`${__BASE__URL__}/auth/register`, {
					email: this.user.email,
					phone_number: this.user.phone,
					first_name: this.user.name,
					last_name: this.user.surname,
					password: this.user.password,
				})
				.then(() => {
					this.$q.notify({
						position: "top",
						type: "positive",
						message: "Успех!",
					});
					this.$router.push("/login");
				})
				.catch(() => {
					this.$q.notify({
						position: "top",
						type: "negative",
						message: "Произошла ошибка!",
					});
				})
				.finally(() => {
					this.loader = false;
				});
		},
	},
};
</script>

<style scoped>
.registration-card {
	background: #ffffff;
	box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
	border: 1px solid #e2e8f0;
	border-radius: 20px;
	overflow: hidden;
	animation: scaleIn 0.4s var(--anim-ease-spring) forwards;
}
.registration-card :deep(.q-card__section) {
	transition: background 0.2s ease;
}
.auth-title {
	padding: 28px 24px 20px;
	color: #1a1a2e;
}
.auth-heading {
	font-size: 1.5rem;
	font-weight: 700;
	letter-spacing: -0.02em;
	color: #1a1a2e;
}
.auth-sub {
	font-size: 0.95rem;
	color: #64748b;
	margin-top: 4px;
}
.auth-switch {
	font-size: 0.9rem;
	margin-top: 12px;
	color: #64748b;
}
.auth-link {
	color: #5064f7;
	text-decoration: none;
	font-weight: 600;
	transition: opacity 0.2s ease;
}
.auth-link:hover {
	opacity: 0.85;
	text-decoration: underline;
}
.auth-body {
	padding: 8px 24px 28px;
}
.auth-input :deep(.q-field__control) {
	border-radius: 12px;
	transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.auth-input :deep(.q-field--focused .q-field__control) {
	box-shadow: 0 0 0 2px rgba(80, 100, 247, 0.25);
}
/* Стили автозаполнения — как у обычных filled-полей Quasar */
.auth-input :deep(input:-webkit-autofill),
.auth-input :deep(input:-webkit-autofill:hover),
.auth-input :deep(input:-webkit-autofill:focus),
.auth-input :deep(input:-webkit-autofill:active) {
	-webkit-box-shadow: 0 0 0 100px rgba(0, 0, 0, 0.05) inset !important;
	box-shadow: 0 0 0 100px rgba(0, 0, 0, 0.05) inset !important;
	-webkit-text-fill-color: #1a1a2e !important;
	caret-color: #1a1a2e;
	transition: background-color 5000s ease-in-out 0s;
}
.auth-input :deep(.q-field__control::before) {
	border-color: rgba(0, 0, 0, 0.24);
}
.auth-btn {
	transition: transform 0.25s var(--anim-ease-spring), box-shadow 0.25s ease;
}
.auth-btn:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 16px rgba(80, 100, 247, 0.3);
}
.auth-btn:active {
	transform: translateY(0);
}
</style>
