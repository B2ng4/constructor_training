import { defineStore } from "pinia";
import { authApi } from "@api";

export const useUserStore = defineStore("user", {
	state: () => ({
		id: null,
		email: "",
		phone_number: "",
		first_name: "",
		last_name: "",
		isLoaded: false,
	}),
	getters: {
		getName: (state) => state.first_name || "Пользователь",
		fullName: (state) =>
			[state.first_name, state.last_name].filter(Boolean).join(" ") || "Пользователь",
		isLoggedIn: (state) => !!state.id,
	},
	actions: {
		setUser(user) {
			if (!user) return;
			this.id = user.id;
			this.email = user.email || "";
			this.phone_number = user.phone_number || "";
			this.first_name = user.first_name || "";
			this.last_name = user.last_name || "";
			this.isLoaded = true;
		},
		clearUser() {
			this.id = null;
			this.email = "";
			this.phone_number = "";
			this.first_name = "";
			this.last_name = "";
			this.isLoaded = false;
		},
		async fetchUser() {
			try {
				const { data } = await authApi.getMe();
				this.setUser(data);
				return data;
			} catch {
				this.clearUser();
				return null;
			}
		},
	},
});