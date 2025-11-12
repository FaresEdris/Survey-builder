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
    const btn = document.createElement("button");
    btn.textContent = s.title;
    btn.className = "link-like";
    btn.addEventListener("click", () => showSurveyDetail(s.id));

    li.appendChild(btn);
    list.appendChild(li);
  });
}

async function showSurveyDetail(id) {
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

  document.getElementById("title").textContent = survey.title;
  const form = document.getElementById("responseForm");
  form.innerHTML = "";

  survey.questions.forEach(q => {
    const qDiv = document.createElement("div");
    qDiv.className = "question";
    const label = document.createElement("p");
    label.textContent = q.text;
    qDiv.appendChild(label);
    if (q.type === "multiple" && q.options?.length) {
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
      // checkboxes right now not supported, adding checkboxes future task
      q.options.forEach((opt, idx) => {
        const optDiv = document.createElement("div");
        optDiv.className = "option";
        optDiv.innerHTML = `
          <label>
            <input type="checkbox" name="q_${q.id}" value="${escapeHtml(opt)}">
            ${escapeHtml(opt)}
          </label>
        `;
        qDiv.appendChild(optDiv);
      });
    } else {
      const input = document.createElement("input");
      input.type = "text";
      input.name = `q_${q.id}`;
      qDiv.appendChild(input);
    }

    form.appendChild(qDiv);
  });

  // show back button 
  const backBtn = document.getElementById("backBtn");
  backBtn.style.display = "inline-block";
  backBtn.onclick = () => {
    details.style.display = "none";
    document.getElementById("surveyList").style.display = "";
    document.getElementById("title").textContent = "";
    form.innerHTML = "";
  };
  
  // Draft button
  const draftBtn = document.getElementById("draftBtn");
draftBtn.style.display = "inline-block";

draftBtn.onclick = () => {
  // Load the saved drafts object from localStorage
  const saved = localStorage.getItem("drafts");
  const drafts = saved ? JSON.parse(saved) : {};

  // Collect current answers from the form
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

  // Save this survey’s draft under its ID
  drafts[survey.id] = {
    surveyTitle: survey.title,
    responses: responses,
    savedAt: new Date().toISOString()
  };

  // Persist updated object
  localStorage.setItem("drafts", JSON.stringify(drafts));
  alert(`Draft for "${survey.title}" saved!`);
};

  // submit behaviour
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
