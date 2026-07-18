type HomePageProps = {
  onStart: () => void;
};

export default function HomePage({ onStart }: HomePageProps) {
  return (
    <main className="page-shell hero-page">
      <section className="hero-copy" aria-labelledby="glowli-title">
        <p className="eyebrow">Browser-based skincare analysis</p>
        <h1 id="glowli-title">Understand your skin with Glowli.</h1>
        <p className="hero-description">
          Upload a clear selfie and receive a simple skin summary from the
          Glowli analysis API. The current response is a development mock while
          the computer-vision pipeline is being built.
        </p>

        <div className="hero-actions">
          <button className="primary-button" type="button" onClick={onStart}>
            Analyze a selfie
          </button>
          <span className="privacy-note">Your image is not saved by this prototype.</span>
        </div>
      </section>

      <aside className="process-card" aria-label="How the Glowli prototype works">
        <span className="process-number">01</span>
        <h2>Choose a photo</h2>
        <p>Select a clear, front-facing image from your computer or phone.</p>

        <span className="process-number">02</span>
        <h2>Send it securely</h2>
        <p>The browser uploads the file to the FastAPI analysis endpoint.</p>

        <span className="process-number">03</span>
        <h2>Review the result</h2>
        <p>Glowli displays the typed JSON response as readable result cards.</p>
      </aside>
    </main>
  );
}

