import { ref, computed, onMounted, onUnmounted } from "vue";

/**
 * Таймер прохождения: обратный отсчёт по duration_minutes, при 0 — «время вышло».
 */
export function usePassageTimer(durationMinutesRef, onTimeUp) {
	const totalDurationSeconds = computed(() => {
		const min = typeof durationMinutesRef?.value === "number" ? durationMinutesRef.value : 0;
		return Math.max(0, min * 60);
	});

	const timeRemaining = ref(0);
	const totalSecondsSpent = ref(0);
	let intervalId = null;

	function formatTime(seconds) {
		const s = Math.floor(Math.abs(seconds));
		const m = Math.floor(s / 60);
		const sec = s % 60;
		return `${m}:${sec.toString().padStart(2, "0")}`;
	}

	const timerProgress = computed(() => {
		const total = totalDurationSeconds.value;
		if (total <= 0) return 1;
		const spent = total - timeRemaining.value;
		return Math.min(1, Math.max(0, spent / total));
	});

	function start() {
		const total = totalDurationSeconds.value;
		if (total <= 0) return;
		timeRemaining.value = total;
		totalSecondsSpent.value = 0;
		intervalId = setInterval(() => {
			timeRemaining.value = Math.max(0, timeRemaining.value - 1);
			totalSecondsSpent.value = totalDurationSeconds.value - timeRemaining.value;
			if (timeRemaining.value <= 0) {
				stop();
				onTimeUp?.();
			}
		}, 1000);
	}

	function stop() {
		if (intervalId) {
			clearInterval(intervalId);
			intervalId = null;
		}
	}

	onMounted(() => {
		start();
	});

	onUnmounted(() => {
		stop();
	});

	return {
		timeRemaining,
		totalSecondsSpent,
		totalDurationSeconds,
		timerProgress,
		formatTime,
		start,
		stop,
	};
}
