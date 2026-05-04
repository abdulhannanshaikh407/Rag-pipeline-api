import { useState, useRef } from 'react';
import { uploadDocument } from '../lib/api';
import { Trash2 } from 'lucide-react';

interface Document {
  id: string;
  name: string;
  size: string;
  pages: number;
  uploadedAt: Date;
  status: 'vectorized' | 'parsing' | 'error' | 'queued';
  chunks: number;
}

export default function Dashboard({ onSelectDoc }: { onSelectDoc: (id: string) => void }) {
  const [documents, setDocuments] = useState<Document[]>([
    { id: '1', name: 'getting-started.md', size: '24 KB', pages: 3, uploadedAt: new Date(), status: 'vectorized', chunks: 12 },
    { id: '2', name: 'api-docs.pdf', size: '142 KB', pages: 12, uploadedAt: new Date(), status: 'vectorized', chunks: 48 },
    { id: '3', name: 'user-guide.txt', size: '56 KB', pages: 8, uploadedAt: new Date(), status: 'parsing', chunks: 24 },
  ]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const result = await uploadDocument(file);
      const newDoc: Document = {
        id: Date.now().toString(),
        name: file.name,
        size: `${(file.size / 1024).toFixed(0)} KB`,
        pages: result.chunks || 1,
        uploadedAt: new Date(),
        status: 'parsing',
        chunks: result.chunks || 1,
      };
      setDocuments(prev => [...prev, newDoc]);
    } catch (err: any) {
      console.error('Upload error:', err);
    } finally {
      e.target.value = '';
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-xl font-bold text-white mb-6">Vector DB</h2>

        <div className="relative group cursor-pointer mb-8" onClick={() => fileInputRef.current?.click()}>
          <div className="scrolling-border rounded-2xl p-12 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-[#6C63FF]/10 rounded-full flex items-center justify-center mb-6 ring-4 ring-[#6C63FF]/5">
              <span className="material-symbols-outlined text-[#6C63FF] text-4xl">cloud_upload</span>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Initialize Data Ingestion</h3>
            <p className="text-slate-400 max-w-md mx-auto text-sm mb-8">
              Drag and drop your technical documentation or click to browse.<br/>
              <span className="text-[#6C63FF] font-medium">PDF, TXT, CSV, JSON, MD</span> supported.
            </p>
            <span className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-8 py-3 rounded-xl font-bold text-sm transition-all">
              Select Core Files
            </span>
          </div>
          <input ref={fileInputRef} type="file" className="hidden" accept=".pdf,.txt,.csv,.md,.json" onChange={handleUpload} />
        </div>

        <div className="glass-card rounded-xl border border-white/10 overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[#6C63FF]">Document Library</span>
          </div>
          <div className="divide-y divide-white/5">
            {documents.map(doc => (
              <div
                key={doc.id}
                onClick={() => onSelectDoc(doc.id)}
                className="px-6 py-4 flex items-center gap-4 hover:bg-white/[0.02] cursor-pointer transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-[#6C63FF]/10 flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-[#6C63FF] text-[20px]">description</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{doc.name}</p>
                  <p className="text-xs text-slate-500">{doc.size} · {doc.pages} pages</p>
                </div>
                <span className={`status-pill ${doc.status}`}>
                  <span className="material-symbols-outlined text-[14px]">
                    {doc.status === 'vectorized' ? 'check_circle' : doc.status === 'parsing' ? 'sync' : doc.status === 'error' ? 'error' : 'schedule'}
                  </span>
                  {doc.status}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDocuments(prev => prev.filter(d => d.id !== doc.id));
                  }}
                  className="p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4 text-slate-500 hover:text-red-400" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
