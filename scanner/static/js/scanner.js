document.addEventListener("DOMContentLoaded", function () {
    const binButtons = document.querySelectorAll(".bin-button");
    const resultDiv = document.getElementById("result");
    const scoreDiv = document.getElementById("score");

    binButtons.forEach(button => {
        button.addEventListener("click", function () {
            const chosenBin = this.getAttribute("data-bin");
            const correctBin = document.getElementById("correct-bin").value;
            const userId = document.getElementById("user-id").value;

            fetch("/validate-bin-choice/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    user_id: userId,
                    chosen_bin: chosenBin,
                    correct_bin: correctBin
                })
            })
                .then(response => response.json())
                .then(data => {
                    resultDiv.textContent = data.message;
                    scoreDiv.textContent = `Score total : ${data.total_score}`;
                })
                .catch(error => console.error("Erreur :", error));
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
