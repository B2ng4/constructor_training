import { BaseApi } from "./BaseAPi.js";

export class MetaTrainingApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	async getTags() {
		try {
			super.httpMethod = "get";
			super.sourceUrl = "/tags/";
			return super.createRequest();
		} catch (e) {
			console.log(e);
		}
	}

	async getLevels() {
		super.httpMethod = "get";
		super.sourceUrl = "/levels/";
		return super.createRequest();
	}

	async uploadImages(uuid, data) {
		super.httpMethod = "post";
		super.sourceUrl = `/training/upload-photos/${uuid}`;
		super.data = data;
		return await super.createRequest();
	}
}
