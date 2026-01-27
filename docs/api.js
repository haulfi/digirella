//===========================================================================================================================
// DigiRella API Client
// Handles all communication with the backend REST API
//===========================================================================================================================

//----------------------------------------------------------------------------------------------------------------------------
// Generic fetch wrapper with error handling
//----------------------------------------------------------------------------------------------------------------------------
async function fetchJson(url, options = {}) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || response.statusText);
    }
    return await response.json();
  } catch (error) {
    console.error(`API Error: ${error.message}`);
    throw error;
  }
}

//----------------------------------------------------------------------------------------------------------------------------
// Get list of available farm types from the API
// Returns: { farm_types: string[] }
//----------------------------------------------------------------------------------------------------------------------------
async function fetchFarmTypes(apiBase) {
  const url = `${apiBase}/v1/farm-types`;
  return await fetchJson(url);
}

//----------------------------------------------------------------------------------------------------------------------------
// Get list of scenarios for a specific farm type
// Returns: { scenarios: Array<{ id: number, summary_az: string, ... }> }
//----------------------------------------------------------------------------------------------------------------------------
async function fetchScenarios(apiBase, farmType) {
  const url = `${apiBase}/v1/farms/${farmType}/scenarios`;
  return await fetchJson(url);
}

//----------------------------------------------------------------------------------------------------------------------------
// Get recommendations for a specific farm type and scenario
// Returns: { farm_type: string, scenario_id: number, model_output: ModelOutput }
//----------------------------------------------------------------------------------------------------------------------------
async function fetchRecommendations(apiBase, farmType, scenarioId, language = "az") {
  const url = `${apiBase}/v1/recommendations`;
  const payload = {
    farm_type: farmType,
    scenario_id: scenarioId,
    language: language,
  };

  const options = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  };

  return await fetchJson(url, options);
}

//----------------------------------------------------------------------------------------------------------------------------
// Health check endpoint (optional)
//----------------------------------------------------------------------------------------------------------------------------
async function fetchHealth(apiBase) {
  const url = `${apiBase}/health`;
  return await fetchJson(url);
}
