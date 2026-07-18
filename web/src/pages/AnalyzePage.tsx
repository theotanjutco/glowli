import { useEffect, useState } from 'react';
import { analyzeSelfie, getApiErrorMessage } from '../api/glowli';
import type { AnalyzeResponse } from '../types/analysis';

type AnalyzePageProps = {
  onBack: () => void;
  onComplete: (analysis: AnalyzeResponse) => void;
};

export default function AnalyzePage({ onBack, onComplete }: AnalyzePageProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl(null);
      return;
    }

    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [selectedFile]);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setErrorMessage(null);
  }

  async function handleAnalyze(): Promise<void> {
    if (!selectedFile) {
      setErrorMessage('Choose an image before starting the analysis.');
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage(null);

    try {
      const analysis = await analyzeSelfie(selectedFile);
      onComplete(analysis);
    } catch (error: unknown) {
      setErrorMessage(getApiErrorMessage(error));
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <main className="page-shell analyze-page">
      <section className="upload-copy" aria-labelledby="upload-title">
        <button className="text-button" type="button" onClick={onBack}>
          ← Back to home
        </button>
        <p className="eyebrow">Selfie upload</p>
        <h1 id="upload-title">Choose an image to analyze.</h1>
        <p>
          Use a well-lit, front-facing photo. Glowli will send the original file
          to the same FastAPI endpoint used by the earlier mobile prototype.
        </p>
      </section>

      <section className="upload-panel" aria-label="Selfie upload form">
        <label className="file-dropzone">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            disabled={isAnalyzing}
          />

          {previewUrl ? (
            <img className="image-preview" src={previewUrl} alt="Selected selfie preview" />
          ) : (
            <span className="empty-preview">
              <strong>Select a selfie</strong>
              <small>JPEG, PNG, or another browser-supported image</small>
            </span>
          )}
        </label>

        {selectedFile ? (
          <p className="selected-file">Selected: {selectedFile.name}</p>
        ) : null}

        {errorMessage ? (
          <p className="error-message" role="alert">
            {errorMessage}
          </p>
        ) : null}

        <button
          className="primary-button full-width"
          type="button"
          onClick={handleAnalyze}
          disabled={!selectedFile || isAnalyzing}
        >
          {isAnalyzing ? 'Analyzing…' : 'Analyze selfie'}
        </button>
      </section>
    </main>
  );
}

