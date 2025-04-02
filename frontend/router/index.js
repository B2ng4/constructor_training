import { createWebHistory, createRouter } from "vue-router";
import { routes } from "./routes";
import { checkAuth } from "../utils/checkAuth";

const router = createRouter({
	history: createWebHistory(),
	routes,
});

router.beforeEach(async (to, from, next) => {
    if (to.name === 'PersonalPage') { //в личный кабинет можно перейти только с токеном авторизации

		let tokenAuth = localStorage.getItem('tokenAuth')
		let auth = false

		if (tokenAuth) {
			auth = await checkAuth(tokenAuth)
		}
        if (!auth.status) {
            next({ name: '403' })
        } else {
            next()
        }
    } else {
        next()
    }
});

export default router;
