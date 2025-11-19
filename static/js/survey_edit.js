const questionsContainer = document.getElementById('questions');
const questionTypes = ['text', 'multiple', 'checkbox'];
let questionCounter = 0;

// Render existing questions
surveyData.questions.forEach(q => addQuestionCard(q, true));

// Add new question
document.getElementById('addQuestionBtn').addEventListener('click', () => {
    addQuestionCard({
        id: null,
        text: '',
        type: 'text',
        options: [],
        required: false,
        deleted: false
    }, false);
});

// Save edited survey
document.getElementById('submitSurveyBtn').addEventListener('click', async () => {

    clearFieldErrors();

    const title = document.getElementById('title');
    const description = document.getElementById('description');

    let hasError = false;

    if (!title.value.trim()) {
        markInvalid(title);
        showError("Title is required");
        hasError = true;
    }
    if (!description.value.trim()) {
        markInvalid(description);
        showError("Description is required");
        hasError = true;
    }

    const questions = Array.from(document.querySelectorAll('.question')).map((q, index) => {
        const textInput = q.querySelector('.question-text');
        const typeSelect = q.querySelector('.question-type');
        let required = q.querySelector('.question-required').checked;

        const optionsInput = q.querySelector('.question-options');
        const options = optionsInput
            ? optionsInput.value.split(',').map(o => o.trim()).filter(o => o)
            : [];

        const id = q.dataset.id ? parseInt(q.dataset.id) : null;
        const deleted = q.dataset.deleted === "true";
        if (deleted) {
            required = false;
            q.querySelector('.question-required').checked = false;

        }

        const text = textInput.value.trim();
        const type = typeSelect.value;

        // TEXT VALIDATION
        if (!deleted && (!text || text.length === 0)) {
            markInvalid(textInput);
            showError(`Question ${index + 1}: Text is required`);
            hasError = true;
        }

        // OPTION VALIDATION
        if (!deleted && (type === 'multiple' || type === 'checkbox') && options.length < 2) {
            markInvalid(optionsInput);
            showError(`Question ${index + 1}: At least 2 options required`);
            hasError = true;
        }

        return { id, text, type, required, deleted, options };
    });
    if (questions.length === 0 || questions.every(q => q.deleted)) {
        showError("At least one non-deleted question is required");
        hasError = true;
    }
    if (hasError) return;

    try {
        const res = await fetch(`/surveys/${surveyData.id}/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                title: title.value.trim(), 
                description: description.value.trim(), 
                questions 
            })
        });
        if (!res.ok) throw new Error('Failed to update survey');
        window.location.href = `/control`;
    } catch (err) {
        console.error(err);
    }
});


// --- UI Helpers ---
function showError(msg) {
    const alertBox = document.createElement("div");
    alertBox.className = "alert alert-danger";
    alertBox.textContent = msg;
    document.querySelector(".container").prepend(alertBox);
    setTimeout(() => alertBox.remove(), 3000);
}

function markInvalid(input) {
    input.classList.add("is-invalid");
}

function clearFieldErrors() {
    document.querySelectorAll(".is-invalid").forEach(el => el.classList.remove("is-invalid"));
}

// ADD QUESTION CARD
function addQuestionCard(q, isOld) {
    questionCounter++;

    const card = document.createElement('div');
    card.className = 'question card p-3 mb-3 shadow-sm';
    card.dataset.index = questionCounter;
    if (isOld && q.id != null) card.dataset.id = q.id;
    card.dataset.deleted = q.deleted ? "true" : "false";

    card.innerHTML = `
        <h4 class="mb-3">Question ${questionCounter}</h4>

        <div class="mb-3">
            <label class="form-label">Text</label>
            <input type="text" class="form-control question-text" value="${q.text}">
        </div>

        <div class="mb-3">
            <label class="form-label">Type</label>
            <select class="form-select question-type">
                ${questionTypes.map(t => `<option value="${t}" ${t === q.type ? 'selected' : ''}>${t}</option>`).join('')}
            </select>
        </div>

        <div class="mb-3 question-options-container" ${q.type === 'text' ? 'style="display:none;"' : ''}>
            <label class="form-label">Options (comma separated)</label>
            <input type="text" class="form-control question-options" value="${(q.options || []).join(', ')}">
        </div>

        <div class="form-check mb-2 d-inline-block me-3">
            <input type="checkbox" class="form-check-input question-required" ${q.required ? 'checked' : ''} id="req-${questionCounter}">
            <label class="form-check-label" for="req-${questionCounter}">Required</label>
        </div>

        ${isOld ? `
        <div class="form-check mb-2 d-inline-block">
            <input type="checkbox" class="form-check-input question-deleted" ${q.deleted ? 'checked' : ''} id="del-${questionCounter}">
            <label class="form-check-label text-danger" for="del-${questionCounter}">Deleted</label>
        </div>
        ` : `
        <button type="button" class="btn btn-danger btn-sm remove-question-btn">Remove</button>
        `}
    `;

    // Show/Hide options input
    const typeSelect = card.querySelector('.question-type');
    const optionsDiv = card.querySelector('.question-options-container');
    typeSelect.addEventListener('change', () => {
        if (typeSelect.value === 'text') optionsDiv.style.display = 'none';
        else optionsDiv.style.display = 'block';
    });

    if (isOld) {
        const deletedCheckbox = card.querySelector('.question-deleted');
        const requiredCheckbox = card.querySelector('.question-required');
        
        deletedCheckbox.addEventListener('change', () => {
            card.dataset.deleted = deletedCheckbox.checked ? "true" : "false";
            
            if (deletedCheckbox.checked) {
                // When deleted: uncheck and disable required
                requiredCheckbox.checked = false;
                requiredCheckbox.disabled = true;
                card.classList.add('opacity-50');
            } else {
                // When restored: re-enable required
                requiredCheckbox.disabled = false;
                card.classList.remove('opacity-50');
            }
        });
        
        // apply initial visual state
        if (card.dataset.deleted === "true") {
            requiredCheckbox.checked = false;
            requiredCheckbox.disabled = true;
            card.classList.add('opacity-50');
        }
    } else {
        // NEW QUESTION → remove immediately
        const removeBtn = card.querySelector('.remove-question-btn');
        removeBtn.addEventListener('click', () => {
            questionsContainer.removeChild(card);
        });
    }

    questionsContainer.appendChild(card);
}
