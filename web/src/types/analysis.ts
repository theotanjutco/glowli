export type SkinType =
  | 'oily'
  | 'dry'
  | 'combination'
  | 'sensitive'
  | 'normal';

export type Severity = 'mild' | 'moderate' | 'severe';

export type SkinCondition = {
  label: string;
  severity: Severity;
  confidence: number;
  description: string;
};

export type AnalyzeResponse = {
  skin_type: SkinType;
  summary: string;
  conditions: SkinCondition[];
};

