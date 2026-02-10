import {BaseApi} from "./BaseAPi.js";

export class TrainingApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	getTrainings() {
		super.httpMethod = 'get';
		super.sourceUrl = '/training/my_trainings/';
		return super.createRequest();
	}

	createTraining(payload) {
		super.httpMethod = 'post';
		super.sourceUrl = '/training/create_training';
		super.data = payload;
		return super.createRequest();
	}

	deleteTraining(uuid) {
		super.httpMethod = "delete";
		super.sourceUrl = `/training/${uuid}`;
		return super.createRequest();
	}

	updateTraining(uuid, payload) {
		super.httpMethod = 'patch';
		super.sourceUrl = `/training/${uuid}`;
		super.data = payload;
		return super.createRequest();
	}

	getTrainingByUuid(uuid) {
		super.httpMethod = 'get';
		super.sourceUrl = `/training/${uuid}`;
		return super.createRequest();
	}
}

export const trainingApi = new TrainingApi();