'use client';
import { useState } from 'react';

interface YearRewind {
  success: boolean;
  review: string;
  puuid: string;
  riot_id: string;
  matches_analyzed: number;
  error?: string;
}

export default function Home() {
  const [riotId, setRiotId] = useState('');
  const [yearRewind, setYearRewind] = useState<YearRewind | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState('');

  // Safe function to extract string from review (handles objects/arrays)
  const getReviewText = (review: any): string => {
    if (typeof review === 'string') {
      return review;
    }
    if (Array.isArray(review)) {
      return review
        .map(item => {
          if (typeof item === 'string') return item;
          if (item && typeof item === 'object' && 'text' in item) return item.text;
          return JSON.stringify(item);
        })
        .join('\n');
    }
    if (review && typeof review === 'object') {
      if ('text' in review) return String(review.text);
      if ('content' in review) return String(review.content);
      return JSON.stringify(review, null, 2);
    }
    return String(review);
  };

  const handleYearRewind = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const trimmedId = riotId.trim();
    if (!trimmedId) {
      setError('Please enter a Riot ID');
      return;
    }

    const [gameName, tagLine] = trimmedId.split('#');
    if (!gameName || !tagLine) {
      setError('Invalid Riot ID format. Use Name#TAG (e.g., Faker#KR1)');
      return;
    }

    setIsLoading(true);
    setError(null);
    setYearRewind(null);
    setProgress('🔍 Finding player...');

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/year-rewind/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`,
        { 
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setYearRewind(data);
        setProgress('');
      } else {
        throw new Error(data.error || 'Failed to generate review');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setProgress('');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-6 md:p-12 bg-gradient-to-b from-gray-900 via-blue-900/20 to-gray-900">
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-5xl md:text-6xl font-bold mb-3 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 text-transparent bg-clip-text">
            Rift Review
          </h1>
          <p className="text-gray-400 text-lg">
            Your AI-Powered League of Legends Year-End Review
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Powered by AWS Bedrock & Riot Games API
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleYearRewind} className="mb-8 animate-fade-in">
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={riotId}
              onChange={(e) => setRiotId(e.target.value)}
              placeholder="Enter Riot ID (e.g., Faker#KR1)"
              disabled={isLoading}
              className="flex-grow p-4 rounded-lg bg-gray-800/50 border-2 border-gray-700 focus:border-blue-500 focus:outline-none transition-colors text-white placeholder-gray-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 font-semibold transition-all transform hover:scale-105 disabled:scale-100 shadow-lg disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Analyzing...
                </span>
              ) : (
                '🎉 Generate Rewind'
              )}
            </button>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/50 border-2 border-red-500 rounded-lg p-4 mb-6 animate-fade-in">
            <p className="text-red-200 flex items-center gap-2">
              <span className="text-2xl">⚠️</span>
              {error}
            </p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="bg-gray-800/50 border-2 border-blue-500/30 rounded-lg p-8 text-center animate-fade-in">
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="animate-spin rounded-full h-20 w-20 border-b-4 border-blue-500"></div>
                <div className="absolute inset-0 flex items-center justify-center text-3xl">
                  🤖
                </div>
              </div>
              <div>
                <p className="text-xl font-semibold text-blue-400 mb-2">
                  AI Agent at Work
                </p>
                <p className="text-gray-400 mb-4">
                  {progress || 'Analyzing your year...'}
                </p>
                <div className="text-sm text-gray-500 space-y-1">
                  <p>✓ Fetching match history</p>
                  <p>✓ Loading match details</p>
                  <p>✓ Calculating trends</p>
                  <p>✓ Analyzing playstyle</p>
                  <p className="text-blue-400">⟳ Generating insights...</p>
                </div>
                <p className="text-xs text-gray-600 mt-4">
                  This may take 3-5 minutes • Stay on this page
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Year Rewind Result */}
        {yearRewind && yearRewind.success && (
          <div className="bg-gradient-to-br from-gray-800/90 to-gray-900/90 border-2 border-blue-500/50 rounded-xl p-8 shadow-2xl animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between mb-6 pb-6 border-b-2 border-gray-700">
              <div>
                <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 text-transparent bg-clip-text">
                  Your 2024 Year Rewind
                </h2>
                <p className="text-gray-400 mt-2">
                  {yearRewind.riot_id} • {yearRewind.matches_analyzed} matches analyzed
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">Powered by</div>
                <div className="text-blue-400 font-semibold">AWS Bedrock AI</div>
              </div>
            </div>

            {/* Review Content */}
            <div className="prose prose-invert prose-lg max-w-none">
              <div className="whitespace-pre-wrap leading-relaxed text-gray-200">
                {getReviewText(yearRewind.review)}
              </div>
            </div>

            {/* Actions */}
            <div className="mt-8 pt-6 border-t-2 border-gray-700 flex gap-4">
              <button
                onClick={() => {
                  setYearRewind(null);
                  setRiotId('');
                }}
                className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold transition-colors"
              >
                ← Generate Another
              </button>
              <button
                onClick={() => {
                  // Copy to clipboard
                  navigator.clipboard.writeText(
                    `🎮 My League of Legends 2024 Year Rewind\n\n${getReviewText(yearRewind.review)}\n\nGenerated by Rift Review`
                  );
                  alert('Copied to clipboard!');
                }}
                className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg font-semibold transition-all"
              >
                📋 Copy to Share
              </button>
            </div>
          </div>
        )}

        {/* Info Footer */}
        {!yearRewind && !isLoading && (
          <div className="mt-12 text-center text-gray-500 text-sm animate-fade-in">
            <p className="mb-2">
              📊 Analyzes ranked & normal matches from the last year
            </p>
            <p className="mb-2">
              🤖 Uses AI to identify your playstyle and provide insights
            </p>
            <p>
              ⚡ Best with 50+ matches • Works for all regions
            </p>
          </div>
        )}
      </div>
    </main>
  );
}