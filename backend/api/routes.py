from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from backend.services.generator import (
    explain_registers,
    generate_circuit_suggestion,
    generate_firmware_template,
)

router = APIRouter(tags=["generation"])
logger = logging.getLogger("embedgen.api.routes")

SupportedMCU = Literal["LPC2148", "Arduino Uno", "ESP32", "PIC16F877A"]


class GenerateCodeRequest(BaseModel):
    microcontroller: SupportedMCU = Field(..., description="Target MCU family")
    task: str = Field(
        ..., min_length=5, max_length=500, description="Natural language firmware task"
    )

    @field_validator("task")
    @classmethod
    def validate_task(cls, value: str) -> str:
        task = value.strip()
        if len(task) < 5:
            raise ValueError("Task must contain at least 5 non-space characters")
        return task


class GenerateCircuitRequest(BaseModel):
    microcontroller: SupportedMCU = Field(..., description="Target MCU family")
    task: str = Field(..., min_length=5, max_length=500, description="Circuit generation task")

    @field_validator("task")
    @classmethod
    def validate_task(cls, value: str) -> str:
        task = value.strip()
        if len(task) < 5:
            raise ValueError("Task must contain at least 5 non-space characters")
        return task


class ExplainRegistersRequest(BaseModel):
    microcontroller: SupportedMCU = Field(..., description="Target MCU family")
    code: str = Field(
        ...,
        min_length=3,
        max_length=4000,
        description="Embedded C code snippet containing register writes",
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        code = value.strip()
        if "=" not in code:
            raise ValueError("Code must contain at least one register assignment")
        return code


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "EmbedGen API is online"}


@router.post("/generate-code")
def generate_code(payload: GenerateCodeRequest) -> dict[str, object]:
    logger.info("generate_code mcu=%s", payload.microcontroller)
    return generate_firmware_template(payload.microcontroller, payload.task)


@router.post("/generate-circuit")
def generate_circuit(payload: GenerateCircuitRequest) -> dict[str, object]:
    logger.info("generate_circuit mcu=%s", payload.microcontroller)
    return generate_circuit_suggestion(payload.microcontroller, payload.task)


@router.post("/explain-registers")
def explain_registers_route(payload: ExplainRegistersRequest) -> dict[str, object]:
    logger.info("explain_registers mcu=%s", payload.microcontroller)
    return explain_registers(payload.microcontroller, payload.code)
