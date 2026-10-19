import { useEffect, useState } from 'react';
import type { AnalyzeResponse } from '../types/analysis';

type ResultsPageProps = {
  analysis: AnalyzeResponse;
  file: File;
  onAnalyzeAnother: () => void;
  onHome: () => void;
};

export default function ResultsPage({
  analysis,
  file,
  onAnalyzeAnother,
  onHome,
}: ResultsPageProps) {
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [imageReady, setImageReady] = useState(false);
  const [imageError, setImageError] = useState<string | null>(null);

  useEffect(() => {
    const url = URL.createObjectURL(file);
    setPhotoUrl(url);
    setImageReady(false);
    setImageError(null);

    return () => URL.revokeObjectURL(url);
  }, [file]);

  return (
    <main className="results-shell">
      <header className="results-header">
        <div>
          <p className="eyebrow">Experimental acne detection</p>
          <h1>Your Glowli results</h1>
          <p>{analysis.summary}</p>
          <p>Boxes show model predictions, not a diagnosis. Confidence scores can be wrong.</p>
        </div>
      </header>

      <section aria-label="Photo with predicted acne regions">
        <div className="detection-photo">
          {photoUrl && (
            <img
              src={photoUrl}
              alt="Uploaded selfie"
              onLoad={(event) => {
                const image = event.currentTarget;
                const matches =
                  image.naturalWidth === analysis.image_width &&
                  image.naturalHeight === analysis.image_height;
                setImageReady(matches);
                setImageError(matches ? null : 'Photo dimensions differ from the analysis; boxes are hidden.');
              }}
              onError={() => {
                setImageReady(false);
                setImageError('The photo could not be displayed. Detection scores are listed below.');
              }}
            />
          )}

          {imageReady && analysis.detections.map((detection, index) => (
            <span
              key={index}
              className="detection-box"
              data-testid="detection-box"
              aria-hidden="true"
              style={{
                left: `${detection.box.x1 * 100}%`,
                top: `${detection.box.y1 * 100}%`,
                width: `${(detection.box.x2 - detection.box.x1) * 100}%`,
                height: `${(detection.box.y2 - detection.box.y1) * 100}%`,
              }}
            >
              <span className="detection-number">{index + 1}</span>
            </span>
          ))}
        </div>

        {imageError && <p role="alert">{imageError}</p>}
      </section>

      <section className="conditions-section" aria-labelledby="detections-title">
        <h2 id="detections-title">Predicted regions ({analysis.detections.length})</h2>
        {analysis.detections.length === 0 ? (
          <p>No regions met the confidence threshold. This does not rule out acne.</p>
        ) : (
          <ol className="detection-list">
            {analysis.detections.map((detection, index) => (
              <li key={index}>
                {detection.label} — model confidence {Math.round(detection.confidence * 100)}%
              </li>
            ))}
          </ol>
        )}
      </section>

      <footer className="results-actions">
        <button className="primary-button" type="button" onClick={onAnalyzeAnother}>
          Analyze another selfie
        </button>
        <button className="secondary-button" type="button" onClick={onHome}>
          Return home
        </button>
      </footer>
    </main>
  );
}
