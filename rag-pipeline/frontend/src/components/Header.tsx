import type { Page } from '../App';

const pageLabels: Record<Page, string> = {
  documents: 'Vector DB',
  chat: 'Chat Interface',
  config: 'LLM Node',
  details: 'Source Viewer',
  logs: 'Retrieval Logs',
  settings: 'Settings',
};

export default function Header({ currentPage }: { currentPage: Page }) {
  return (
    <header className="fixed top-0 right-0 left-[260px] h-16 bg-[#0D0F1A]/20 backdrop-blur-[20px] border-b border-white/10 flex justify-between items-center px-8 z-40">
      <div className="flex items-center gap-8">
        <span className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">
          Aether Engine
        </span>
        <nav className="flex gap-6 items-center">
          <span className="text-[#6C63FF] border-b-2 border-[#6C63FF] pb-1 text-xs font-bold uppercase tracking-widest">
            {pageLabels[currentPage]}
          </span>
        </nav>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          API Connected
        </div>
        <div className="h-8 w-[1px] bg-white/10 mx-2"></div>
        <div className="w-8 h-8 rounded-full bg-[#6C63FF]/20 border border-[#6C63FF]/30 flex items-center justify-center text-xs font-bold text-[#6C63FF]">
          U
        </div>
      </div>
    </header>
  );
}
