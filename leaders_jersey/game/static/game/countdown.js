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
                clearInterval(intervalId); 

                if (document.visibilityState === "visible") {  // 👀 Only reload if user is actually looking
                    showLoadingSpinner();                      // 🌀 Show spinner
                    setTimeout(() => location.reload(), 500);  // 🔄 Reload after 0.5s
                }

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
        const intervalId = setInterval(updateCountdown, 1000);
    });

    function showLoadingSpinner() {
        const spinner = document.createElement('div');
        spinner.innerHTML = `
            <div style="
                position: fixed; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%);
                background: rgba(255, 255, 255, 0.9);
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);
                z-index: 9999;
                text-align: center;
            ">
                <div style="
                    border: 5px solid #f3f3f3;
                    border-top: 5px solid #3498db;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 10px auto;
                "></div>
                <div style="font-size: 18px; font-weight: bold;">Reloading...</div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(spinner);
    }
});
