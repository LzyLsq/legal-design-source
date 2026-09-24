export interface ComplianceResult {
  content: string;
  reason: string;
}

export interface ComplianceResponseData {
  compliance: boolean;
  result: ComplianceResult[];
}

export interface ComplianceResponse {
  message: string;
  code: number;
  data: ComplianceResponseData;
}