import {BaseApi} from "./BaseApi.js";

export class TrainingApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	async getTrainings() {
		try {
			super.httpMethod = 'get';
			super.sourceUrl = '/training/my_trainings/';
			return super.createRequest();
		} catch (e) {
			throw new Error(e);
		}
	}

	async createTraining(payload) {
		try {
			super.httpMethod = 'post';
			super.sourceUrl = '/training/create_training';
			super.data = payload;
			return super.createRequest();
		} catch (e) {
			throw new Error(e);
		}
	}

	async deleteTraining(uuid) {
		try {
			super.httpMethod = "delete";
			super.sourceUrl = `/training/${uuid}`;
			return super.createRequest();
		} catch (e) {
			throw new Error(e);
		}
	}

	async updateTraining(uuid, payload) {
		try {
			super.httpMethod = 'patch';
			super.sourceUrl = `/training/${uuid}`
			super.data = payload;
			return super.createRequest();
		} catch (e) {
			throw new Error(e);
		}
	}

}