const form = document.getElementById("surveyForm");
const draftBtn = document.getElementById("draftBtn");
const submitBtn = document.getElementById("submitBtn");
const backBtn = document.getElementById("backBtn");
const resetBtn = document.getElementById("resetBtn");
const errorBox = document.getElementById("errorContainer");

/* -------------------------------
   LOAD DRAFT IF EXISTS
-------------------------------- */
window.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("drafts");
    if (!saved) return;

    const drafts = JSON.parse(saved);
    const draft = drafts[survey.id];
    if (!draft) return;

    for (const r of draft.responses) {
        const qid = r.question_id;
        const value = r.answer;

        const field = form.querySelector(`[name="q_${qid}"]`);
        if (!field) continue;

        if (Array.isArray(value)) {
            value.forEach(v => {
                const cb = form.querySelector(`[name="q_${qid}"][value="${v}"]`);
                if (cb) cb.checked = true;
            });
        } else {
            const el = form.querySelector(`[name="q_${qid}"][value="${value}"]`);
            if (el) el.checked = true;
            else if (field.tagName === "TEXTAREA") field.value = value;
        }
    }
});

/* -------------------------------
   SAVE DRAFT
-------------------------------- */
draftBtn.onclick = () => {
    const saved = localStorage.getItem("drafts");
    const drafts = saved ? JSON.parse(saved) : {};

    drafts[survey.id] = {
        surveyTitle: survey.title,
        responses: readResponse(survey),
        savedAt: new Date().toISOString(),
    };

    localStorage.setItem("drafts", JSON.stringify(drafts));
};

/* -------------------------------
   RESET FORM
-------------------------------- */
resetBtn.onclick = () => {
    clearDraft();
    form.reset();
};

/* -------------------------------
   VALIDATE BEFORE SUBMITTING
-------------------------------- */
submitBtn.onclick = async (e) => {
    e.preventDefault();
    clearErrors();

    if (!validateRequired()) {
        return;
    }

    const payload = {
        respondent: "anonymous",
        answers: readResponse(survey),
    };

    try {
        const res = await fetch(`/api/surveys/${survey.id}/responses`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!res.ok) throw new Error("Network error");

        clearDraft();
        backBtn.click();

    } catch (err) {
        showError("Failed to submit response.");
        console.error(err);
    }
};

/* -------------------------------
   VALIDATE REQUIRED QUESTIONS
-------------------------------- */
function validateRequired() {
    let valid = true;

    survey.questions.forEach(q => {
        if (!q.required) return;

        const block = form.querySelector(`[data-qid="${q.id}"]`);
        const name = `q_${q.id}`;
        const inputs = form.querySelectorAll(`[name="${name}"]`);

        let answered = false;

        if (q.type === "text") {
            answered = inputs[0].value.trim().length > 0;
        }
        else if (q.type === "multiple") {
            answered = Array.from(inputs).some(i => i.checked);
        }
        else if (q.type === "checkbox") {
            answered = Array.from(inputs).some(i => i.checked);
        }

        if (!answered) {
            block.classList.add("is-invalid");
            block.querySelector(".invalid-feedback").style.display = "block";
            valid = false;
        } else {
            block.classList.remove("is-invalid");
        }
    });

    if (!valid) {
        showError("Please fill in all required questions.");
    }

    return valid;
}

/* ------------------------------- */
function showError(msg) {
    errorBox.innerHTML = `
        <div class="alert alert-danger">${msg}</div>
    `;
}

function clearErrors() {
    errorBox.innerHTML = "";
    document.querySelectorAll(".invalid-feedback").forEach(el => el.style.display = "none");
}

/* -------------------------------
   READ RESPONSE
-------------------------------- */
function readResponse(survey) {
    return survey.questions.map(q => {
        if (q.type === "multiple") {
            const checked = form.querySelector(`input[name="q_${q.id}"]:checked`);
            return { question_id: q.id, answer: checked ? checked.value : "" };
        }

        if (q.type === "checkbox") {
            const checkedBoxes = form.querySelectorAll(`input[name="q_${q.id}"]:checked`);
            return { question_id: q.id, answer: Array.from(checkedBoxes).map(cb => cb.value) };
        }

        const field = form.querySelector(`[name="q_${q.id}"]`);
        return { question_id: q.id, answer: field.value.trim() };
    });
}

/* -------------------------------
   CLEAR DRAFT
-------------------------------- */
function clearDraft() {
    const saved = localStorage.getItem("drafts");
    if (!saved) return;

    const drafts = JSON.parse(saved);
    delete drafts[survey.id];
    localStorage.setItem("drafts", JSON.stringify(drafts));
}
