console.log("Create Survey JS loaded!");
document.addEventListener("DOMContentLoaded", () => {
  const questionsDiv = document.getElementById("questions");
  const addQuestionBtn = document.getElementById("addQuestionBtn");
  const submitSurveyBtn = document.getElementById("submitSurveyBtn");

  let questionCount = 0;



  // Add question
  addQuestionBtn.addEventListener("click", () => {
    const qDiv = document.createElement("div");
    qDiv.className = "question";

    const qIndex = questionCount++;
    qDiv.innerHTML = `
      <h4>Question ${qIndex + 1}</h4>
      <input type="text" class="q-text" placeholder="Enter question text" required>

      <label>Type:</label>
      <select class="q-type">
        <option value="text">Text</option>
        <option value="multiple">Multiple Choice</option>
      </select>

      <div class="options" style="display:none;">
        <p>Options (comma-separated):</p>
        <input type="text" class="q-options" placeholder="Option1, Option2, Option3">
      </div>
      <button type="button" class="remove-question-btn">Remove Question</button>
      <hr>
    `;

    // Toggle options field
    const typeSelect = qDiv.querySelector(".q-type");
    const optionsDiv = qDiv.querySelector(".options");
    typeSelect.addEventListener("change", () => {
      optionsDiv.style.display = typeSelect.value === "multiple" ? "block" : "none";
    });

    // Remove question button
    qDiv.querySelector(".remove-question-btn").addEventListener("click", () => {
      questionsDiv.removeChild(qDiv);
    });

    questionsDiv.appendChild(qDiv);
  });

  // Submit survey
  submitSurveyBtn.addEventListener("click", async () => {
    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();

    /* if (!title || !description) {
      alert("Title and description are required.");
      return;
    } */

    const questionElements = document.querySelectorAll(".question");
    const questions = Array.from(questionElements).map(q => {
      const text = q.querySelector(".q-text").value.trim();
      const type = q.querySelector(".q-type").value;
      const optionsField = q.querySelector(".q-options");
      const options =
        optionsField && type === "multiple"
          ? optionsField.value.split(",").map(o => o.trim()).filter(o => o)
          : [];

      if (!text) {
        alert("Question text cannot be empty.");
        throw new Error("Empty question text");
      }

      if (type === "multiple" && options.length < 2) {
        alert("Multiple choice questions must have at least two options.");
        throw new Error("Not enough options");
      }

      return { text, type, options };
    });

    const newSurvey = { title, description, questions };

    try {
      const response = await fetch("/api/surveys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSurvey)
      });

      if (!response.ok) throw new Error("Failed to create survey");

      alert("Survey created successfully!");
      window.location.href = "/surveys/view";
    } catch (err) {
      console.error(err);
      alert("Error creating survey.");
    }
  });
});
