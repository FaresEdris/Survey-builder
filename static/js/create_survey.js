const questionTypes = ['text', 'multiple', 'checkbox'];
let questionCounter = 0;
const questionsContainer = document.getElementById('questions');

document.getElementById('addQuestionBtn').addEventListener('click', () => {
    questionCounter++;
    const questionCard = document.createElement('div');
    questionCard.className = 'question';
    questionCard.dataset.index = questionCounter;

    questionCard.innerHTML = `
        <h4>Question ${questionCounter}</h4>
        <label>Text:</label>
        <input type="text" class="question-text" required>

        <label>Type:</label>
        <select class="question-type">
            ${questionTypes.map(t => `<option value="${t}">${t}</option>`).join('')}
        </select>

        <div class="question-options-container" style="display:none;">
            <label>Options (comma separated):</label>
            <input type="text" class="question-options">
        </div>

        <label>
            <input type="checkbox" class="question-required"> Required
        </label>

        <button type="button" class="remove-question-btn">Remove</button>
        <hr>
    `;

    questionsContainer.appendChild(questionCard);

    const typeSelect = questionCard.querySelector('.question-type');
    const optionsDiv = questionCard.querySelector('.question-options-container');
    typeSelect.addEventListener('change', () => {
        if (typeSelect.value === 'text') {
            optionsDiv.style.display = 'none';
        } else {
            optionsDiv.style.display = 'block';
        }
    });

    questionCard.querySelector('.remove-question-btn').addEventListener('click', () => {
        questionsContainer.removeChild(questionCard);
    });
});

// Submit survey
document.getElementById('submitSurveyBtn').addEventListener('click', async () => {
    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();

   /*  if (!title || !description) {
        alert('Title and description are required.');
        return;
    } */

    const questions = Array.from(document.querySelectorAll('.question')).map(q => {
        const text = q.querySelector('.question-text').value.trim();
        const type = q.querySelector('.question-type').value;
        const required = q.querySelector('.question-required').checked;
        const optionsInput = q.querySelector('.question-options');
        const options = optionsInput ? optionsInput.value.split(',').map(o => o.trim()).filter(o => o) : [];

        return { text, type, required, options };
    });

    /* if (questions.length === 0) {
        alert('Add at least one question.');
        return;
    } */

    try {
        const res = await fetch('/api/surveys', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, questions })
        });
        if (!res.ok) throw new Error('Failed to create survey.');
        //alert('Survey created successfully!');
        window.location.href = '/surveys/view';
    } catch (err) {
        console.error(err);
        //alert('Error creating survey.');
    }
});

