import { createWebHistory, createRouter } from "vue-router";
import { routes } from "./routes.js";
import { checkAuth } from "@utils/checkAuth.js";

const router = createRouter({
	history: createWebHistory(),
	routes,
});

router.beforeEach(async (to, from, next) => {
	if (to.path.startsWith("/personal")) {
		const tokenAuth = localStorage.getItem("tokenAuth");
		let auth = { status: false };
		if (tokenAuth) {
			auth = await checkAuth(tokenAuth);
		}
		if (!auth.status) {
			next({ path: "/login", query: { redirect: to.fullPath } });
		} else {
			next();
		}
	} else {
		next();
	}
});

export default router;
