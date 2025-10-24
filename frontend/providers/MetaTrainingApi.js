import {BaseApi} from "./BaseApi.js";

export class MetaTrainingApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	async getTags() {
		try {
			super.httpMethod = 'get';
			super.sourceUrl = '/tags/';
			return super.createRequest();
		} catch (e) {
			throw new Error(e);
		}
	}

	async getLevels() {
		try {
			super.httpMethod = "get";
			super.sourceUrl = "/levels/";
			return super.createRequest();
		} catch (e) {
			throw new Error(e);
		}
	}

}