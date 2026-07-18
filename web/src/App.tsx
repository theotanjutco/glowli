import { useState } from 'react';
import AnalyzePage from './pages/AnalyzePage';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';
import type { AnalyzeResponse } from './types/analysis';

type ActivePage = 'home' | 'analyze' | 'results';

export default function App() {
  const [activePage, setActivePage] = useState<ActivePage>('home');
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);

  function showHome(): void {
    setActivePage('home');
  }

  function showAnalyze(): void {
    setAnalysis(null);
    setActivePage('analyze');
  }

  function showResults(completedAnalysis: AnalyzeResponse): void {
    setAnalysis(completedAnalysis);
    setActivePage('results');
  }

  if (activePage === 'analyze') {
    return <AnalyzePage onBack={showHome} onComplete={showResults} />;
  }

  if (activePage === 'results' && analysis) {
    return (
      <ResultsPage
        analysis={analysis}
        onAnalyzeAnother={showAnalyze}
        onHome={showHome}
      />
    );
  }

  return <HomePage onStart={showAnalyze} />;
}

