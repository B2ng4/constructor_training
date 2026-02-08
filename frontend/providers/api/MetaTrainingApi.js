import { BaseApi } from "./BaseAPi.js";

export class MetaTrainingApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	getTags() {
		super.httpMethod = "get";
		super.sourceUrl = "/tags/";
		return super.createRequest();
	}

	getLevels() {
		super.httpMethod = "get";
		super.sourceUrl = "/levels/";
		return super.createRequest();
	}

	uploadImages(uuid, data) {
		super.httpMethod = "post";
		super.sourceUrl = `/training/upload-photos/${uuid}`;
		super.data = data;
		return super.createRequest();
	}
}
