import LoginPage from "../pages/LoginPage.vue"
import WelcomePage from "../pages/WelcomePage.vue"

export const routes = [
    { path: '/', component: WelcomePage },
    { path: '/login', component: LoginPage}
]