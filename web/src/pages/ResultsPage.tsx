import type { AnalyzeResponse } from '../types/analysis';

type ResultsPageProps = {
  analysis: AnalyzeResponse;
  onAnalyzeAnother: () => void;
  onHome: () => void;
};

export default function ResultsPage({
  analysis,
  onAnalyzeAnother,
  onHome,
}: ResultsPageProps) {
  return (
    <main className="results-shell">
      <header className="results-header">
        <div>
          <p className="eyebrow">Analysis complete</p>
          <h1>Your Glowli results</h1>
          <p>{analysis.summary}</p>
        </div>

        <div className="skin-type-card">
          <span>Skin type</span>
          <strong>{analysis.skin_type}</strong>
        </div>
      </header>

      <section className="conditions-section" aria-labelledby="conditions-title">
        <div className="section-heading">
          <h2 id="conditions-title">Condition overview</h2>
          <span>{analysis.conditions.length} result(s)</span>
        </div>

        <div className="condition-grid">
          {analysis.conditions.map((condition, index) => (
            <article className="condition-card" key={`${condition.label}-${index}`}>
              <div className="condition-card-heading">
                <h3>{condition.label}</h3>
                <span className={`severity-badge severity-${condition.severity}`}>
                  {condition.severity}
                </span>
              </div>

              <p>{condition.description}</p>

              <div className="confidence-row">
                <span>Model confidence</span>
                <strong>{Math.round(condition.confidence * 100)}%</strong>
              </div>
            </article>
          ))}
        </div>
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

