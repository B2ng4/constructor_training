import LoginPage from "../pages/LoginPage.vue";
import WelcomePage from "../pages/WelcomePage.vue";
import RegistrationPage from "../pages/RegistrationPage.vue";
import PersonalPage from "../pages/PersonalPage.vue";
import Page403 from "../pages/Page403.vue"

export const routes = [
	{ path: "/", component: WelcomePage },
	{ path: "/login", component: LoginPage },
	{ path: "/registration", component: RegistrationPage },
	{ path: "/personal", component: PersonalPage, name: 'PersonalPage' },
	{ path: "/403", component: Page403, name: '403' },
];
