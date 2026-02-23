import {
	EditPage,
	HelpPage,
	HomePage,
	LandingPage,
	LibraryPage,
	LoginPage,
	Page403,
	PersonalPage,
	RegistrationPage,
	TrainingPage,
	PassageTraining,
	TrainingWelcomePage,
	TrainingPlayPage,
} from "@pages";

export const routes = [
	{ path: "/", component: LandingPage, name: 'LandingPage' },
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
	{
		path: "/training/passage/:accessToken",
		component: PassageTraining,
		redirect: (to) => ({ path: `${to.path}/welcome` }),
		children: [
			{
				path: "welcome",
				name: "TrainingWelcome",
				component: TrainingWelcomePage,
			},
			{
				path: "play",
				name: "TrainingPlay",
				component: TrainingPlayPage,
			},
		],
	},
];
