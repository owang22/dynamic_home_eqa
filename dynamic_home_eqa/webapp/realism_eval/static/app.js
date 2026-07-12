// app.js — realism eval frontend. Adapted from the reference time-series
// QA webapp's own flow (start -> loadApp -> showItem -> saveAndNext ->
// celebration), retargeted to a single 2x2-image item instead of a
// time-series plot.

let participantId = null;
let items = [];
let responses = {};   // item_id -> saved response
let currentIndex = 0;
let itemStartTime = null;

function start() {
  const name = document.getElementById("name-input").value.trim();
  if (!name) { alert("Enter your first name."); return; }
  fetch("/api/start", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  })
    .then(r => r.json())
    .then(data => { participantId = data.participant_id; loadApp(); });
}

function loadApp() {
  Promise.all([
    fetch(`/api/items/${participantId}`).then(r => r.json()),
    fetch(`/api/progress/${participantId}`).then(r => r.json()),
  ]).then(([itemData, progressData]) => {
    items = itemData.items;
    responses = progressData;
    if (!items.length) { alert("No items available — has the render job been run?"); return; }
    document.getElementById("start-screen").style.display = "none";
    document.getElementById("eval-screen").style.display = "block";
    populateQuestionJumpMenu();
    currentIndex = items.findIndex(it => !(it.item_id in responses));
    if (currentIndex === -1) currentIndex = 0;
    showItem();
  });
}

function showItem() {
  const item = items[currentIndex];
  itemStartTime = Date.now();

  document.getElementById("item-image").src = item.png_url;
  document.getElementById("caption-box").innerHTML =
    `<b>${item.label}</b> (${item.category}, ${item.change_type})  &middot;  ${item.t_clock}<br>` +
    `${item.from ?? "(new)"} &rarr; ${item.to}  &middot;  mover: ${item.mover ?? "n/a"}<br>` +
    `reason: ${item.reason ?? ""}`;

  clearRadios("placement"); clearRadios("behavior"); clearRadios("visibility");
  clearCheckboxes("issue");
  document.getElementById("comment").value = "";

  applyStateItemNA(item);

  const saved = responses[item.item_id];
  if (saved) {
    setRadio("placement", saved.placement);
    setRadio("behavior", saved.behavior);
    setRadio("visibility", saved.visibility);
    (saved.issues || []).forEach(v => setCheckbox("issue", v));
    document.getElementById("comment").value = saved.comment || "";
  }

  document.getElementById("progress-line").textContent =
    `Item ${currentIndex + 1} / ${items.length}  &middot;  ${Object.keys(responses).length} answered`
      .replace("&middot;", "·");
  document.getElementById("question-jump").value = String(currentIndex);
  updateDebugBox();
}

function clearRadios(name) {
  document.querySelectorAll(`input[name='${name}']`).forEach(el => { el.checked = false; });
}
function clearCheckboxes(name) {
  document.querySelectorAll(`input[name='${name}']`).forEach(el => { el.checked = false; });
}
function setRadio(name, value) {
  const el = document.querySelector(`input[name='${name}'][value='${value}']`);
  if (el) el.checked = true;
}
function setCheckbox(name, value) {
  const el = document.querySelector(`input[name='${name}'][value='${value}']`);
  if (el) el.checked = true;
}
function getSelectedRadio(name) {
  const el = document.querySelector(`input[name='${name}']:checked`);
  return el ? el.value : null;
}
function getSelectedCheckboxes(name) {
  return Array.from(document.querySelectorAll(`input[name='${name}']:checked`)).map(el => el.value);
}

// State-change events cannot be visually represented (see
// scripts/realism_render_job.py's STATUS_NOT_APPLICABLE — the render
// itself already shows this, not a client-side guess) — placement and
// visibility are auto-set to not_applicable and grayed out; only
// behavior stays a real, required judgment for these items.
function applyStateItemNA(item) {
  const isState = item.change_type === "state";
  for (const [axis, boxSelector] of [["placement", ".rating-box.placement"], ["visibility", ".rating-box.visibility"]]) {
    document.querySelector(boxSelector).classList.toggle("na-disabled", isState);
    document.getElementById(`${axis}-options`).style.display = isState ? "none" : "";
    document.getElementById(`${axis}-na-note`).style.display = isState ? "block" : "none";
    if (isState) setRadio(axis, "not_applicable");
  }
}

function allQuestionsAnswered() {
  const item = items[currentIndex];
  if (item.change_type === "state") {
    return !!getSelectedRadio("behavior");
  }
  return getSelectedRadio("placement") && getSelectedRadio("behavior") && getSelectedRadio("visibility");
}

function saveCurrent() {
  if (!allQuestionsAnswered()) {
    alert("Please answer all three rating questions before continuing.");
    return false;
  }
  const item = items[currentIndex];
  const payload = {
    participant_id: participantId,
    item_id: item.item_id,
    placement: getSelectedRadio("placement"),
    behavior: getSelectedRadio("behavior"),
    visibility: getSelectedRadio("visibility"),
    issues: getSelectedCheckboxes("issue"),
    comment: document.getElementById("comment").value,
    time_spent_sec: (Date.now() - itemStartTime) / 1000.0,
  };
  return fetch("/api/response", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(r => {
    if (!r.ok) return r.json().then(e => { throw new Error(e.detail || "save failed"); });
    responses[item.item_id] = payload;
    populateQuestionJumpMenu();
    return true;
  }).catch(err => { alert("Could not save: " + err.message); return false; });
}

function saveAndNext() {
  saveCurrent().then(ok => {
    if (!ok) return;
    if (Object.keys(responses).length >= items.length) { showCelebration(); return; }
    currentIndex = (currentIndex + 1) % items.length;
    showItem();
  });
}

function prevItem() {
  currentIndex = (currentIndex - 1 + items.length) % items.length;
  showItem();
}

function populateQuestionJumpMenu() {
  const sel = document.getElementById("question-jump");
  sel.innerHTML = "";
  items.forEach((it, i) => {
    const opt = document.createElement("option");
    opt.value = String(i);
    const mark = it.item_id in responses ? "✓ " : "";
    opt.textContent = `${mark}${i + 1}. ${it.label}`;
    sel.appendChild(opt);
  });
  sel.value = String(currentIndex);
}

function jumpToQuestion() {
  currentIndex = parseInt(document.getElementById("question-jump").value, 10);
  showItem();
}

function toggleDebug() {
  updateDebugBox();
}

function updateDebugBox() {
  const box = document.getElementById("debug-box");
  const show = document.getElementById("debug-toggle").checked;
  box.style.display = show ? "block" : "none";
  if (!show) return;
  const item = items[currentIndex];
  box.textContent = JSON.stringify(
    { item_id: item.item_id, automatic_signals: item.automatic_signals },
    null, 2,
  );
}

function showCelebration() {
  const overlay = document.getElementById("celebration-overlay");
  overlay.style.display = "flex";
  for (let i = 0; i < 24; i++) {
    const b = document.createElement("div");
    b.className = "burst";
    b.style.left = "50%"; b.style.top = "40%";
    b.style.setProperty("--dx", `${(Math.random() - 0.5) * 400}px`);
    b.style.setProperty("--dy", `${(Math.random() - 0.5) * 400}px`);
    b.style.background = ["gold", "tomato", "mediumseagreen", "cornflowerblue"][i % 4];
    overlay.appendChild(b);
    setTimeout(() => b.remove(), 900);
  }
}

function closeCelebration() {
  document.getElementById("celebration-overlay").style.display = "none";
}
