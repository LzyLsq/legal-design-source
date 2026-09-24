import pydantic


class BaseResponse(pydantic.BaseModel):
    message: str
    code: int


"""
ComplianceResponse 合规性检查响应体
"""


class ComplianceResult(pydantic.BaseModel):
    content: str
    reason: str


class ComplianceResponseData(pydantic.BaseModel):
    compliance: bool
    result: list[ComplianceResult]


class ComplianceResponse(BaseResponse):
    data: ComplianceResponseData
