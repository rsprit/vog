from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Set


class Stringency(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'


class Protein(BaseModel):
    id: str
    seq: str
    description: Optional[str] = None


class Gene(BaseModel):
    id: str
    seq: str


class Species(BaseModel):
    id: int
    name: str
    phage: bool
    source: str
    version: int


class Group(BaseModel):
    id: str
    description: str
    categories: str
    protein_count: int
    proteins: Set[str]
    species_count: int
    species: Set[str]
    genomes_in_group: int
    genomes_total: int
    ancestors: List[str]
    stringency_high: bool
    stringency_medium: bool
    stringency_low: bool

