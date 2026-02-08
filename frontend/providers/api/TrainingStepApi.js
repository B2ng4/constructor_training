import {BaseApi} from "./BaseAPi.js";

export class TrainingStepApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	editStep(trainingUuid, stepId, data) {
		super.httpMethod = "patch";
		super.sourceUrl = `/training/${trainingUuid}/steps/${stepId}`;
		super.data = data;
		return super.createRequest();
	}

	reorderSteps(trainingUuid, data) {
		super.httpMethod = "patch";
		super.sourceUrl = `/training/${trainingUuid}/steps/reorder`;
		super.data = data;
		return super.createRequest();
	}
}

export const trainingStepApi = new TrainingStepApi();