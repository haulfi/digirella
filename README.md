# DigiRella - Agricultural Decision Support System

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**DigiRella** is an AI-powered agricultural decision support system that provides intelligent farming recommendations based on real-time sensor data and environmental conditions. The system uses domain-specific decision models for different farm types to generate contextual advice in multiple languages.

## 🌾 Features

- **Multi-Farm Support**: Specialized models for wheat, livestock, orchard, greenhouse, and mixed farming
- **Intelligent Recommendations**: Context-aware decision rules based on weather, soil, crop stage, and resource availability
- **Conflict Resolution**: Automatic prioritization and blocking of incompatible actions
- **Multi-Language**: Template-based localization system (currently supports Azerbaijani)
- **RESTful API**: Clean REST API with OpenAPI/Swagger documentation
- **Interactive UI**: Web-based interface with scenario selection and chatbot
- **Extensible Architecture**: Plugin-style model registration with decorator pattern

## 🌐 Live Demo

- **Frontend**: [https://haulfi.github.io/digirella/](https://haulfi.github.io/digirella/)
- **Backend API**: [https://digirella-alfalfa.onrender.com](https://digirella-alfalfa.onrender.com)
- **API Docs**: [https://digirella-alfalfa.onrender.com/docs](https://digirella-alfalfa.onrender.com/docs)

The live demo is fully functional. Select a farm type, choose a scenario, and explore AI-powered farming recommendations.

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- Modern web browser (for frontend)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/haulfi/digirella.git
   cd digirella
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   cd backend
   uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Open the frontend**
   - Open `docs/index.html` in your browser
   - Or serve with a local web server:
     ```bash
     cd docs
     python -m http.server 8080
     ```
   - Navigate to `http://localhost:8080`

## 📁 Project Structure

```
DigiRella/
├── backend/                    # FastAPI REST API server
│   ├── app.py                 # Main application & endpoints
│   ├── schema.py              # Pydantic models & data schemas
├── models/                     # Farm-specific decision models
│   ├── base.py               # Abstract base model (template method pattern)
│   ├── registry.py           # Auto-registration system
│   ├── rules_catalog.py      # Localization & formatting
│   ├── wheat/                # Wheat farming model
│   ├── livestock/            # Dairy cattle model
│   ├── orchard/              # Fruit tree model
│   ├── greenhouse/           # Protected crop model
│   └── mixed/                # Mixed farm operations
├── docs/                       # Frontend & Documentation (GitHub Pages)
│   ├── index.html            # Main page
│   ├── app.js                # Application logic
│   ├── api.js                # API client
│   ├── ui.js                 # UI rendering
│   ├── docs.js               # Documentation modal
│   ├── config.js             # Configuration
│   ├── styles.css            # Styling
│   ├── logo.png              # Brand logo
│   └── documentation_az.md   # Azerbaijani docs
├── assets/                     # Test scenarios
│   └── farms/                # Farm-specific scenarios
├── frontend/                   # Original frontend (archived)
└── requirements.txt          # Python dependencies
```
**Note: You dont need copied files in dcs folder. They are there for deploying in render**
## 🔧 Architecture

### Backend Architecture

DigiRella uses a **Template Method Pattern** for consistent model execution flow:

```python
@register_model("wheat")
class WheatModel(BaseModel):
    def _derive(self, di):
        # Convert raw values to categorical buckets

    def _build_struct(self, di, derived):
        # Create immutable context structure

    def _apply_rules(self, ctx, recs, not_recs):
        # Apply domain-specific decision rules
```

**Execution Pipeline:**
1. **Parse Inputs** → Extract decision_inputs from JSON
2. **Derive Buckets** → Convert continuous values to categories
3. **Build Context** → Create immutable dataclass structure
4. **Apply Rules** → Execute farm-specific decision logic
5. **Resolve Conflicts** → Prioritize and block conflicting actions
6. **Format Output** → Localize reasons and recommendations

### Registry Pattern

Models auto-register using decorators:

```python
@register_model("wheat")
class WheatModel(BaseModel):
    # Model automatically registered on import
```

Benefits:
- No manual registration required
- Self-documenting
- Hot-pluggable models

## 🌐 API Documentation

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "ok": true,
  "status": "healthy"
}
```

#### `GET /v1/farm-types`
Get list of available farm types.

**Response:**
```json
{
  "farm_types": ["wheat", "livestock", "orchard", "greenhouse", "mixed"]
}
```

#### `GET /v1/farms/{farm_type}/scenarios`
List scenarios for a farm type.

**Response:**
```json
{
  "farm_type": "wheat",
  "scenarios": [
    {
      "id": 1,
      "scenario_id": "wheat_dry_hot",
      "summary_az": "Quraqlıq və isti hava şəraiti"
    }
  ]
}
```

#### `POST /v1/recommendations`
Generate recommendations for a scenario.

**Request:**
```json
{
  "farm_type": "wheat",
  "scenario_id": 1,
  "language": "az"
}
```

**Response:**
```json
{
  "farm_type": "wheat",
  "scenario_id": 1,
  "model_output": {
    "derived": {
      "moisture_bucket": "low",
      "weather_bucket": "hot"
    },
    "recommendations": [
      {
        "code": "IRRIGATE_TODAY",
        "priority": "yüksək",
        "reasons": ["Torpaq rütubəti aşağıdır (16%)."],
        "reasons_structured": [{"key": "soil_moisture_low", "params": {"sm": 16}}]
      }
    ],
    "not_recommended": []
  }
}
```

## 🧩 Adding a New Farm Type

1. **Create model directory**
   ```bash
   mkdir models/yourfarm
   touch models/yourfarm/__init__.py
   touch models/yourfarm/yourfarm.py
   ```

2. **Define your model**
   ```python
   from models.base import BaseModel
   from models.registry import register_model

   @register_model("yourfarm")
   class YourFarmModel(BaseModel):
       def _derive(self, di):
           return {"bucket": "value"}

       def _build_struct(self, di, derived):
           return YourFarmStruct(...)

       def _apply_rules(self, ctx, recs, not_recs):
           # Your rules here
           pass
   ```

3. **Add localization templates**
   Edit `models/rules_catalog.py`:
   ```python
   _TEMPLATES = {
       "yourfarm": {
           "az": {
               "reason_key": "Translated message {param}."
           }
       }
   }
   ```

4. **Import in registry**
   Edit `models/registry.py`:
   ```python
   from models.yourfarm.yourfarm import YourFarmModel  # noqa: E402, F401
   ```

## 🧪 Testing with Scenarios

Test scenarios are located in `assets/farms/{farm_type}/synthetic_scenarios/`.

**Example scenario structure:**
```json
{
  "scenario_id": "wheat_dry_hot",
  "summary_az": "Quraqlıq və isti hava şəraiti",
  "decision_inputs": {
    "weather": {
      "t_max_c": 35,
      "humidity_pct": 25,
      "rain_mm_24h": 0
    },
    "soil": {
      "soil_moisture_pct": 16
    },
    "crop": {
      "stage_code": "tillering"
    }
  }
}
```

## 🎨 Frontend Usage

1. **Connect to API**: Enter backend URL (default: `http://127.0.0.1:8000`)
2. **Select Farm Type**: Choose from available farm types
3. **Pick Scenario**: Select a test scenario
4. **View Recommendations**: See "Do" and "Don't" actions
5. **Chat**: Ask questions about the current scenario

## 🔒 Security Considerations

- **CORS**: Currently set to allow all origins (`*`). Restrict in production.
- **Validation**: All inputs validated with Pydantic models
- **No Authentication**: Add authentication for production deployment
- **Rate Limiting**: Consider adding rate limiting for public APIs

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.13+

# Install dependencies
pip install -r requirements.txt

# Run with verbose logging
uvicorn app:app --reload --log-level debug
```

### Frontend can't connect
- Verify backend is running on port 8000
- Check CORS settings in `backend/app.py`
- Open browser console for error messages

### No recommendations generated
- Verify scenario JSON structure matches schema
- Check backend logs for validation errors
- Ensure farm type is registered in `models/registry.py`

## 📊 Performance Optimization

- **Model Lazy Loading**: Models instantiated only when needed
- **Scenario Caching**: Add `@lru_cache` to file loading functions
- **Response Caching**: Consider Redis for frequently-used scenarios
- **Database**: Move scenarios from JSON files to database for production


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **haul** - Initial work

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Pydantic for data validation
- Agricultural domain experts for decision rules

## 📧 Contact

- Project Link: [https://github.com/haulfi/digirella](https://github.com/haulfi/digirella)
- Email: ulfathasangarayev@gmail.com

---

**Made with 🌱 for farmers**