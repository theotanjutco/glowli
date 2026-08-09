// Restricting skintypes to types that the backend will return
export type SkinType = 
    "normal" 
    | "oily" 
    | "dry" 
    | "combination" 
    | "sensitive"
    | "normal";

export type Severity = "mild" | "moderate" | "severe";

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