#===========================================================================================================================
# Base Model Abstract Class
# Defines the template workflow for all farm models using the Template Method pattern
#===========================================================================================================================

#----------------------------------------------------------------------------------------------------------------------------
# IMPORTS
from backend.schema import BaseScenarioData, ModelOutput
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Priority ranking for conflict resolution
# Used when multiple rules recommend the same action with different priorities
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}
#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------
# Base model abstract class - All farm models inherit from this
# Implements shared workflow and conflict resolution, subclasses provide specific rules
class BaseModel(ABC):
    # Each subclass must define which ScenarioData class to use
    scenario_data_class: Type[BaseScenarioData] = BaseScenarioData

    #----------------------------------------------------------------------------------------------------------------------------
    # Main entry point - Executes the model workflow
    # Orchestrates parsing, deriving, rule application, and conflict resolution
    def run(self, scenario_data: Dict[str, Any])-> ModelOutput:
        di = self._parse_inputs(scenario_data)                    # shared
        derived = self._derive(di)                                # model-specific derived buckets
        ctx = self._build_struct(di, derived)                     # model-specific context

        recs: List[Dict[str, Any]] = []                           # list of recommendations
        not_recs: List[Dict[str, Any]] = []                       # list of not-reccommended actions

        self._apply_rules(ctx, recs, not_recs)                    # model-specific rules
        recs, not_recs = self._resolve_conflicts(recs, not_recs)  # shared
        return self._make_output(derived, recs, not_recs)         # shared
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Parse scenario data into structured ScenarioData object
    # Extracts decision_inputs from JSON and wraps in accessor object
    # Uses the scenario_data_class defined by each farm model
    def _parse_inputs(self, scenario_data: Dict[str, Any]):
        return self.scenario_data_class(scenario_data.get("decision_inputs", {}))
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Add a recommendation action to the recommendations list
    # Helper method for rules to add actions with code, priority, and reasons
    def _add_rec(self, recs, code: str, priority: str, reasons: List[str]) -> None:
        recs.append({"code": code, "priority": priority, "reasons": reasons})
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Add a not-recommended action to the restrictions list
    # Helper method for rules to add actions that should NOT be done
    def _add_not(self, not_recs, code: str, reasons: List[str]) -> None:
        not_recs.append({"code": code, "reasons": reasons})
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Resolve conflicts between recommendations and restrictions
    # Rules: 1) Highest priority wins for duplicates, 2) Not-recommended always blocks recommended
    def _resolve_conflicts(self, recs, not_recs):
         # Index by code
        rec_by_code: Dict[str, Dict[str, Any]] = {}
        for r in recs:
            code = r["code"]
            # keep highest priority if duplicates
            if code not in rec_by_code:
                rec_by_code[code] = r
            else:
                if PRIORITY_RANK.get(r.get("priority", "low"), 1) > PRIORITY_RANK.get(rec_by_code[code].get("priority", "low"), 1):
                    rec_by_code[code] = r

        not_by_code: Dict[str, Dict[str, Any]] = {}
        for n in not_recs:
            code = n["code"]
            not_by_code[code] = n  # last wins; could also merge reasons

        # Conflict: if code exists in not_recommended, remove from recommendations
        for code in list(rec_by_code.keys()):
            if code in not_by_code:
                del rec_by_code[code]

        # Return clean lists
        final_recs = list(rec_by_code.values())
        final_not = list(not_by_code.values())
        return final_recs, final_not
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Package results into ModelOutput structure
    # Creates final output with derived buckets, recommendations, and not-recommended actions
    def _make_output(self, derived, recs, not_recs):
        return ModelOutput(derived=derived, recommendations=recs, not_recommended=not_recs)
    #----------------------------------------------------------------------------------------------------------------------------

    #----------------------------------------------------------------------------------------------------------------------------
    # Abstract methods - Must be implemented by each farm model subclass
    #----------------------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def _derive(self, di):
        """Compute derived buckets from raw sensor data"""
        ...

    @abstractmethod
    def _build_struct(self, di, derived):
        """Build farm-specific context structure for rule evaluation"""
        ...

    @abstractmethod
    def _apply_rules(self, ctx, recs, not_recs):
        """Apply all farm-specific decision rules"""
        ...
    #----------------------------------------------------------------------------------------------------------------------------