import {BaseApi} from "./BaseAPi.js";

export class TrainingApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	getTrainings() {
		super.params = {};
		super.httpMethod = 'get';
		super.sourceUrl = '/training/my_trainings/';
		return super.createRequest();
	}

	createTraining(payload) {
		super.params = {};
		super.httpMethod = 'post';
		super.sourceUrl = '/training/create_training';
		super.data = payload;
		return super.createRequest();
	}

	deleteTraining(uuid) {
		super.params = {};
		super.httpMethod = "delete";
		super.sourceUrl = `/training/${uuid}`;
		return super.createRequest();
	}

	updateTraining(uuid, payload) {
		super.params = {};
		super.httpMethod = 'patch';
		super.sourceUrl = `/training/${uuid}`;
		super.data = payload;
		return super.createRequest();
	}

	getTrainingByUuid(uuid) {
		super.params = {};
		super.httpMethod = 'get';
		super.sourceUrl = `/training/${uuid}`;
		return super.createRequest();
	}

	publishTraining(uuid) {
		super.params = {};
		super.httpMethod = 'post';
		super.sourceUrl = `/training/${uuid}/publish`;
		return super.createRequest();
	}

	unpublishTraining(uuid) {
		super.params = {};
		super.httpMethod = 'post';
		super.sourceUrl = `/training/${uuid}/unpublish`;
		return super.createRequest();
	}

	getPublicTraining(accessToken) {
		super.params = {};
		super.httpMethod = 'get';
		super.sourceUrl = `/training/public/${accessToken}`;
		return super.createRequest();
	}

	startPassageAttempt(accessToken) {
		super.params = {};
		super.httpMethod = 'post';
		super.sourceUrl = `/training/public/${accessToken}/passage/start`;
		super.data = {};
		return super.createRequest();
	}

	completePassageAttempt(accessToken, payload) {
		super.params = {};
		super.httpMethod = 'post';
		super.sourceUrl = `/training/public/${accessToken}/passage/complete`;
		super.data = payload;
		return super.createRequest();
	}

	getPassageAnalytics(uuid) {
		super.params = {};
		super.httpMethod = 'get';
		super.sourceUrl = `/training/${uuid}/passage-analytics`;
		return super.createRequest();
	}

	getPassageHistory(uuid, params = {}) {
		super.httpMethod = 'get';
		super.sourceUrl = `/training/${uuid}/passage-history`;
		super.params = params;
		return super.createRequest();
	}
}

export const trainingApi = new TrainingApi();
