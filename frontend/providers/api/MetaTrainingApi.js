import { BaseApi } from "./BaseAPi.js";

export class MetaTrainingApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	getTags() {
		this.httpMethod = "get";
		this.sourceUrl = "/tags/";
		this.data = {};
		this.params = {};
		return this.createRequest();
	}

	createTag(label) {
		const body = { label: String(label || "").trim() };
		this.httpMethod = "post";
		this.sourceUrl = "/tags/";
		this.data = body;
		this.params = {};
		return this.createRequest();
	}

	getLevels() {
		this.httpMethod = "get";
		this.sourceUrl = "/levels/";
		this.data = {};
		this.params = {};
		return this.createRequest();
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
