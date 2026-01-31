from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
import re

# ── regex helpers ─────────────────────────────────────────────────────────
DATE_RX = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")      # dd.mm.yyyy


# ── model ─────────────────────────────────────────────────────────────────
class EuroScore2Strict(BaseModel):
    # 1 ─ identifiers & demographics -----------------------------------------
    case_number:            Optional[int]  = Field(..., description="Report ID")
    date_of_birth:          Optional[str]  = Field(..., description="dd.mm.yyyy | null")
    date_of_surgery:        Optional[str]  = Field(..., description="dd.mm.yyyy | null")
    sex: Optional[Literal["male", "female"]] = Field(...)

    # 2 ─ binary flags -------------------------------------------------------
    chronic_lung_disease:       bool = Field(...)
    extracardiac_arteriopathy:  bool = Field(...)
    poor_mobility:              bool = Field(...)
    previous_cardiac_surgery:   bool = Field(...)
    active_endocarditis:        bool = Field(...)
    critical_preoperative_state: bool = Field(...)
    dialysis:                   bool = Field(...)
    diabetes_on_insulin:        bool = Field(...)
    ccs_angina_class_4:         bool = Field(...)
    recent_mi:                  bool = Field(...)
    thoracic_aorta_surgery:     bool = Field(...)

    # 3 ─ numeric (nullable) -------------------------------------------------
    creatinine: Optional[float] = Field(..., description="micromol/L | null")
    weight:     Optional[float] = Field(..., description="kg | null")

    # 4 ─ categorical enums --------------------------------------------------
    lv_function: Literal["good", "moderate", "poor", "very poor"] = Field(...)
    pulmonary_hypertension: Literal["No", "moderate", "severe"]   = Field(...)
    nyha_class:  Literal["1", "2", "3", "4"]                      = Field(...)
    urgency:     Literal["elective", "urgent", "emergency", "salvage"] = Field(...)
    major_procedure_weight: Literal[
        "isolated CABG",
        "single non-CABG",
        "2 procedures",
        "3 procedures"
    ] = Field(...)

    # ── validators ----------------------------------------------------------
    @field_validator("date_of_birth", "date_of_surgery")
    @classmethod
    def _validate_date(cls, v):
        if v is None or DATE_RX.fullmatch(v):
            return v
        raise ValueError("must be dd.mm.yyyy or null")

    # -----------------------------------------------------------------------
    model_config = dict(extra="forbid")
