#===========================================================================================================================
# Model and Formatter Registry
# Auto-registration system for farm models with decorator pattern
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from typing import Any, Callable, Dict, List
from models.base import BaseModel
from models.rules_catalog import create_formatter
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Model registry - Auto-populated by @register_model decorator
# Maps farm type names to their model instances
#----------------------------------------------------------------------------------------------------------------------------
_REGISTRY: Dict[str, BaseModel] = {}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Formatter registry - Auto-populated by register_model decorator
# Maps farm type names to their output formatter functions
#----------------------------------------------------------------------------------------------------------------------------
_FORMATTERS: Dict[str, Callable[[Dict[str, Any], str], Dict[str, Any]]] = {}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Auto-registration decorator for farm models
# Use this decorator on model classes to automatically register them
#----------------------------------------------------------------------------------------------------------------------------
def register_model(farm_type: str):
    """
    Decorator to automatically register a farm model and its formatter.

    Args:
        farm_type: Type identifier (e.g., 'wheat', 'livestock', 'orchard')

    Returns:
        Decorated class

    Example:
        >>> @register_model('wheat')
        >>> class WheatModel(BaseModel):
        >>>     ...

    Benefits:
        - No need to manually edit _REGISTRY
        - Self-documenting (farm type next to model class)
        - Automatically creates formatter using create_formatter()
    """
    def decorator(cls):
    # Store class (not instance) for lazy instantiation
        _REGISTRY[farm_type] = cls
        
        # Auto-create and register formatter for this farm type
        _FORMATTERS[farm_type] = create_formatter(farm_type)
        
        return cls
    return decorator
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Get list of all registered farm types
# Auto-syncs with registry - no manual list needed
#----------------------------------------------------------------------------------------------------------------------------
def get_available_farm_types() -> List[str]:
    """
    Returns list of all currently registered farm types.

    Returns:
        List of farm type identifiers

    Example:
        >>> get_available_farm_types()
        ['wheat', 'livestock', 'orchard']
    """
    return sorted(_REGISTRY.keys())
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Return the model instance for a given farm type
#----------------------------------------------------------------------------------------------------------------------------
def get_model(name: str) -> BaseModel:
    """
    Get registered model for a farm type.

    Args:
        name: Farm type identifier

    Returns:
        Model instance for the farm type

    Raises:
        ValueError: If farm type not registered
    """
    try:
        model_cls = _REGISTRY[name]
        # Lazy instantiation - create only when needed
        if isinstance(model_cls, type):
            return model_cls()
        return model_cls
    except KeyError:
        raise ValueError(f"Unknown model: {name}. Available: {list(_REGISTRY.keys())}")
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Passthrough formatter for farm types without specific templates
# Returns model output unchanged (used as default fallback)
#----------------------------------------------------------------------------------------------------------------------------
def _passthrough_formatter(model_output: Dict[str, Any], language: str) -> Dict[str, Any]:
    """
    Default formatter that returns output unchanged.
    Used when no specific formatter is registered.
    """
    return model_output
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Return the formatter function for a given farm type
# Falls back to passthrough formatter if no specific formatter is registered
#----------------------------------------------------------------------------------------------------------------------------
def get_formatter(name: str) -> Callable[[Dict[str, Any], str], Dict[str, Any]]:
    """
    Get formatter function for a farm type.

    Args:
        name: Farm type identifier

    Returns:
        Formatter function that localizes model output
    """
    return _FORMATTERS.get(name, _passthrough_formatter)
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Import models here to trigger auto-registration via decorators
# This must be at the end of the file to avoid circular imports
#----------------------------------------------------------------------------------------------------------------------------
from models.wheat.wheat import WheatModel  # noqa: E402, F401
from models.livestock.livestock import LivestockModel  # noqa: E402, F401
from models.orchard.orchard import OrchardModel  # noqa: E402, F401
from models.greenhouse.greenhouse import GreenhouseModel  # noqa: E402, F401
from models.mixed.mixed import MixedModel  # noqa: E402, F401
#----------------------------------------------------------------------------------------------------------------------------
