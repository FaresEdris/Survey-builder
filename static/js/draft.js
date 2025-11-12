// draft.js

// Utility: get all drafts from localStorage
function getDraftsFromLocalStorage() {
  const drafts = localStorage.getItem("drafts");
  return drafts ? JSON.parse(drafts) : {};
}

// Display all drafts in the list
async function displayLocalStorageDrafts() {
  const drafts = getDraftsFromLocalStorage();
  const listDiv = document.getElementById("surveyList");
  listDiv.innerHTML = "<h3>Saved Drafts:</h3>";

  const ul = document.createElement("ul");
  ul.style.listStyle = "none";
  ul.style.padding = "0";

  for (const [surveyId, draft] of Object.entries(drafts)) {
    const li = document.createElement("li");
    li.style.marginBottom = "10px";

    // Survey title
    const titleSpan = document.createElement("span");
    titleSpan.textContent = draft.surveyTitle || `Survey #${surveyId}`;

    // View button
    const viewBtn = document.createElement("button");
    viewBtn.textContent = "View";
    viewBtn.className = "btn primary";
    viewBtn.style.marginLeft = "10px";
    viewBtn.onclick = async () => {
      try {
        const survey = await apiGet(`/surveys/${surveyId}`);
        showDraftSurvey(survey, draft);
      } catch (err) {
        alert("Failed to load survey.");
        console.error(err);
      }
    };

    // Remove button
    const rmBtn = document.createElement("button");
    rmBtn.textContent = "Remove";
    rmBtn.className = "btn removeBtn";
    rmBtn.style.marginLeft = "5px";
    rmBtn.onclick = () => {
      const drafts = getDraftsFromLocalStorage();
      delete drafts[surveyId];
      localStorage.setItem("drafts", JSON.stringify(drafts));
      li.remove();
      document.getElementById("surveyDetail").innerHTML = ""; // clear detail
    };

    li.appendChild(titleSpan);
    li.appendChild(viewBtn);
    li.appendChild(rmBtn);
    ul.appendChild(li);
  }

  listDiv.appendChild(ul);
}

function showDraftSurvey(survey, draft) {
  const container = document.getElementById("surveyDetail");
  const listDiv = document.getElementById("surveyList");

  // Hide the drafts list
  listDiv.style.display = "none";
  container.innerHTML = ""; // clear previous content

  // Back button
  const backBtn = document.createElement("button");
  backBtn.textContent = "← Back to Drafts";
  backBtn.className = "btn";
  backBtn.style.marginBottom = "20px";
  backBtn.onclick = () => {
    container.innerHTML = "";
    listDiv.style.display = "block";
  };
  container.appendChild(backBtn);

  // Survey title
  const titleEl = document.createElement("h2");
  titleEl.textContent = survey.title;
  container.appendChild(titleEl);

  const form = document.createElement("form");

  survey.questions.forEach(q => {
    const div = document.createElement("div");
    div.innerHTML = `<p>${q.text}</p>`;

    const saved = draft.responses.find(r => r.question_id === q.id);

    if (q.type === "multiple") {
      q.options.forEach(opt => {
        const input = document.createElement("input");
        input.type = "radio";
        input.name = `q_${q.id}`;
        input.value = opt;
        if (saved && saved.answer === opt) input.checked = true;
        div.appendChild(input);
        div.appendChild(document.createTextNode(opt));
      });
    } else if (q.type === "checkbox") {
      q.options.forEach(opt => {
        const input = document.createElement("input");
        input.type = "checkbox";
        input.name = `q_${q.id}`;
        input.value = opt;
        if (saved && saved.answer.includes(opt)) input.checked = true;
        div.appendChild(input);
        div.appendChild(document.createTextNode(opt));
      });
    } else {
      const input = document.createElement("input");
      input.type = "text";
      input.name = `q_${q.id}`;
      if (saved) input.value = saved.answer;
      div.appendChild(input);
    }

    form.appendChild(div);
  });

  container.appendChild(form);

  // Submit button
  const submitBtn = document.createElement("button");
  submitBtn.textContent = "Submit Survey";
  submitBtn.className = "btn primary";
  submitBtn.style.marginTop = "15px";
  submitBtn.onclick = async (e) => {
    e.preventDefault();

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

      // Remove draft after submission
      const drafts = JSON.parse(localStorage.getItem("drafts") || "{}");
      delete drafts[survey.id];
      localStorage.setItem("drafts", JSON.stringify(drafts));

      alert("Survey submitted successfully!");
      container.innerHTML = "";
      listDiv.style.display = "block";
      displayLocalStorageDrafts(); // refresh the draft list
    } catch (err) {
      console.error(err);
      alert("Failed to submit survey.");
    }
  };

  container.appendChild(submitBtn);
}


// Initialize page
document.addEventListener("DOMContentLoaded", displayLocalStorageDrafts);
