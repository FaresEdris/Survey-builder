const questionsDiv = document.getElementById("questions");
const addQuestionBtn = document.getElementById("addQuestionBtn");
const submitSurveyBtn = document.getElementById("submitSurveyBtn");

let questions = [];

addQuestionBtn.onclick = () => {
  const qDiv = document.createElement("div");
  qDiv.className = "question";

  const qIndex = questions.length;

  qDiv.innerHTML = `
    <h4>Question ${qIndex + 1}</h4>
    <input type="text" class="q-text" placeholder="Enter question text">

    <label>Type:</label>
    <select class="q-type">
      <option value="text">Text</option>
      <option value="multiple">Multiple Choice</option>
    </select>

    <div class="options" style="display:none;">
      <p>Options (comma-separated):</p>
      <input type="text" class="q-options" placeholder="Option1, Option2, Option3">
    </div>
  `;

  // Toggle options field based on type
  const typeSelect = qDiv.querySelector(".q-type");
  const optionsDiv = qDiv.querySelector(".options");
  typeSelect.addEventListener("change", () => {
    optionsDiv.style.display = typeSelect.value === "multiple" ? "block" : "none";
  });

  questionsDiv.appendChild(qDiv);
};

submitSurveyBtn.onclick = async () => {
  const title = document.getElementById("title").value;
  const description = document.getElementById("description").value;

  const questionElements = document.querySelectorAll(".question");
  const questionData = Array.from(questionElements).map(q => {
    const text = q.querySelector(".q-text").value;
    const type = q.querySelector(".q-type").value;
    const optionsField = q.querySelector(".q-options");
    const options = optionsField && type === "multiple"
      ? optionsField.value.split(",").map(o => o.trim()).filter(o => o)
      : [];

    return { text, type, options };
  });

  const newSurvey = {
    title,
    description,
    questions: questionData
  };

  await apiPost("/surveys", newSurvey);
  alert("Survey created successfully!");
  window.location.href = "surveys.html";
};
