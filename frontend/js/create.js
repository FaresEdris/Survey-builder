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
  // Validation currently handled in backend
  /* if(!title && !description) {
    alert("Title and Description are required.");
    return;
  }
  if (!title) {
    alert("Title is required.");
    return;
  }
  if(!description) {
    alert("Description is required.");
    return;
  } */
  const questionElements = document.querySelectorAll(".question");
  const questionData = Array.from(questionElements).map(q => {
    const text = q.querySelector(".q-text").value;
    const type = q.querySelector(".q-type").value;
    const optionsField = q.querySelector(".q-options");
    const options = optionsField && type === "multiple"
      ? optionsField.value.split(",").map(o => o.trim()).filter(o => o)
      : [];
    if (!text) {
      alert("Question name cannot be empty.");
      error("Question name is required");
      return;
    }
    if(type === "multiple" && options.length === 0) {
      alert("Multiple choice questions must have at least one option.");
      error("Invalid question options");
    }
    if(type === "multiple" && options.length < 2) {
      alert("Multiple choice questions must have at least two options.");
      error("At least two options required");
    }
    return { text, type, options };
  });

  const newSurvey = {
    title,
    description,
    questions: questionData
  };

  try {
    await apiPost("/surveys", newSurvey);
    alert("Survey created successfully!");}
  catch(err){
    alert(`Error creating survey: ${err.message}`);
    return;
  }
  window.location.href = "surveys.html";
};
