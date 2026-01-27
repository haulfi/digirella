//===========================================================================================================================
// DigiRella Main Application
// Manages application state, event handlers, and coordinates UI and API interactions
//===========================================================================================================================

//----------------------------------------------------------------------------------------------------------------------------
// Application State
//----------------------------------------------------------------------------------------------------------------------------
const state = {
  farmTypes: [],
  farmType: null,
  scenarioId: null,
  modelOutput: null,
  language: DEFAULT_LANGUAGE,
  scenarios: [],
};

//----------------------------------------------------------------------------------------------------------------------------
// DOM Element References
//----------------------------------------------------------------------------------------------------------------------------
let apiInput, connectBtn, resetBtn, statusText;
let farmTypesEl, scenarioListEl, scenarioHintEl;
let selectionPill, doListEl, dontListEl, derivedBox;
let chatArea, chatInput, chatSend;

//----------------------------------------------------------------------------------------------------------------------------
// Initialize DOM references after page load
//----------------------------------------------------------------------------------------------------------------------------
function initDOMReferences() {
  apiInput = document.getElementById("apiBase");
  connectBtn = document.getElementById("connectBtn");
  resetBtn = document.getElementById("resetBtn");
  statusText = document.getElementById("statusText");
  farmTypesEl = document.getElementById("farmTypes");
  scenarioListEl = document.getElementById("scenarioList");
  scenarioHintEl = document.getElementById("scenarioHint");
  selectionPill = document.getElementById("selectionPill");
  doListEl = document.getElementById("doList");
  dontListEl = document.getElementById("dontList");
  derivedBox = document.getElementById("derivedBox") || { textContent: "" };
  chatArea = document.getElementById("chatArea");
  chatInput = document.getElementById("chatInput");
  chatSend = document.getElementById("chatSend");
}

//----------------------------------------------------------------------------------------------------------------------------
// Get API base URL from input field
//----------------------------------------------------------------------------------------------------------------------------
function getApiBase() {
  return apiInput.value.replace(/\/+$/, "");
}

//----------------------------------------------------------------------------------------------------------------------------
// Update status text
//----------------------------------------------------------------------------------------------------------------------------
function setStatus(text) {
  statusText.textContent = text;
}

//----------------------------------------------------------------------------------------------------------------------------
// Load farm types from API and render
//----------------------------------------------------------------------------------------------------------------------------
async function loadFarmTypes() {
  setStatus("Təsərrüfat tipləri yüklənir...");
  try {
    const data = await fetchFarmTypes(getApiBase());
    state.farmTypes = data.farm_types || [];
    renderFarmTypes(state.farmTypes, state.farmType, farmTypesEl, selectFarmType);
    setStatus("Təsərrüfat tipi seçin.");
  } catch (err) {
    setStatus(`Xəta: ${err.message}`);
  }
}

//----------------------------------------------------------------------------------------------------------------------------
// Handle farm type selection
//----------------------------------------------------------------------------------------------------------------------------
async function selectFarmType(farmType) {
  state.farmType = farmType;
  state.scenarioId = null;
  state.modelOutput = null;
  state.scenarios = [];
  selectionPill.textContent = `Təsərrüfat tipi: ${farmLabel(farmType)}`;
  scenarioHintEl.textContent = "Ssenarini seçin.";
  renderFarmTypes(state.farmTypes, state.farmType, farmTypesEl, selectFarmType);
  await loadScenarios();
  renderResults(null, doListEl, dontListEl, derivedBox);
}

//----------------------------------------------------------------------------------------------------------------------------
// Load scenarios for selected farm type
//----------------------------------------------------------------------------------------------------------------------------
async function loadScenarios() {
  if (!state.farmType) {
    scenarioHintEl.textContent = "Əvvəl təsərrüfat tipini seçin.";
    return;
  }
  scenarioHintEl.textContent = "Ssenarilər yüklənir...";
  try {
    const data = await fetchScenarios(getApiBase(), state.farmType);
    state.scenarios = data.scenarios || [];
    renderScenarios(state.scenarios, state.scenarioId, scenarioListEl, selectScenario);
    scenarioHintEl.textContent = "Ssenarini seçin.";
  } catch (err) {
    scenarioHintEl.textContent = `Xəta: ${err.message}`;
  }
}

