import { useState } from 'react';

interface Chunk {
  id: number;
  content: string;
  chars: number;
  score: number;
}

const mockChunks: Chunk[] = [
  { id: 1, content: 'The RAG pipeline implements a modular architecture with separate components for ingestion, embedding, and retrieval. Each component is designed to be swappable...', chars: 2847, score: 0.92 },
  { id: 2, content: 'Vector search uses dense embeddings to find semantically similar documents. The embedding model converts text into high-dimensional vectors...', chars: 1923, score: 0.87 },
  { id: 3, content: 'BM25 provides sparse retrieval based on term frequency. It works well for keyword-based queries where exact matches matter...', chars: 3156, score: 0.81 },
  { id: 4, content: 'Hybrid search combines both vector and BM25 results using Reciprocal Rank Fusion (RRF) to get the best of both approaches...', chars: 2489, score: 0.78 },
  { id: 5, content: 'Chunking strategies include recursive character splitting, token-based splitting, and semantic chunking. The default is recursive with overlap...', chars: 1678, score: 0.65 },
];

export default function DocDetails({ docId, onBack }: { docId: string | null; onBack?: () => void }) {
  const [selectedChunk, setSelectedChunk] = useState<Chunk | null>(mockChunks[0]);

  if (!docId) {
    return (
      <div className="h-full flex items-center justify-center text-slate-500">
        <p className="font-inter tracking-widest uppercase text-xs">Select a document to view details</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6">
      <div className="max-w-6xl mx-auto w-full flex-1 flex flex-col">
        <div className="flex items-center gap-4 mb-6">
          <button onClick={onBack} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
            <span className="material-symbols-outlined text-[18px]">arrow_back</span>
            <span className="text-sm">Back to Documents</span>
          </button>
        </div>

        <div className="glass-card rounded-xl border border-white/10 p-4 mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-[#6C63FF]/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-[#6C63FF] text-2xl">description</span>
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-bold text-white">Document Details</h2>
              <p className="text-xs text-slate-500">ID: {docId}</p>
            </div>
            <div className="flex gap-6 text-center">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF]">Chunks</p>
                <p className="text-lg font-bold text-white">{mockChunks.length}</p>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF]">Pages</p>
                <p className="text-lg font-bold text-white">12</p>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF]">Status</p>
                <span className="status-pill vectorized">
                  <span className="material-symbols-outlined text-[14px]">check_circle</span>
                  Ready
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex-1 flex gap-6 min-h-0">
          <div className="w-1/3 overflow-y-auto space-y-2 pr-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF] block mb-2">Chunk List</span>
            {mockChunks.map(chunk => (
              <div
                key={chunk.id}
                onClick={() => setSelectedChunk(chunk)}
                className={`glass-card rounded-lg p-4 cursor-pointer border transition-all duration-200 ${
                  selectedChunk?.id === chunk.id
                    ? 'border-[#6C63FF]/50 bg-[#6C63FF]/5'
                    : 'border-white/10 hover:border-white/20'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-white">Chunk {chunk.id}</span>
                  <span className="text-[10px] text-slate-500">{chunk.chars} chars</span>
                </div>
                <div className="w-full bg-white/5 rounded-full h-1 mb-2">
                  <div
                    className="bg-[#6C63FF] h-1 rounded-full"
                    style={{ width: `${chunk.score * 100}%` }}
                  ></div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-500">Relevance</span>
                  <span className="text-[10px] font-bold text-[#6C63FF]">{(chunk.score * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF] block mb-2">Chunk Content</span>
            <div className="glass-card rounded-lg p-6 border border-white/10 font-mono text-sm text-slate-300 leading-relaxed">
              {selectedChunk ? (
                <pre className="whitespace-pre-wrap">{selectedChunk.content}</pre>
              ) : (
                <p className="text-slate-500 text-xs">Select a chunk to view content</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
