import { BaseApi } from "./BaseAPi.js";
import axios from "axios";

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

	addStep(trainingUuid, data) {
		super.httpMethod = "post";
		super.sourceUrl = `/training/${trainingUuid}/steps`;
		super.data = data;
		return super.createRequest();
	}

	reorderSteps(trainingUuid, data) {
		super.httpMethod = "patch";
		super.sourceUrl = `/training/${trainingUuid}/steps/reorder`;
		super.data = data;
		return super.createRequest();
	}

	getScenarioGraph(trainingUuid) {
		super.httpMethod = "get";
		super.sourceUrl = `/training/${trainingUuid}/scenario`;
		super.params = {};
		return super.createRequest();
	}

	saveScenarioGraph(trainingUuid, data) {
		super.httpMethod = "put";
		super.sourceUrl = `/training/${trainingUuid}/scenario`;
		super.data = data;
		return super.createRequest();
	}

	deleteStep(trainingUuid, stepId) {
		super.httpMethod = "delete";
		super.sourceUrl = `/training/${trainingUuid}/steps/${stepId}`;
		return super.createRequest();
	}

	replaceStepScreenshot(trainingUuid, stepId, blob, filename = "step-crop.png") {
		const fd = new FormData();
		fd.append("file", blob, filename);
		super.httpMethod = "post";
		super.sourceUrl = `/training/${trainingUuid}/steps/${stepId}/screenshot`;
		super.data = fd;
		super.headers = {};
		return super.createRequest();
	}

	detectStepElements(trainingUuid, stepId) {
		super.httpMethod = "post";
		super.sourceUrl = `/training/${trainingUuid}/steps/${stepId}/detect-elements`;
		return super.createRequest();
	}

	fetchStepScreenshotBlob(trainingUuid, stepId) {
		const token =
			typeof localStorage !== "undefined" ? localStorage.getItem("tokenAuth") : "";
		return axios.get(
			`${__BASE__URL__}/training/${trainingUuid}/steps/${stepId}/screenshot-source`,
			{
				responseType: "blob",
				headers: token ? { Authorization: `Bearer ${token}` } : {},
			}
		);
	}
}

export const trainingStepApi = new TrainingStepApi();