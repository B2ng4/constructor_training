import { authApi } from "@api";
import { useUserStore } from "@store/userData.js";

export async function checkAuth(tokenAuth) {
	if (!tokenAuth) return { status: false };
	try {
		const { data } = await authApi.getMe();
		useUserStore().setUser(data);
		return { dataUser: data, status: true };
	} catch {
		useUserStore().clearUser();
		return { status: false };
	}
}