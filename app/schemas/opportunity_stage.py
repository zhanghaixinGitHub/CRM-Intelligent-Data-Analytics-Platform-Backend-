"""商机阶段推进模型。"""

from pydantic import BaseModel


class OpportunityAdvanceRequest(BaseModel):
    """商机阶段推进请求。"""

    target_stage: str
    proposal_doc_uploaded: bool = False
    review_passed: bool = False

