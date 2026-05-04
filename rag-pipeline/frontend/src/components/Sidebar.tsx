import { logout } from '../lib/api';
import type { Page } from '../App';

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
}

const navItems = [
  { page: 'documents' as Page, icon: 'folder_open', label: 'Documents' },
  { page: 'chat' as Page, icon: 'forum', label: 'Chat' },
  { page: 'config' as Page, icon: 'precision_manufacturing', label: 'Model Config' },
  { page: 'logs' as Page, icon: 'database_search', label: 'Retrieval Logs' },
  { page: 'settings' as Page, icon: 'tune', label: 'Settings' },
];

export default function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  return (
    <aside className="fixed left-0 top-0 h-screen w-[260px] border-r border-white/10 bg-[#0D0F1A]/40 backdrop-blur-[40px] flex flex-col py-8 z-50 glow-right">
      <div className="px-6 mb-10">
        <h1 className="text-lg font-black text-white tracking-widest uppercase">RAG.core</h1>
        <p className="text-[10px] text-[#6C63FF] font-bold tracking-widest uppercase mt-1">Pipeline Active</p>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navItems.map(({ page, icon, label }) => (
          <button
            key={page}
            onClick={() => onNavigate(page)}
            className={`w-full flex items-center px-4 py-3 text-sm font-semibold transition-all duration-300 rounded-lg ${
              currentPage === page
                ? 'text-white bg-white/5 border-r-2 border-[#6C63FF]'
                : 'text-slate-500 hover:text-slate-300 hover:bg-white/10'
            }`}
          >
            <span className="material-symbols-outlined mr-3 text-[20px]">{icon}</span>
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="mt-auto px-4 space-y-4">
        <button
          onClick={() => onNavigate('documents')}
          className="w-full py-3 bg-[#6C63FF] text-white rounded-lg font-bold text-sm flex items-center justify-center hover:shadow-[0_0_20px_rgba(108,99,255,0.4)] transition-all duration-300 active:scale-[0.98]"
        >
          <span className="material-symbols-outlined mr-2 text-[18px]">add</span>
          New Session
        </button>

        <div className="pt-6 border-t border-white/10 space-y-2">
          <button
            onClick={() => { logout(); window.location.reload(); }}
            className="flex items-center px-4 py-2 text-slate-500 hover:text-red-400 text-xs font-medium transition-all w-full"
          >
            <span className="material-symbols-outlined mr-3 text-[18px]">logout</span>
            Sign Out
          </button>
        </div>
      </div>
    </aside>
  );
}
