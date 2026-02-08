<template>
	<div class="container">
		<BaseCard class="card text-blue-grey-8 shadow-24" width="500px">
			<template v-slot:title>
				<div class="text-white column content-center items-center">
					<h5 class="q-mb-xs">Добро пожаловать</h5>
					<div>Регистрация</div>
					<div>
						Есть аккаунт?
						<router-link class="text-white" to="/login">Вход</router-link>
					</div>
				</div>
			</template>
			<template v-slot:body>
				<div class="column justify-center items-center content-center">
					<q-input
						filled
						label-color="white"
						color="white"
						v-model="user.name"
						label="Имя *"
						lazy-rules
						class="full-width"
						input-style="color: white"
					/>
					<q-input
						filled
						label-color="white"
						color="white"
						v-model="user.surname"
						label="Фамилия *"
						lazy-rules
						class="full-width q-mt-lg"
						input-style="color: white"
					/>
					<q-input
						filled
						label-color="white"
						color="white"
						v-model="user.phone"
						label="Телефон *"
						lazy-rules
						class="full-width q-mt-lg"
						input-style="color: white"
					/>
					<q-input
						filled
						label-color="white"
						color="white"
						v-model="user.email"
						label="Логин *"
						lazy-rules
						class="full-width q-mt-lg"
						input-style="color: white"
					/>
					<q-input
						filled
						:type="isPwd ? 'password' : 'text'"
						label-color="white"
						color="white"
						v-model="user.password"
						label="Пароль *"
						lazy-rules
						class="full-width q-mt-lg"
						input-style="color: white"
					>
						<template v-slot:append>
							<q-icon
								:name="isPwd ? 'visibility_off' : 'visibility'"
								class="cursor-pointer text-white"
								@click="isPwd = !isPwd"
							/>
						</template>
					</q-input>
					<q-btn
						outline
						rounded
						class="q-mt-lg size-button-70"
						color="white"
						@click="onSubmit()"
					>
						<q-spinner-bars v-if="loader === true" color="white" size="2em" />
						<span v-else>Регистрация</span>
					</q-btn>
				</div>
			</template>
		</BaseCard>
	</div>
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
.container {
	height: 100vh;
	width: 50%;
	display: flex;
	justify-content: center;
	align-items: center;
}

.my-card {
	background-color: #6274f8;
	border-radius: 5%;
}
</style>
