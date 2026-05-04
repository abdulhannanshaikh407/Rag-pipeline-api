import { useState } from 'react';

export default function Config() {
  const [config, setConfig] = useState({
    model: 'mistralai/mistral-7b-instruct:free',
    temperature: 0.1,
    maxTokens: 2048,
    embedding: 'sentence-transformers/all-MiniLM-L6-v2',
    embeddingProvider: 'huggingface',
    dimensions: 384,
    retrieval: 'Hybrid',
    topK: 5,
    bm25Weight: 0.3,
    vectorWeight: 0.7,
    chunkSize: 800,
    chunkOverlap: 50,
  });

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-2xl mx-auto">
        <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-8">
          LLM Node
        </h2>

        <div className="space-y-6">
          <div className="glass-card rounded-xl p-6 border border-white/10">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF] mb-4 block">LLM Configuration</span>
            <div className="space-y-4">
              <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Model</label>
                <select
                  value={config.model}
                  onChange={e => setConfig({ ...config, model: e.target.value })}
                  className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none appearance-none"
                >
                  <option>mistralai/mistral-7b-instruct:free</option>
                  <option>gpt-4o</option>
                  <option>claude-opus-4-5</option>
                  <option>gpt-4-turbo-preview</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Temperature</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={config.temperature}
                    onChange={e => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                    className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none"
                  />
                </div>
                <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Max Tokens</label>
                  <input
                    type="number"
                    value={config.maxTokens}
                    onChange={e => setConfig({ ...config, maxTokens: parseInt(e.target.value) })}
                    className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="glass-card rounded-xl p-6 border border-white/10">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF] mb-4 block">Embedding Engine</span>
            <div className="space-y-4">
              <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Provider</label>
                <select
                  value={config.embeddingProvider}
                  onChange={e => setConfig({ ...config, embeddingProvider: e.target.value })}
                  className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none appearance-none"
                >
                  <option>huggingface</option>
                  <option>openai</option>
                </select>
              </div>
              <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Model</label>
                <input
                  value={config.embedding}
                  onChange={e => setConfig({ ...config, embedding: e.target.value })}
                  className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none"
                />
              </div>
              <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Dimensions</label>
                <input
                  type="number"
                  value={config.dimensions}
                  onChange={e => setConfig({ ...config, dimensions: parseInt(e.target.value) })}
                  className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none"
                />
              </div>
            </div>
          </div>

          <div className="glass-card rounded-xl p-6 border border-white/10">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF] mb-4 block">Retrieval Engine</span>
            <div className="space-y-4">
              <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Mode</label>
                <select
                  value={config.retrieval}
                  onChange={e => setConfig({ ...config, retrieval: e.target.value })}
                  className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none appearance-none"
                >
                  <option>Hybrid</option>
                  <option>Vector</option>
                  <option>BM25</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Top-K</label>
                  <input
                    type="number"
                    value={config.topK}
                    onChange={e => setConfig({ ...config, topK: parseInt(e.target.value) })}
                    className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none"
                  />
                </div>
                <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">BM25 Weight</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={config.bm25Weight}
                    onChange={e => setConfig({ ...config, bm25Weight: parseFloat(e.target.value) })}
                    className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="glass-card rounded-xl p-6 border border-white/10">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF] mb-4 block">Chunking Engine</span>
            <div className="grid grid-cols-2 gap-4">
              <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Chunk Size</label>
                <input
                  type="number"
                  value={config.chunkSize}
                  onChange={e => setConfig({ ...config, chunkSize: parseInt(e.target.value) })}
                  className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none"
                />
              </div>
              <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
                <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">Chunk Overlap</label>
                <input
                  type="number"
                  value={config.chunkOverlap}
                  onChange={e => setConfig({ ...config, chunkOverlap: parseInt(e.target.value) })}
                  className="w-full bg-transparent px-4 py-3 text-white text-sm focus:outline-none"
                />
              </div>
            </div>
          </div>

          <div className="glass-card rounded-xl p-6 border border-white/10">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF] mb-4 block">Security</span>
            <div className="relative bg-black/20 rounded border-b border-transparent input-glow">
              <label className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-2">API Key</label>
              <div className="flex items-center px-4 py-3">
                <span className="text-xs text-slate-500 font-mono">•••••••••••••••••••••••••</span>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button className="btn-primary">
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
