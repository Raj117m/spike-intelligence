"""
Demand Physics Ontology (DPO)

This file defines the scientific ontology of the Demand Physics Engine.

Every prediction, hypothesis, sensor and validation should ultimately
connect back to one of these concepts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ------------------------------------------------------------------
# Fundamental World Processes
# ------------------------------------------------------------------

class Process(Enum):

    CLIMATE = "Climate"

    ECONOMY = "Economy"

    TECHNOLOGY = "Technology"

    SOCIETY = "Society"

    INFRASTRUCTURE = "Infrastructure"

    POLITICS = "Politics"

    BIOLOGY = "Biology"

    INFORMATION = "Information"

    ENERGY = "Energy"

    SUPPLY_NETWORK = "Supply Network"


# ------------------------------------------------------------------
# Latent States
# ------------------------------------------------------------------

@dataclass(slots=True)
class LatentState:

    name: str

    process: Process

    description: str


# ------------------------------------------------------------------
# Context
# ------------------------------------------------------------------

@dataclass(slots=True)
class Context:

    name: str

    description: str


# ------------------------------------------------------------------
# Human Need
# ------------------------------------------------------------------

@dataclass(slots=True)
class Need:

    name: str

    description: str


# ------------------------------------------------------------------
# Capability
# ------------------------------------------------------------------

@dataclass(slots=True)
class Capability:

    name: str

    description: str


# ------------------------------------------------------------------
# Product
# ------------------------------------------------------------------

@dataclass(slots=True)
class ProductConcept:

    name: str

    category: str


# ------------------------------------------------------------------
# Environmental Driver
# ------------------------------------------------------------------

@dataclass(slots=True)
class Driver:

    name: str

    description: str


# ------------------------------------------------------------------
# Observable Sensor
# ------------------------------------------------------------------

@dataclass(slots=True)
class Sensor:

    name: str

    source: str

    measures: str


# ------------------------------------------------------------------
# Scientific Chain
# ------------------------------------------------------------------

DEMAND_CHAIN = [

    "World Process",

    "Latent State",

    "Context",

    "Need",

    "Capability",

    "Product",

    "Environmental Driver",

    "Observable Sensor",

    "Evidence",

    "Prediction",

    "Validation",

]
