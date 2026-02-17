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

	createTag(label) {
		super.httpMethod = "post";
		super.sourceUrl = "/tags/";
		super.data = { label };
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

	uploadVideo(uuid, formData) {
		super.httpMethod = "post";
		super.sourceUrl = `/training/upload-video/${uuid}`;
		super.data = formData;
		return super.createRequest();
	}
}
