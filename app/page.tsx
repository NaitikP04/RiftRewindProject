'use client';
import { useState } from 'react';

export default function Home() {
  const [riotId, setRiotId] = useState('YourName#NA1');
  const [matches, setMatches] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setMatches([]);

    const [gameName, tagLine] = riotId.split('#');
    if (!gameName || !tagLine) {
      setError('Invalid Riot ID format. Use Name#TAG');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/matches/${encodeURIComponent(gameName)}/${encodeURIComponent(tagLine)}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Player not found or API error');
      }
      const data = await response.json();
      setMatches(Array.isArray(data.matches) ? data.matches : []);
    } catch (err) {
      setMatches([]);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-24 bg-gray-900 text-white">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center text-blue-400">Rift Rewind</h1>
        <p className="text-gray-400 text-center mb-6">Track your recent League of Legends matches</p>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={riotId}
            onChange={(e) => setRiotId(e.target.value)}
            placeholder="PlayerName#TAG"
            className="flex-grow p-2 rounded bg-gray-800 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:bg-gray-500"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {error && <p className="text-red-500 mt-4">{error}</p>}

        {Array.isArray(matches) && matches.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold">Last 10 Matches:</h2>
            <ul className="mt-2 space-y-2 list-disc list-inside bg-gray-800 p-4 rounded">
              {matches.map((matchId) => (
                <li key={matchId} className="font-mono text-sm">{matchId}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </main>
  );
}