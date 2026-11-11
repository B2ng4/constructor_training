import { defineStore } from "pinia";
import { Notify } from "quasar";
import { tasksApi } from "@api";
import {
	isSystemNotificationSupported,
	requestSystemNotificationPermission,
	showSystemNotification,
} from "@utils/systemNotifications.js";

function wsBaseUrl() {
	let base = typeof __BASE__URL__ !== "undefined" ? __BASE__URL__ : "http://localhost:8002";
	if (base.startsWith("/")) {
		const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
		base = `${protocol}//${window.location.host}${base.replace(/\/$/, "")}`;
	} else {
		base = base.replace(/^https?/, (match) => (match === "https" ? "wss" : "ws"));
	}
	return base;
}

function normalizeTask(raw) {
	const taskId = raw.task_id || raw.id;
	if (!taskId) return null;
	return {
		task_id: String(taskId),
		status: raw.status || "pending",
		progress: Number(raw.progress ?? 0),
		message: raw.message || null,
		training_uuid: raw.training_uuid ? String(raw.training_uuid) : null,
		original_filename: raw.original_filename || null,
		steps_created: raw.steps_created ?? null,
		error_message: raw.error_message || null,
		task_type: raw.task_type || null,
		updatedAt: Date.now(),
	};
}

const ACTIVE_STATUSES = new Set(["pending", "processing"]);

function dedupeActiveTasks(tasks) {
	const byKey = new Map();
	for (const task of tasks) {
		const key = task.training_uuid || task.task_id;
		const prev = byKey.get(key);
		if (!prev || (task.updatedAt || 0) >= (prev.updatedAt || 0)) {
			byKey.set(key, task);
		}
	}
	return Array.from(byKey.values()).sort(
		(a, b) => (b.updatedAt || 0) - (a.updatedAt || 0)
	);
}

export function ensureNotificationsConnected() {
	const store = useNotificationsStore();
	store.connect();
	return store;
}

