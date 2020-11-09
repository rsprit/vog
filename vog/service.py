import os
from pandas import read_table
from Bio import SeqIO
from .domain import Group, Species, Stringency


class SpeciesService:

    def __init__(self, filename):
        self._data = read_table(filename,
                                header=0,
                                names=['name', 'id', 'phage', 'source', 'version'],
                                index_col='id') \
            .assign(phage=lambda df: df.phage == 'phage')

    def __getitem__(self, id):
        return Species(id=id, **self._data.loc[id])

    def find(self, name=None, phage=None):
        result = self._data

        if phage is not None:
            result = result[result.phage == bool(phage)]
        if name is not None:
            result = result[result.name.apply(lambda x: name.lower() in x.lower())]

        for id, row in result.iterrows():
            yield Species(id=id, **row)


class GroupService:

    def __init__(self, directory):
        self._directory = directory

        members = read_table(os.path.join(directory, 'vog.members.tsv'),
                             header=0,
                             names=['group', 'protein_count', 'species_count', 'categories', 'proteins'],
                             index_col='group')
        members = members.assign(
            proteins=members.proteins.apply(lambda s: frozenset(s.split(','))),
        )
        members = members.assign(
            species=members.proteins.apply(lambda s: frozenset(p.split('.')[0] for p in s))
        )

        annotations = read_table(os.path.join(directory, 'vog.annotations.tsv'),
                                 header=0,
                                 names=['group', 'protein_count', 'species_count', 'categories', 'description'],
                                 usecols=['group', 'description'],
                                 index_col='group')

        lca = read_table(os.path.join(directory, 'vog.lca.tsv'),
                         header=0,
                         names=['group', 'genomes_in_group', 'genomes_total', 'ancestors'],
                         index_col='group')
        lca = lca.assign(
            ancestors=lca.ancestors.fillna('').apply(lambda s: s.split(';'))
        )

        virusonly = read_table(os.path.join(directory, 'vog.virusonly.tsv'),
                               header=0,
                               names=['group', 'stringency_high', 'stringency_medium', 'stringency_low'],
                               dtype={'stringency_high': bool, 'stringency_medium': bool, 'stringency_low': bool},
                               index_col='group')

        self._data = members.join(annotations).join(lca).join(virusonly)

    def __getitem__(self, id):
        return Group(id=id, **self._data.loc[id])

    def find(self, description=None, species=None, stringency=None):
        for id, row in self._data.iterrows():
            if description is not None:
                if description.lower() not in row.description.lower():
                    continue

            if species is not None:
                if not set(species).issubset(row.species):
                    continue

            if stringency is not None:
                if stringency == Stringency.high and not row.stringency_high:
                    continue
                if stringency == Stringency.medium and not row.stringency_medium:
                    continue
                if stringency == Stringency.low and not row.stringency_low:
                    continue

            yield Group(id=id, **row)

    def proteins(self, id):
        filename = os.path.join(self._directory, 'faa', '{}.faa'.format(id))
        return SeqIO.parse(filename, 'fasta')


class VogService:

    def __init__(self, directory):
        self._directory = directory
        self._groups = None
        self._species = None
        self._proteins = None
        self._genes = None

    @property
    def species(self):
        if self._species is None:
            self._species = SpeciesService(os.path.join(self._directory, 'vog.species.list'))
        return self._species

    @property
    def proteins(self):
        if self._proteins is None:
            self._proteins = SeqIO.index(os.path.join(self._directory, 'vog.proteins.all.fa'), 'fasta')
        return self._proteins

    @property
    def genes(self):
        if self._genes is None:
            self._genes = SeqIO.index(os.path.join(self._directory, 'vog.genes.all.fa'), 'fasta')
        return self._genes

    @property
    def groups(self):
        if self._groups is None:
            self._groups = GroupService(self._directory)
        return self._groups
