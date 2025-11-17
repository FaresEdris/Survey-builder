const questionsContainer = document.getElementById('questions');
const questionTypes = ['text', 'multiple', 'checkbox'];
let questionCounter = 0;

// Render existing questions
surveyData.questions.forEach(q => addQuestionCard(q));

// Add new question
document.getElementById('addQuestionBtn').addEventListener('click', () => {
    addQuestionCard({
        id: null,         // New question, no ID yet
        text: '',
        type: 'text',
        options: [],
        deleted: false,
        required: false
    });
});

// Submit edited survey
document.getElementById('submitSurveyBtn').addEventListener('click', async () => {
    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();

/*     if (!title || !description) {
        alert('Title and description are required.');
        return;
    } */

    const questions = Array.from(document.querySelectorAll('.question')).map(q => {
        const text = q.querySelector('.question-text').value.trim();
        const type = q.querySelector('.question-type').value;
        const required = q.querySelector('.question-required').checked;
        const deleted = q.querySelector('.question-delete').checked;
        const optionsInput = q.querySelector('.question-options');
        const options = optionsInput ? optionsInput.value.split(',').map(o => o.trim()).filter(o => o) : [];
        const id = q.dataset.id ? parseInt(q.dataset.id) : null;

        return { id, text, type, required, deleted, options };
    });

    try {
        const res = await fetch(`/surveys/${surveyData.id}/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, questions })
        });
        if (!res.ok) throw new Error('Failed to update survey.');
        //alert(JSON.stringify({ title, description, questions }));
        window.location.href = `/surveys/${surveyData.id}/responses`;
    } catch (err) {
        console.error(err);
        //alert('Error saving survey.');
    }
});

// Helper to create question card
function addQuestionCard(q) {
    questionCounter++;
    const card = document.createElement('div');
    card.className = 'question';
    card.dataset.index = questionCounter;
    if (q.id) card.dataset.id = q.id;

    card.innerHTML = `
        <h4>Question ${questionCounter}</h4>

        <label>Text:</label>
        <input type="text" class="question-text" value="${q.text}" required>

        <label>Type:</label>
        <select class="question-type">
            ${questionTypes.map(t => `<option value="${t}" ${t===q.type?'selected':''}>${t}</option>`).join('')}
        </select>

        <div class="question-options-container" ${q.type==='text'?'style="display:none;"':''}>
            <label>Options (comma separated):</label>
            <input type="text" class="question-options" value="${q.options.join(', ')}">
        </div>

        <label>
            <input type="checkbox" class="question-required" ${q.required?'checked':''}>
            Required
        </label>
        <label>
            <input type="checkbox" class="question-delete" ${q.deleted?'checked':''}>
            Delete
        </label>

        <button type="button" class="remove-question-btn">Remove</button>
        <hr>
    `;

    // Toggle options visibility based on type
    const typeSelect = card.querySelector('.question-type');
    const optionsDiv = card.querySelector('.question-options-container');
    typeSelect.addEventListener('change', () => {
        if (typeSelect.value === 'text') optionsDiv.style.display = 'none';
        else optionsDiv.style.display = 'block';
    });

    // Remove question card
    card.querySelector('.remove-question-btn').addEventListener('click', () => {
        questionsContainer.removeChild(card);
    });

    questionsContainer.appendChild(card);
}
