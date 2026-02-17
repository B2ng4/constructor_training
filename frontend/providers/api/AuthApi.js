import { BaseApi } from "./BaseAPi.js";

export class AuthApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	getMe() {
		super.httpMethod = "get";
		super.sourceUrl = "/auth/me/";
		return super.createRequest();
	}
}

export const authApi = new AuthApi();
