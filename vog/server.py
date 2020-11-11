from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from .service import VogService
from .domain import Alignment, Protein, Gene, Species, Group, Stringency

svc = VogService('data')
api = FastAPI()


@api.get('/species', response_model=List[Species])
async def list_species(name: Optional[str] = None, phage: Optional[bool] = None):
    return svc.species.find(name=name, phage=phage)


@api.get('/species/{key}', response_model=Species)
async def get_species(key: int):
    try:
        return svc.species[key]
    except KeyError:
        raise HTTPException(404)


@api.get('/proteins/{key}', response_model=Protein)
async def get_protein(key: str):
    try:
        record = svc.proteins[key]
        return Protein(id=record.id, description=record.description, seq=str(record.seq))
    except KeyError:
        raise HTTPException(404)


@api.get('/genes/{key}', response_model=Gene)
async def get_gene(key: str):
    try:
        record = svc.genes[key]
        return Gene(id=record.id, description=record.description, seq=str(record.seq))
    except KeyError:
        raise HTTPException(404)


@api.get('/groups', response_model=List[Group])
async def list_groups(
        description: Optional[str] = None,
        species: Optional[List[str]] = Query(None),
        stringency: Optional[Stringency] = None):
    return svc.groups.find(description=description, species=species, stringency=stringency)


@api.get('/groups/{key}', response_model=Group)
async def get_group(key: str):
    try:
        return svc.groups[key]
    except KeyError:
        raise HTTPException(404)


@api.get('/groups/{key}/proteins', response_model=List[Protein])
async def get_group_proteins(key: str):
    try:
        return [Protein(id=s.id, seq=str(s.seq), description=s.description) for s in svc.groups.proteins(key)]
    except KeyError:
        raise HTTPException(404)


@api.get('/groups/{key}/alignment', response_model=List[Alignment])
async def get_group_alignment(key: str):
    try:
        return [Alignment(id=s.id, seq=str(s.seq), description=s.description) for s in svc.groups.alignment(key)]
    except KeyError:
        raise HTTPException(404)
