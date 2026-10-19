import { useState } from 'react';
import AnalyzePage from './pages/AnalyzePage';
import HomePage from './pages/HomePage';
import ResultsPage from './pages/ResultsPage';
import type { AnalyzeResponse } from './types/analysis';

type ActivePage = 'home' | 'analyze' | 'results';

export default function App() {
  const [activePage, setActivePage] = useState<ActivePage>('home');
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [resultFile, setResultFile] = useState<File | null>(null);

  function showHome(): void {
    setAnalysis(null);
    setResultFile(null);
    setActivePage('home');
  }

  function showAnalyze(): void {
    setAnalysis(null);
    setResultFile(null);
    setActivePage('analyze');
  }

  function showResults(completedAnalysis: AnalyzeResponse, file: File): void {
    setAnalysis(completedAnalysis);
    setResultFile(file);
    setActivePage('results');
  }

  if (activePage === 'analyze') {
    return <AnalyzePage onBack={showHome} onComplete={showResults} />;
  }

  if (activePage === 'results' && analysis && resultFile) {
    return (
      <ResultsPage
        analysis={analysis}
        file={resultFile}
        onAnalyzeAnother={showAnalyze}
        onHome={showHome}
      />
    );
  }

  return <HomePage onStart={showAnalyze} />;
}

