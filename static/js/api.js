const BASE_URL = "http://127.0.0.1:5000";

async function apiGet(path) {
    const res = await fetch(`${BASE_URL}${path}`);
    return await res.json();
}

async function apiPost(path, body) {
    const res = await fetch(`${BASE_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });
    const data = await res.json();
    // Handle errors from backend
    if (!res.ok) {
        throw new Error(data.error || "request failed");
    }
    return data;
}
async function apiDelete(path) {
    const res = await fetch(`${BASE_URL}${path}`, { method: "DELETE" });
    return await res.json();
}
    