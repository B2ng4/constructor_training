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
}