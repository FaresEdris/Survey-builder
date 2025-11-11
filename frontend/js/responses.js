async function loadSurveys() {
    const surveys = await apiGet("/surveys");
    const listDiv = document.getElementById("surveyList");
  
    listDiv.innerHTML = "<h3>Choose a survey to view responses:</h3>";
    const ul = document.createElement("ul");
    ul.style.listStyle = "none";
    ul.style.padding = "0";
  
    surveys.forEach(s => {
      const li = document.createElement("li");
      li.style.marginBottom = "10px";
      li.innerHTML = `<button class="btn" onclick="loadResponses(${s.id})">${s.title}</button>`;
      ul.appendChild(li);
    });
  
    listDiv.appendChild(ul);
  }
  
  async function loadResponses(surveyId) {
    const detailsDiv = document.getElementById("responseDetails");
    detailsDiv.style.display = "block";
    detailsDiv.innerHTML = "<p>Loading responses...</p>";
  
    try {
      const responses = await apiGet(`/surveys/${surveyId}/responses`);
      if (!responses || responses.length === 0) {
        detailsDiv.innerHTML = `<p>No responses yet for survey ID ${surveyId}.</p>`;
        return;
      }
  
      let html = `<h3>Responses for Survey ID: ${surveyId}</h3>`;
  
      responses.forEach((r, idx) => {
        html += `<div class="question">
                   <h4>Respondent #${idx + 1} (${r.respondent})</h4>`;
        r.answers.forEach(a => {
          html += `<p><b>Q${a.question_id}:</b> ${a.answer}</p>`;
        });
        html += `</div>`;
      });
  
      detailsDiv.innerHTML = html;
    } catch (e) {
      detailsDiv.innerHTML = `<p style="color:red;">Error loading responses.</p>`;
      console.error(e);
    }
  }
  
  
  document.addEventListener("DOMContentLoaded", loadSurveys);
  