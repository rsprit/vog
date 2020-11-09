from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from .service import VogService
from .domain import Protein, Gene, Species, Group, Stringency

svc = VogService('data')
api = FastAPI()


@api.get('/species', response_model=List[Species])
async def list_species(name: Optional[str] = None, phage: Optional[bool] = None):
    return svc.species.find(name=name, phage=phage)


@api.get('/species/{id}', response_model=Species)
async def get_species(id: int):
    try:
        return svc.species[id]
    except KeyError:
        raise HTTPException(404)


@api.get('/proteins/{id}', response_model=Protein)
async def get_protein(id: str):
    try:
        record = svc.proteins[id]
        return Protein(id=record.id, description=record.description, seq=str(record.seq))
    except KeyError:
        raise HTTPException(404)


@api.get('/genes/{id}', response_model=Gene)
async def get_gene(id: str):
    try:
        record = svc.genes[id]
        return Gene(id=record.id, description=record.description, seq=str(record.seq))
    except KeyError:
        raise HTTPException(404)


@api.get('/groups', response_model=List[Group])
async def list_groups(
        description: Optional[str] = None,
        species: Optional[List[str]] = Query(None),
        stringency: Optional[Stringency] = None):
    return svc.groups.find(description=description, species=species, stringency=stringency)


@api.get('/groups/{id}', response_model=Group)
async def get_group(id: str):
    try:
        return svc.groups[id]
    except KeyError:
        raise HTTPException(404)


@api.get('/groups/{id}/proteins', response_model=List[Protein])
async def get_group_proteins(id: str):
    for s in svc.groups.proteins(id):
        yield Protein(id=s.id, seq=str(s.seq), description=s.description)
