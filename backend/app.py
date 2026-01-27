#===========================================================================================================================
# FastAPI Backend Application
# REST API for DigiRella farm decision support system
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from fastapi import FastAPI, HTTPException, Path as ApiPath, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import json
from typing import Dict, Any, List
from dataclasses import asdict
from models.registry import get_model, get_formatter, get_available_farm_types
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# GLOBAL CONFIGURATION
#----------------------------------------------------------------------------------------------------------------------------
# Base directory
BASE_DIR = Path(__file__).resolve().parent
# Farm assets directory
FARMS_SCEN_DIR = (BASE_DIR / "../assets/farms").resolve()
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# API Request/Response Models
#----------------------------------------------------------------------------------------------------------------------------
class RecommendRequest(BaseModel):
    """Request model for recommendations endpoint"""
    farm_type: str
    scenario_id: int = Field(..., ge=1, le=1000)
    language: str = Field("az", min_length=2, max_length=5)
    @field_validator('farm_type')
    def validate_farm_type(cls, v):
        ft = v.strip().lower()
        supported_farms = get_available_farm_types()
        if ft not in supported_farms:
            raise ValueError(f"Unsupported farm_type='{ft}'. Supported: {supported_farms}")
        return ft
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Initialize FastAPI Application
#----------------------------------------------------------------------------------------------------------------------------
app = FastAPI(
    title="Digirella - Farm Assistant API",
    description="AI-powered agricultural decision support system",
    version="1.0.0"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Helper Functions
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Extract scenario ID from filename
#----------------------------------------------------------------------------------------------------------------------------
def extract_scenario_id(path: Path) -> int:
    """
    Extract scenario ID from filename like 'scenario_10.json'.

    Args:
        path: Path to scenario file

    Returns:
        Scenario ID as integer
    """
    return int(path.stem.split("_")[1])
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Validate and normalize farm type
# Used as FastAPI dependency to automatically validate farm types
#----------------------------------------------------------------------------------------------------------------------------
def validate_farm_type(farm_type: str) -> str:
    """
    FastAPI dependency to validate and normalize farm type.

    Args:
        farm_type: Farm type from request path/body

    Returns:
        Normalized farm type (lowercase, stripped)

    Raises:
        HTTPException: If farm type is not supported
    """
    ft = farm_type.strip().lower()
    supported_farms = get_available_farm_types()

    if ft not in supported_farms:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported farm_type='{ft}'. Supported: {supported_farms}"
        )
    return ft
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Get scenario file path for a specific farm type and scenario ID
#----------------------------------------------------------------------------------------------------------------------------
def scenario_path(farm_type: str, scenario_id: int) -> Path:
    """
    Build path to scenario JSON file.

    Args:
        farm_type: Type of farm (already normalized)
        scenario_id: Scenario number

    Returns:
        Path to scenario file
    """
    return FARMS_SCEN_DIR / farm_type / "synthetic_scenarios" / f"scenario_{scenario_id}.json"
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Load JSON file with error handling
#----------------------------------------------------------------------------------------------------------------------------
def load_json(path: Path) -> Dict[str, Any]:
    """
    Load and parse JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        HTTPException: If file not found or invalid JSON
    """
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in {path}: {e}")
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Load specific scenario data
#----------------------------------------------------------------------------------------------------------------------------
def load_scenario(farm_type: str, scenario_id: int) -> Dict[str, Any]:
    """
    Load scenario data for a specific farm type and ID.

    Args:
        farm_type: Type of farm (already normalized)
        scenario_id: Scenario number

    Returns:
        Scenario data dictionary
    """
    return load_json(scenario_path(farm_type, scenario_id))
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# List all scenarios for a farm type
#----------------------------------------------------------------------------------------------------------------------------
def list_scenarios_for_farm(farm_type: str) -> List[Dict[str, Any]]:
    """
    Get list of all available scenarios for a farm type.

    Args:
        farm_type: Type of farm (already normalized)

    Returns:
        List of scenario metadata (id, scenario_id, summary_az)
    """
    scen_dir = FARMS_SCEN_DIR / farm_type / "synthetic_scenarios"

    if not scen_dir.exists():
        return []

    # Find all scenario files and sort by ID
    files = sorted(scen_dir.glob("scenario_*.json"), key=extract_scenario_id)

    scenarios = []
    for file_path in files:
        data = load_json(file_path)
        # Extract minimal metadata for UI
        scenarios.append({
            "id": extract_scenario_id(file_path),
            "scenario_id": data.get("scenario_id", ""),
            "summary_az": data.get("summary_az", "")
        })

    return scenarios
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Run farm model and format output
#----------------------------------------------------------------------------------------------------------------------------
def run_model(farm_type: str, scenario_data: Dict[str, Any], language: str = "az") -> Dict[str, Any]:
    """
    Execute farm model and localize output.

    Args:
        farm_type: Type of farm (already normalized)
        scenario_data: Input scenario data
        language: Output language (default: 'az')

    Returns:
        Formatted model output with recommendations

    Raises:
        HTTPException: If model not found or execution fails
    """
    try:
        # Get model and run it
        model = get_model(farm_type)
        model_out = model.run(scenario_data)

        # Get formatter and localize output
        formatter = get_formatter(farm_type)
        return formatter(asdict(model_out), language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model execution failed: {e}")
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# API Endpoints
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Health check endpoint
#----------------------------------------------------------------------------------------------------------------------------
@app.get("/health")
def health():
    """
    Health check endpoint.

    Returns:
        Status dictionary
    """
    return {"ok": True, "status": "healthy"}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Get list of supported farm types
#----------------------------------------------------------------------------------------------------------------------------
@app.get("/v1/farm-types")
def get_farm_types():
    """
    Get list of all supported farm types.

    Returns:
        Dictionary with farm_types list (auto-detected from registry)
    """
    return {"farm_types": get_available_farm_types()}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Get all scenarios for a farm type
#----------------------------------------------------------------------------------------------------------------------------
@app.get("/v1/farms/{farm_type}/scenarios")
def get_scenarios(farm_type: str = Depends(validate_farm_type)):
    """
    Get list of scenarios for a specific farm type.

    Args:
        farm_type: Farm type (validated by dependency)

    Returns:
        Dictionary with farm_type and scenarios list
    """
    return {
        "farm_type": farm_type,
        "scenarios": list_scenarios_for_farm(farm_type)
    }
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Get specific scenario data
#----------------------------------------------------------------------------------------------------------------------------
@app.get("/v1/farms/{farm_type}/scenarios/{scenario_id}")
def get_scenario(
    farm_type: str = Depends(validate_farm_type),
    scenario_id: int = ApiPath(..., ge=1, le=1000)
):
    """
    Get raw data for a specific scenario.

    Args:
        farm_type: Farm type (validated by dependency)
        scenario_id: Scenario number (1-1000)

    Returns:
        Dictionary with farm_type, scenario_id, and scenario_data
    """
    data = load_scenario(farm_type, scenario_id)
    return {
        "farm_type": farm_type,
        "scenario_id": scenario_id,
        "scenario_data": data
    }
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Generate recommendations for a scenario
#----------------------------------------------------------------------------------------------------------------------------
@app.post("/v1/recommendations")
def recommendations(req: RecommendRequest):
    """
    Generate farming recommendations for a specific scenario.

    Args:
        req: Request with farm_type, scenario_id, and language

    Returns:
        Dictionary with farm_type, scenario_id, and model_output
    """

    # Load scenario and run model
    scenario_data = load_scenario(req.farm_type, req.scenario_id)
    model_output = run_model(req.farm_type, scenario_data, req.language)

    return {
        "farm_type": req.farm_type,
        "scenario_id": req.scenario_id,
        "model_output": model_output
    }
#----------------------------------------------------------------------------------------------------------------------------
