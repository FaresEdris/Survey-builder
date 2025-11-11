// survey.js
async function loadSurveys() {
  const surveys = await apiGet("/surveys");
  const list = document.getElementById("surveyList");
  list.innerHTML = "";

  if (!surveys || surveys.length === 0) {
    list.innerHTML = "<li>No surveys found.</li>";
    return;
  }

  surveys.forEach(s => {
    const li = document.createElement("li");

    // Use a button so we don't navigate away; prevents default anchor behavior
    const btn = document.createElement("button");
    btn.textContent = s.title;
    btn.className = "link-like";
    btn.addEventListener("click", () => showSurveyDetail(s.id));

    li.appendChild(btn);
    list.appendChild(li);
  });
}

async function showSurveyDetail(id) {
  // fetch selected survey
  let survey;
  try {
    survey = await apiGet(`/surveys/${id}`);
  } catch (err) {
    alert("Failed to load survey.");
    return;
  }

  // hide list, show details area
  document.getElementById("surveyList").style.display = "none";
  const details = document.getElementById("surveyDetails");
  details.style.display = "block";

  // fill title
  document.getElementById("title").textContent = survey.title || "Untitled survey";

  // render questions
  const form = document.getElementById("responseForm");
  form.innerHTML = "";

  survey.questions.forEach(q => {
    const qDiv = document.createElement("div");
    qDiv.className = "question";

    const label = document.createElement("p");
    label.textContent = q.text;
    qDiv.appendChild(label);

    if (q.type === "multiple" && q.options?.length) {
      // radio buttons (single choice)
      q.options.forEach(opt => {
        const optDiv = document.createElement("div");
        optDiv.className = "option";
        optDiv.innerHTML = `
          <label>
            <input type="radio" name="q_${q.id}" value="${escapeHtml(opt)}">
            ${escapeHtml(opt)}
          </label>
        `;
        qDiv.appendChild(optDiv);
      });
    } else if (q.type === "checkbox" && q.options?.length) {
      // checkboxes (multi-select)
      q.options.forEach((opt, idx) => {
        const optDiv = document.createElement("div");
        optDiv.className = "option";
        // include index to allow multiple checkboxes with same name
        optDiv.innerHTML = `
          <label>
            <input type="checkbox" name="q_${q.id}" value="${escapeHtml(opt)}">
            ${escapeHtml(opt)}
          </label>
        `;
        qDiv.appendChild(optDiv);
      });
    } else {
      // default text input
      const input = document.createElement("input");
      input.type = "text";
      input.name = `q_${q.id}`;
      qDiv.appendChild(input);
    }

    form.appendChild(qDiv);
  });

  // show back button and submit behaviour
  const backBtn = document.getElementById("backBtn");
  backBtn.style.display = "inline-block";
  backBtn.onclick = () => {
    details.style.display = "none";
    document.getElementById("surveyList").style.display = "";
    document.getElementById("title").textContent = "";
    form.innerHTML = "";
  };

  document.getElementById("submitBtn").onclick = async () => {
    const responses = survey.questions.map(q => {
      if (q.type === "multiple") {
        const checked = form.querySelector(`input[name="q_${q.id}"]:checked`);
        return { question_id: q.id, answer: checked ? checked.value : "" };
      } else if (q.type === "checkbox") {
        const checkedBoxes = form.querySelectorAll(`input[name="q_${q.id}"]:checked`);
        const values = Array.from(checkedBoxes).map(cb => cb.value);
        return { question_id: q.id, answer: values };
      } else {
        const field = form.querySelector(`[name="q_${q.id}"]`);
        return { question_id: q.id, answer: field ? field.value : "" };
      }
    });

    try {
      await apiPost(`/surveys/${survey.id}/responses`, {
        respondent: "anonymous",
        answers: responses
      });
      alert("Response submitted!");
      // reset to list view
      backBtn.click();
    } catch (err) {
      alert("Failed to submit response.");
    }
  };
}

// small helper to avoid HTML injection from options
function escapeHtml(s) {
  if (typeof s !== "string") return s;
  return s.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}

document.addEventListener("DOMContentLoaded", loadSurveys);
