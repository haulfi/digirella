//===========================================================================================================================
// DigiRella UI Rendering Functions
// Handles all DOM manipulation and rendering logic
//===========================================================================================================================

//----------------------------------------------------------------------------------------------------------------------------
// Clear all child elements from a DOM element
//----------------------------------------------------------------------------------------------------------------------------
function clearElement(element) {
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}

//----------------------------------------------------------------------------------------------------------------------------
// Render farm type cards in the grid
//----------------------------------------------------------------------------------------------------------------------------
function renderFarmTypes(farms, selectedFarmType, containerEl, onSelectCallback) {
  clearElement(containerEl);

  if (!farms.length) {
    const empty = document.createElement("div");
    empty.textContent = "Təsərrüfat tipi tapılmadı.";
    containerEl.appendChild(empty);
    return;
  }

  farms.forEach((farm, index) => {
    const card = document.createElement("div");
    card.className = "card";
    card.style.animationDelay = `${0.05 + index * 0.08}s`;
    card.innerHTML = `<h3>${farmLabel(farm)}</h3><p>Təsərrüfat tipini seçin</p>`;

    if (farm === selectedFarmType) {
      card.classList.add("selected");
    }

    card.addEventListener("click", () => onSelectCallback(farm));
    containerEl.appendChild(card);
  });
}

//----------------------------------------------------------------------------------------------------------------------------
// Render scenario cards in the grid
//----------------------------------------------------------------------------------------------------------------------------
function renderScenarios(scenarios, selectedScenarioId, containerEl, onSelectCallback) {
  clearElement(containerEl);

  if (!scenarios.length) {
    const empty = document.createElement("div");
    empty.textContent = "Ssenari tapılmadı.";
    containerEl.appendChild(empty);
    return;
  }

  scenarios.forEach((scenario, index) => {
    const card = document.createElement("div");
    card.className = "card";
    card.style.animationDelay = `${0.05 + index * 0.08}s`;

    const summary = scenario.summary_az || "Ssenari təsviri yoxdur.";
    card.innerHTML = `<h3>${scenario.id}</h3><p>${summary}</p>`;
    card.dataset.scenarioId = scenario.id;

    if (scenario.id === selectedScenarioId) {
      card.classList.add("selected");
    }

    card.addEventListener("click", () => onSelectCallback(scenario.id));
    containerEl.appendChild(card);
  });
}

//----------------------------------------------------------------------------------------------------------------------------
// Render a single action/recommendation item
//----------------------------------------------------------------------------------------------------------------------------
function renderAction(action) {
  const item = document.createElement("div");
  item.className = "item";

  const title = document.createElement("strong");
  const label = actionLabel(action.code);
  title.textContent = action.priority ? `${label} (${action.priority})` : label;
  item.appendChild(title);

  // Add reason lines
  (action.reasons || []).forEach((reasonText) => {
    const line = document.createElement("div");
    line.textContent = reasonText;
    item.appendChild(line);
  });

  return item;
}

//----------------------------------------------------------------------------------------------------------------------------
// Render recommendations and not-recommended actions
//----------------------------------------------------------------------------------------------------------------------------
function renderResults(modelOutput, doListEl, dontListEl, derivedBoxEl) {
  clearElement(doListEl);
  clearElement(dontListEl);

  if (!modelOutput) {
    doListEl.textContent = "Ssenari seçilməyib.";
    dontListEl.textContent = "Ssenari seçilməyib.";
    if (derivedBoxEl) {
      derivedBoxEl.textContent = "Məlumat yoxdur.";
    }
    return;
  }

  const recs = modelOutput.recommendations || [];
  const notRecs = modelOutput.not_recommended || [];

  // Render recommendations
  recs.forEach((rec) => doListEl.appendChild(renderAction(rec)));
  if (!recs.length) {
    doListEl.textContent = "Tövsiyə yoxdur.";
  }

  // Render not-recommended actions
  notRecs.forEach((rec) => dontListEl.appendChild(renderAction(rec)));
  if (!notRecs.length) {
    dontListEl.textContent = "Məhdudiyyət yoxdur.";
  }

  // Render derived data if element exists
  if (derivedBoxEl) {
    const derived = modelOutput.derived || {};
    derivedBoxEl.textContent = JSON.stringify(derived, null, 2);
  }
}

//----------------------------------------------------------------------------------------------------------------------------
// Add a chat message bubble to the chat area
//----------------------------------------------------------------------------------------------------------------------------
function addChatMessage(chatAreaEl, role, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  chatAreaEl.appendChild(bubble);
  chatAreaEl.scrollTop = chatAreaEl.scrollHeight;
}

//----------------------------------------------------------------------------------------------------------------------------
// Build chatbot reply based on user input and model output
//----------------------------------------------------------------------------------------------------------------------------
function buildChatReply(userText, modelOutput) {
  if (!modelOutput) {
    return "Tövsiyə məlumatı yoxdur.";
  }

  const text = userText.toLowerCase();
  const recs = modelOutput.recommendations || [];
  const notRecs = modelOutput.not_recommended || [];

  // Handle "why" questions
  if (text.includes("niyə") || text.includes("niye")) {
    const target = recs[0] || notRecs[0];
    if (!target) {
      return "Bu gün üçün xüsusi səbəb yoxdur. Hər şey normal vəziyyətdədir.";
    }
    return `çünki, \n- ${target.reasons.join("\n- ")}`;
  }

  // Handle "what to do today" questions
  if (text.includes("bu gun") || text.includes("bu gün") || text.includes("ne et")) {
    if (!recs.length) {
      return "Bu gün üçün xüsusi tövsiyə yoxdur. Hər şey normal vəziyyətdədir. Başqa ssenarini yoxlamaq üçün səhifədən digər ssenarilərə baxa bilərsiniz.";
    }
    const lines = recs.slice(0, 3).map((rec) => {
      const label = actionLabel(rec.code);
      const reason = rec.reasons[0] ? ` — ${rec.reasons[0]}` : "";
      return `- ${label}${reason}`;
    });
    return `Bu gün üçün əsas tövsiyələr:\n${lines.join("\n")}`;
  }

  // Handle "status" or "vəziyyət" questions
  if (text.includes("veziyyet") || text.includes("vəziyyət") || text.includes("necə") || text.includes("nece")) {
    if (!recs.length && !notRecs.length) {
      return "Hər şey yaxşıdır və normal vəziyyətdədir. Heç bir xüsusi tədbir tələb olunmur.";
    }
    if (recs.length) {
      return `${recs.length} tövsiyə var. "Bu gün nə edim?" sualını verə bilərsiniz.`;
    }
  }

  // Handle thank you
  if (text.includes("tesek") || text.includes("təsək") || text.includes("sagol") || text.includes("sağo")) {
    return "Dəyməz. Xoş oldu!";
  }

  // More helpful default response
  return 'Bu ssenari üçün məlumatı görmək üçün "Bu gün nə edim?" və ya "Vəziyyət necədir?" suallarını verə bilərsiniz.';
}
