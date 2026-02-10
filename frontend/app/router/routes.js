import {
	EditPage,
	HelpPage,
	HomePage,
	LibraryPage,
	LoginPage,
	Page403,
	PersonalPage,
	RegistrationPage,
	TrainingPage,
	CompleteTraining
} from "@pages";

export const routes = [
	{path: "/", redirect: "/login" },
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
				path: '/personal/training',
				component: TrainingPage,
			},
			{
				path: '/personal/help',
				component: HelpPage,
			},
		]
	},
	{ path: "/403", component: Page403, name: '403' },
	{ path: "/edit/:uuid", component: EditPage },
	{path: '/public/:access-token', component: CompleteTraining}
];
