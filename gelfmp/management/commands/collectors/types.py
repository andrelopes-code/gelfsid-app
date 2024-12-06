import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class Aliases:
    def __init__(self, file_name):
        self.file_path = Path(__file__).parent / file_name
        self.aliases = self.load()

    def load(self):
        if self.file_path.exists():
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.aliases, f, indent=4, ensure_ascii=False)

    def add(self, alias, value):
        self.aliases[alias] = value
        self.save()

    def get(self, alias):
        return self.aliases.get(alias)

    def __contains__(self, alias):
        return alias in self.aliases

    def __getitem__(self, alias):
        return self.aliases[alias]


class DocumentData(BaseModel):
    name: Optional[str]
    status: Optional[str]
    filepath: Optional[str]
    validity: Optional[datetime]
    type: str = ''


class SupplierData(BaseModel):
    id: int
    rm_code: Optional[str]
    corporate_name: str
    city: str
    cpf_cnpj: str
    state: str
    material_type: str
    environmental_permit: DocumentData
    ctf: DocumentData
    regief: DocumentData
