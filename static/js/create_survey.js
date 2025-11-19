const questionTypes = ['text', 'multiple', 'checkbox'];
let questionCounter = 0;
const questionsContainer = document.getElementById('questionsContainer');
const addQuestionBtn = document.getElementById('addQuestionBtn');

let questionCount = 0;

addQuestionBtn.addEventListener('click', () => {
    questionCount++;
    const questionDiv = document.createElement('div');
    questionDiv.classList.add('card', 'mb-3', 'p-3', 'question-item', 'shadow-sm');
    questionDiv.setAttribute('data-id', questionCount);

    questionDiv.innerHTML = `
        <div class="mb-2 d-flex justify-content-between align-items-center">
            <h5>Question ${questionCount}</h5>
            <button type="button" class="btn btn-sm btn-danger remove-question-btn">Remove</button>
        </div>
        <div class="mb-2">
            <label class="form-label">Question Text</label>
            <input type="text" class="form-control question-text" required>
            <div class="invalid-feedback">Question text is required.</div>
        </div>
        <div class="mb-2">
            <label class="form-label">Type</label>
            <select class="form-select question-type">
                <option value="text">Text</option>
                <option value="multiple">Multiple Choice</option>
                <option value="checkbox">Checkbox</option>
            </select>
        </div>
        <div class="mb-2 question-options d-none">
            <label class="form-label">Options (comma separated)</label>
            <input type="text" class="form-control question-options-input">
            <div class="invalid-feedback">At least 2 options are required.</div>
        </div>
        <div class="form-check">
            <input class="form-check-input question-required" type="checkbox">
            <label class="form-check-label">Required</label>
        </div>
    `;

    questionsContainer.appendChild(questionDiv);

    // Show/hide options based on type
    const typeSelect = questionDiv.querySelector('.question-type');
    const optionsDiv = questionDiv.querySelector('.question-options');
    typeSelect.addEventListener('change', () => {
        if (typeSelect.value === 'multiple' || typeSelect.value === 'checkbox') {
            optionsDiv.classList.remove('d-none');
            optionsDiv.querySelector('input').required = true;
        } else {
            optionsDiv.classList.add('d-none');
            optionsDiv.querySelector('input').required = false;
        }
    });

    // Remove question
    questionDiv.querySelector('.remove-question-btn').addEventListener('click', () => {
        questionDiv.remove();
    });
});

// Form submit handler
const form = document.getElementById('createSurveyForm');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    // show bootstrap validation styles
    form.classList.add('was-validated');

    // If native validation fails, stop and show browser/Bootstrap feedback
    if (!form.checkValidity()) {
        const firstInvalid = form.querySelector(':invalid');
        if (firstInvalid) firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }

    // Gather values
    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();
    let hasError = false;
    if (!title || title.length === 0) {
        document.getElementById('title').classList.add('is-invalid');
        hasError = true;
    }
    if (!description || description.length === 0) {
        document.getElementById('description').classList.add('is-invalid');
        hasError = true;
    }
    const questionsArr = Array.from(document.querySelectorAll('.question-item'));
    
    const questions = questionsArr.map(q => {
        const textInput = q.querySelector('.question-text');
        const text = textInput.value.trim();
        const type = q.querySelector('.question-type').value;
        const required = q.querySelector('.question-required').checked;
        const optionsInput = q.querySelector('.question-options-input');
        const options = optionsInput ? optionsInput.value.split(',').map(o => o.trim()).filter(o => o) : [];

        // Reset error styles
        textInput.classList.remove('is-invalid');
        if (optionsInput) optionsInput.classList.remove('is-invalid');

        // Validation for dynamic question fields
        if (!text || text.length === 0) {
            textInput.classList.add('is-invalid');
            hasError = true;
        }

        if ((type === 'multiple' || type === 'checkbox') && options.length < 2) {
            optionsInput.classList.add('is-invalid');
            hasError = true;
        }

        return { text, type, required, options };
    });

    if (hasError) {
        document.querySelector('.is-invalid')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }

    try {
        const res = await fetch('/api/surveys', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, questions })
        });
        if (!res.ok) throw new Error('Failed to create survey.');
        window.location.href = '/surveys/view';
    } catch (err) {
        console.error(err);
        alert('Error creating survey.');
    }
});

