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

	publishTraining(uuid, requiresAuth = false) {
		super.params = { requires_auth: requiresAuth };
		super.httpMethod = 'post';
		super.sourceUrl = `/training/${uuid}/publish`;
		return super.createRequest();
	}

	uploadIcon(uuid, formData) {
		super.params = {};
		super.httpMethod = 'post';
		super.sourceUrl = `/training/upload-icon/${uuid}`;
		super.data = formData;
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

	async streamRewriteTaskText(text, onChunk) {
		const token = localStorage.getItem("tokenAuth");
		const response = await fetch(`${__BASE__URL__}/training/ai/rewrite-task`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				...(token ? { "Authorization": `Bearer ${token}` } : {})
			},
			body: JSON.stringify({ text })
		});

		if (!response.ok) {
			throw new Error("Network response was not ok");
		}

		const reader = response.body.getReader();
		const decoder = new TextDecoder("utf-8");

		while (true) {
			const { value, done } = await reader.read();
			if (done) break;
			const chunk = decoder.decode(value, { stream: true });
			if (chunk) onChunk(chunk);
		}
	}

	generateStepTTS(trainingUuid, stepId) {
		super.params = {};
		super.httpMethod = 'post';
		super.sourceUrl = `/training/${trainingUuid}/steps/${stepId}/tts`;
		super.data = {};
		return super.createRequest();
	}

	uploadPdf(trainingUuid, file) {
		const formData = new FormData();
		formData.append('file', file);
		super.params = {};
		super.httpMethod = 'post';
		super.sourceUrl = `/training/upload-pdf/${trainingUuid}`;
		super.data = formData;
		super.headers = { 'Content-Type': 'multipart/form-data' };
		return super.createRequest();
	}
}

export const trainingApi = new TrainingApi();
