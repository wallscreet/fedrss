from pydantic import BaseModel


class Entity(BaseModel):
    name: str
    contract_id: str
    location: str


class ContractingAgency(BaseModel):
    name: str
    location: str


class DodContractInfo(BaseModel):
    """
    Pydantic model to extract contract details from text extracted from DOD awards/contracts URL extracted from the DOD contracts RSS feed.
    """
    contractors: list[Entity]
    purpose: str
    amount: float
    contracting_agency: ContractingAgency
