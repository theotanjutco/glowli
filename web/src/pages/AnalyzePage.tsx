import { useEffect, useState } from 'react';
import { analyzeSelfie, getApiErrorMessage } from '../api/glowli';
import type { AnalyzeResponse } from '../types/analysis';
import { getImageValidationError } from '../utils/imageValidation';

type AnalyzePageProps = {
  onBack: () => void;
  onComplete: (analysis: AnalyzeResponse, file: File) => void;
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

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>): void {
    const input = event.currentTarget;
    const file = input.files?.[0] ?? null;

    setErrorMessage(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const validationError = getImageValidationError(file);

    if (validationError) {
      setSelectedFile(null);
      setErrorMessage(validationError);
      input.value = '';
      return;
    }

    setSelectedFile(file);
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
      onComplete(analysis, selectedFile);
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
          Use a well-lit, front-facing photo. Glowli will validate the image
          before sending it to the FastAPI analysis endpoint.
        </p>
      </section>

      <section className="upload-panel" aria-label="Selfie upload form">
        <label className="file-dropzone">
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
            disabled={isAnalyzing}
          />

          {previewUrl ? (
            <img className="image-preview" src={previewUrl} alt="Selected selfie preview" />
          ) : (
            <span className="empty-preview">
              <strong>Select a selfie</strong>
              <small>JPEG, PNG, or WebP - max 10 MB</small>
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

