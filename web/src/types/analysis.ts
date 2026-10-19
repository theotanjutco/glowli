export type BoundingBox = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
};

export type AcneDetection = {
  label: 'Acne';
  confidence: number;
  box: BoundingBox;
};

export type AnalyzeResponse = {
  summary: string;
  image_width: number;
  image_height: number;
  detections: AcneDetection[];
};

