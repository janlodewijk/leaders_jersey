document.addEventListener("DOMContentLoaded", function () {
    const countdowns = document.querySelectorAll("[id^='countdown-stage-']");

    countdowns.forEach(countdownSpan => {
        const deadlineStr = countdownSpan.getAttribute("data-deadline");
        const deadline = new Date(deadlineStr);

        function updateCountdown() {
            const now = new Date();
            const diff = deadline - now;

            if (diff <= 0) {
                countdownSpan.textContent = "Locked";
                return;
            }

            const totalSeconds = Math.floor(diff / 1000);
            const seconds = totalSeconds % 60;
            const minutes = Math.floor((totalSeconds / 60) % 60);
            const hours = Math.floor((totalSeconds / 3600) % 24);
            const days = Math.floor(totalSeconds / 86400);

            countdownSpan.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
        }

        updateCountdown();
        setInterval(updateCountdown, 1000);
    });
});
