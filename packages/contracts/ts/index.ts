export interface AnalysisRequest {
  run_id: string;
}

export interface Dataset {
  path: string;
  coverage?: string;
}

export interface BacktestReport {
  difference: number;
}

export interface IngestLineage {
  source: string;
  checksum?: string;
}

export interface DQReport {
  checked: number;
  issues: number;
}

export interface XBRLOutput {
  path: string;
  facts?: number;
}
