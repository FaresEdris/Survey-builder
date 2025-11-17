const form = document.getElementById("surveyForm");
const draftBtn = document.getElementById("draftBtn");
const submitBtn = document.getElementById("submitBtn");
const backBtn = document.getElementById("backBtn");
const resetBtn = document.getElementById("resetBtn");

// Load draft if exists
window.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("drafts");
    if (!saved) return;

    const drafts = JSON.parse(saved);
    const draft = drafts[survey.id];
    if (!draft) return;

    for (const r of draft.responses) {
        const qid = r.question_id;
        const value = r.answer;

        const el = form.querySelector(`[name="q_${qid}"]`);
        if (!el) continue;

        if (el.type === "radio") {
            const radio = form.querySelector(`[name="q_${qid}"][value="${value}"]`);
            if (radio) radio.checked = true;
        } else if (el.type === "checkbox") {
            value.forEach(v => {
                const cb = form.querySelector(`[name="q_${qid}"][value="${v}"]`);
                if (cb) cb.checked = true;
            });
        } else if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
            el.value = value;
        }
    }
});

// Save draft
draftBtn.onclick = () => {
    const saved = localStorage.getItem("drafts");
    const drafts = saved ? JSON.parse(saved) : {};
    const responses = readResponse(survey);
    drafts[survey.id] = {
        surveyTitle: survey.title,
        responses: responses,
        savedAt: new Date().toISOString()
    };
    localStorage.setItem("drafts", JSON.stringify(drafts));
};

// Reset form
resetBtn.onclick = () => {
    clearDraft();
    form.reset();
}

// Submit response
submitBtn.onclick = async (e) => {
    e.preventDefault();
    const responses = readResponse(survey);
    const payload = {
        respondent: "anonymous",
        answers: responses
    };

    try {
        const res = await fetch(`/api/surveys/${survey.id}/responses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Network response was not ok');
        clearDraft();
        //alert("Response submitted successfully!");
        backBtn.click();

    } catch (err) {
        console.error(err);
        //alert("Failed to submit response.");
    }
};

function readResponse(survey) {
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
    return responses;
}
// there is something wrong with if sata
function clearDraft() {
    const saved = localStorage.getItem("drafts");
    savedDrafts = JSON.parse(saved);
    savedDraft = savedDrafts ? savedDrafts[survey.id] : null;
    if (savedDraft == null) return 
        //alert("No drafts to clear.");
    const drafts = JSON.parse(saved);
    delete drafts[survey.id];
    localStorage.setItem("drafts", JSON.stringify(drafts));
    //alert(`Draft for "${survey.title}" cleared!`);
}