//----------------------------------------------------------------------------------------------------------------------------
// Handle scenario selection
//----------------------------------------------------------------------------------------------------------------------------
async function selectScenario(scenarioId) {
  state.scenarioId = scenarioId;
  renderScenarios(state.scenarios, state.scenarioId, scenarioListEl, selectScenario);
  await loadRecommendations(scenarioId);
}

//----------------------------------------------------------------------------------------------------------------------------
// Load recommendations for selected scenario
//----------------------------------------------------------------------------------------------------------------------------
async function loadRecommendations(scenarioId) {
  if (!state.farmType) {
    return;
  }
  setStatus("Tövsiyələr yüklənir...");
  try {
    const data = await fetchRecommendations(getApiBase(), state.farmType, scenarioId, state.language);
    state.modelOutput = data.model_output;
    renderResults(state.modelOutput, doListEl, dontListEl, derivedBox);
    setStatus("Hazırdır.");
  } catch (err) {
    setStatus(`Xəta: ${err.message}`);
  }
}

//----------------------------------------------------------------------------------------------------------------------------
// Ensure scenario 1 is loaded for chatbot (auto-selects if needed)
//----------------------------------------------------------------------------------------------------------------------------
async function ensureScenarioOne() {
  if (!state.farmType) {
    addChatMessage(chatArea, "bot", "Zəhmət olmasa təsərrüfat tipini seçin.");
    return false;
  }
  if (!state.scenarios.length) {
    await loadScenarios();
  }
  state.scenarioId = 1;
  renderScenarios(state.scenarios, state.scenarioId, scenarioListEl, selectScenario);
  await loadRecommendations(1);
  return true;
}

//----------------------------------------------------------------------------------------------------------------------------
// Handle chatbot send action
//----------------------------------------------------------------------------------------------------------------------------
async function handleChatSend() {
  const text = chatInput.value.trim();
  if (!text) {
    return;
  }
  chatInput.value = "";
  addChatMessage(chatArea, "user", text);

  const ok = await ensureScenarioOne();
  if (!ok) {
    return;
  }

  const reply = buildChatReply(text, state.modelOutput);
  addChatMessage(chatArea, "bot", reply);
}

//----------------------------------------------------------------------------------------------------------------------------
// Handle connect button click
//----------------------------------------------------------------------------------------------------------------------------
function handleConnect() {
  loadFarmTypes();
}

//----------------------------------------------------------------------------------------------------------------------------
// Handle reset button click
//----------------------------------------------------------------------------------------------------------------------------
function handleReset() {
  state.farmType = null;
  state.scenarioId = null;
  state.modelOutput = null;
  state.farmTypes = [];
  state.scenarios = [];
  selectionPill.textContent = "Təsərrüfat tipi: seçilməyib";
  scenarioHintEl.textContent = "Əvvəl təsərrüfat tipini seçin.";
  renderFarmTypes([], state.farmType, farmTypesEl, selectFarmType);
  renderScenarios([], state.scenarioId, scenarioListEl, selectScenario);
  renderResults(null, doListEl, dontListEl, derivedBox);
  clearElement(chatArea);
  setStatus("Gözləmə rejimi.");
}

//----------------------------------------------------------------------------------------------------------------------------
// Check for API parameter in URL query string
//----------------------------------------------------------------------------------------------------------------------------
function checkUrlParams() {
  const apiParam = new URLSearchParams(window.location.search).get("api");
  if (apiParam) {
    apiInput.value = apiParam;
  }
}

//----------------------------------------------------------------------------------------------------------------------------
// Attach event listeners
//----------------------------------------------------------------------------------------------------------------------------
function attachEventListeners() {
  connectBtn.addEventListener("click", handleConnect);
  resetBtn.addEventListener("click", handleReset);
  chatSend.addEventListener("click", handleChatSend);
  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleChatSend();
    }
  });
}

//----------------------------------------------------------------------------------------------------------------------------
// Initialize application on page load
//----------------------------------------------------------------------------------------------------------------------------
window.addEventListener("load", () => {
  initDOMReferences();
  checkUrlParams();
  attachEventListeners();
  loadFarmTypes();
  addChatMessage(chatArea, "bot", "Salam! Təsərrüfat tipini seçin və sual verin.");
});
