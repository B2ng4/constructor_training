import LoginPage from "@pages/LoginPage.vue";
import PersonalPage from "@pages/PersonalPage.vue";
import Page403 from "@pages/Page403.vue";

export const routes = [
	{ path: "/login", component: LoginPage, name: 'LoginPage' },
	{ path: "/personal", component: PersonalPage, name: 'PersonalPage' },
	{ path: "/403", component: Page403, name: '403' },
];
