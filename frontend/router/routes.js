import LoginPage from "@pages/LoginPage.vue";
import PersonalPage from "@pages/PersonalPage.vue";
import Page403 from "@pages/Page403.vue";
import RegistrationPage from "@pages/RegistrationPage.vue";
import HomePage from "@pages/HomePage.vue";
import LibraryPage from "@pages/LibraryPage.vue";
import TraningPage from "@pages/TraningPage.vue";
import HelpPage from "@pages/HelpPage.vue";

export const routes = [
	{ path: "/login", component: LoginPage, name: 'LoginPage' },
	{ path: "/registration", component: RegistrationPage},
	{ 	
		path: "/personal", 
		component: PersonalPage, 
		name: 'PersonalPage',
		redirect: '/personal/home',
		children: [
			{
				path: '/personal/home',
				component: HomePage,
			},
			{
				path: '/personal/library',
				component: LibraryPage,
			},
			{
				path: '/personal/traning',
				component: TraningPage,
			},
			{
				path: '/personal/help',
				component: HelpPage,
			},
		]
	},
	{ path: "/403", component: Page403, name: '403' },
];