export const useNotificationsStore = defineStore("notifications", {
	state: () => ({
		socket: null,
		connected: false,
		reconnectTimer: null,
		pingTimer: null,
		taskUpdates: {},
		notifiedTerminal: {},
	}),

	getters: {
		activeTasks(state) {
			const active = Object.values(state.taskUpdates).filter((t) =>
				ACTIVE_STATUSES.has(t.status)
			);
			return dedupeActiveTasks(active);
		},
		activeTaskCount() {
			return this.activeTasks.length;
		},
		isProcessing() {
			return this.activeTaskCount > 0;
		},
	},

	actions: {
		connect() {
			const token = localStorage.getItem("tokenAuth");
			if (!token) return;

			if (this.socket) {
				const state = this.socket.readyState;
				if (state === WebSocket.OPEN || state === WebSocket.CONNECTING) {
					return;
				}
				this._clearSocket();
			}

			const url = `${wsBaseUrl()}/ws/notifications`;
			const ws = new WebSocket(url, [`bearer.${token}`]);

			ws.onopen = () => {
				this.connected = true;
				this.syncActiveTasks();
				this._startPing(ws);
			};

			ws.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					this.handleMessage(data);
				} catch {
					/* ignore */
				}
			};

			ws.onclose = () => {
				this.connected = false;
				this._clearPing();
				this.socket = null;
				this.scheduleReconnect();
			};

			ws.onerror = () => {
				ws.close();
			};

			this.socket = ws;
		},

		_startPing(ws) {
			this._clearPing();
			this.pingTimer = setInterval(() => {
				if (ws.readyState === WebSocket.OPEN) {
					ws.send("ping");
				}
			}, 25000);
		},

		_clearPing() {
			if (this.pingTimer) {
				clearInterval(this.pingTimer);
				this.pingTimer = null;
			}
		},

		_clearSocket() {
			this._clearPing();
			if (this.socket) {
				this.socket.onclose = null;
				this.socket.close();
				this.socket = null;
			}
			this.connected = false;
		},

		scheduleReconnect() {
			if (this.reconnectTimer) return;
			if (!localStorage.getItem("tokenAuth")) return;
			this.reconnectTimer = setTimeout(() => {
				this.reconnectTimer = null;
				this.connect();
			}, 5000);
		},

		disconnect() {
			if (this.reconnectTimer) {
				clearTimeout(this.reconnectTimer);
				this.reconnectTimer = null;
			}
			this._clearSocket();
		},

		registerTask(raw) {
			const task = normalizeTask(raw);
			if (!task) return null;

			const prev = this.taskUpdates[task.task_id];
			if (prev) {
				task.progress = Math.max(prev.progress || 0, task.progress || 0);
				if (
					prev.message &&
					(!raw.message || (task.progress || 0) <= (prev.progress || 0))
				) {
					task.message = prev.message;
				}
			}

			this.taskUpdates[task.task_id] = {
				...prev,
				...task,
				updatedAt: Date.now(),
			};

			if (!ACTIVE_STATUSES.has(task.status)) {
				this.pruneStaleTasks();
			}

			return { task, prevStatus: prev?.status || null };
		},

		pruneStaleTasks() {
			for (const [id, task] of Object.entries(this.taskUpdates)) {
				if (!ACTIVE_STATUSES.has(task.status)) {
					delete this.taskUpdates[id];
				}
			}
		},

		_notifyCompleted(data) {
			const taskId = String(data.task_id || data.id || "");
			if (taskId && this.notifiedTerminal[taskId]) return;
			if (taskId) this.notifiedTerminal[taskId] = "completed";

			const title = data.message || "Тренинг готов";
			const caption = data.steps_created
				? `Создано шагов: ${data.steps_created}. Можно открыть редактор.`
				: "Шаги успешно добавлены в тренинг.";

			if (document.hidden) {
				showSystemNotification({
					title,
					body: caption,
					tag: taskId ? `training-completed-${taskId}` : undefined,
					trainingUuid: data.training_uuid,
				});
			} else {
				Notify.create({
					message: title,
					caption,
					type: "positive",
					position: "top-right",
					icon: "check_circle",
					timeout: 10000,
					color: "positive",
					classes: "beautiful-notify",
					actions: [
						{
							label: "Открыть тренинг",
							color: "white",
							handler: () => {
								if (data.training_uuid) {
									window.location.href = `/edit/${data.training_uuid}`;
								}
							},
						},
						{ label: "Закрыть", color: "white", handler: () => {} },
					],
				});
			}
		},

		_notifyFailed(data) {
			const taskId = String(data.task_id || data.id || "");
			if (taskId && this.notifiedTerminal[taskId]) return;
			if (taskId) this.notifiedTerminal[taskId] = "failed";

			const isPdf = data.task_type === "pdf_processing";
			const defaultTitle = isPdf ? "Ошибка обработки PDF" : "Ошибка обработки видео";
			const defaultCaption = isPdf ? "Попробуйте загрузить файл ещё раз." : "Попробуйте загрузить видео ещё раз.";

			const title = data.error_message || data.message || defaultTitle;
			const caption = defaultCaption;

			if (document.hidden) {
				showSystemNotification({
					title: defaultTitle,
					body: title,
					tag: taskId ? `training-failed-${taskId}` : undefined,
				});
			} else {
				Notify.create({
					type: "negative",
					message: title,
					caption,
					position: "top-right",
					icon: "error",
					timeout: 8000,
				});
			}
		},

		async prepareSystemNotifications() {
			if (!isSystemNotificationSupported()) return "unsupported";
			return requestSystemNotificationPermission();
		},

		_emitTrainingUpdate(data) {
			if (data.training_uuid) {
				window.dispatchEvent(
					new CustomEvent("training-task-update", { detail: data })
				);
			}
		},

		async syncActiveTasks() {
			try {
				const { data } = await tasksApi.listTasks(true);
				const activeIds = new Set(
					(data || []).map((row) => String(row.id || row.task_id))
				);

				for (const [id, task] of Object.entries(this.taskUpdates)) {
					if (ACTIVE_STATUSES.has(task.status) && !activeIds.has(id)) {
						delete this.taskUpdates[id];
					}
				}

				for (const row of data || []) {
					this.registerTask(row);
				}
			} catch {
				/* ignore if not auth */
			}
		},

		async pollTaskProgress() {
			if (!localStorage.getItem("tokenAuth")) return;

			// Не дёргаем API, если WebSocket жив и нет активных задач.
			if (this.connected && !this.isProcessing) {
				return;
			}

			if (!this.connected) {
				this.connect();
			}

			try {
				const { data: activeRows } = await tasksApi.listTasks(true);
				const activeIds = new Set();

				for (const row of activeRows || []) {
					const id = String(row.id || row.task_id);
					activeIds.add(id);
					const { prevStatus } = this.registerTask(row) || {};
					const payload = { ...row, task_id: id, type: "task_update" };
					this._emitTrainingUpdate(payload);
					if (row.status === "completed" && ACTIVE_STATUSES.has(prevStatus)) {
						this._notifyCompleted(payload);
					} else if (row.status === "failed" && ACTIVE_STATUSES.has(prevStatus)) {
						this._notifyFailed(payload);
					}
				}

				const tracked = Object.entries({ ...this.taskUpdates });
				for (const [id, task] of tracked) {
					if (!ACTIVE_STATUSES.has(task.status) || activeIds.has(id)) continue;
					try {
						const { data: full } = await tasksApi.getTask(id);
						if (!full) continue;
						const { prevStatus } = this.registerTask(full) || {};
						const payload = {
							...full,
							task_id: id,
							type: "task_update",
						};
						this._emitTrainingUpdate(payload);
						if (full.status === "completed" && ACTIVE_STATUSES.has(prevStatus)) {
							this._notifyCompleted(payload);
						} else if (full.status === "failed" && ACTIVE_STATUSES.has(prevStatus)) {
							this._notifyFailed(payload);
						}
					} catch {
						/* task may have been removed */
					}
				}
			} catch {
				/* ignore polling errors */
			}
		},

		handleMessage(data) {
			if (data.type === "connected" || data.type === "pong") {
				return;
			}

			if (data.type === "task_update" && data.task_id) {
				const { prevStatus } = this.registerTask(data) || {};
				this._emitTrainingUpdate(data);

				const status = data.status;
				if (status === "completed") {
					if (!prevStatus || ACTIVE_STATUSES.has(prevStatus)) {
						this._notifyCompleted(data);
					}
				} else if (status === "failed") {
					if (!prevStatus || ACTIVE_STATUSES.has(prevStatus)) {
						this._notifyFailed(data);
					}
				}
			}
		},
	},
});
