import LoginPage from "@pages/LoginPage.vue";
import PersonalPage from "@pages/PersonalPage.vue";
import Page403 from "@pages/Page403.vue";
import RegistrationPage from "@pages/RegistrationPage.vue";

export const routes = [
	{ path: "/login", component: LoginPage, name: 'LoginPage' },
	{ path: "/registration", component: RegistrationPage},
	{ path: "/personal", component: PersonalPage, name: 'PersonalPage' },
	{ path: "/403", component: Page403, name: '403' },
];
