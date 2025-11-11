async function loadSurveys() {
    const surveys = await apiGet("/surveys");
    const list = document.getElementById("surveyList");
    list.innerHTML = "";

    surveys.forEach(s => {
        const li = document.createElement("li");
        li.innerHTML = `<a href="survey.html?id=${s.id}">${s.title}</a>`;
        list.appendChild(li);
    });
}

document.addEventListener("DOMContentLoaded", loadSurveys);
