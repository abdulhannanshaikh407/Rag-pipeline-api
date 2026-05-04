import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Config from './pages/Config';
import Chat from './pages/Chat';
import DocDetails from './pages/DocDetails';
import Login from './pages/Login';
import { motion, AnimatePresence } from 'motion/react';
import { isLoggedIn } from './lib/api';

export type Page = 'documents' | 'config' | 'chat' | 'details' | 'logs' | 'settings';

export default function App() {
  const [authed, setAuthed] = useState(isLoggedIn());
  const [currentPage, setCurrentPage] = useState<Page>('documents');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  if (!authed) {
    return <Login onSuccess={() => setAuthed(true)} />;
  }

  const navigateTo = (page: Page, docId: string | null = null) => {
    setCurrentPage(page);
    if (docId) setSelectedDocId(docId);
  };

  return (
    <div className="flex h-screen bg-[#080d1a] text-white selection:bg-[#6C63FF]/30 overflow-hidden">
      <Sidebar currentPage={currentPage} onNavigate={navigateTo} />
      <div className="flex-1 flex flex-col min-w-0 relative">
        <Header currentPage={currentPage} />
        <main className="flex-1 overflow-hidden relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentPage}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3, ease: 'easeOut' }}
              className="h-full w-full"
            >
              {currentPage === 'documents' && <Dashboard onSelectDoc={(id) => navigateTo('details', id)} />}
              {currentPage === 'config' && <Config />}
              {currentPage === 'chat' && <Chat />}
              {currentPage === 'details' && <DocDetails docId={selectedDocId} />}
              {(currentPage === 'logs' || currentPage === 'settings') && (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <p className="font-inter tracking-widest uppercase text-xs">Module under maintenance</p>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </main>
        <div className="fixed top-[-10%] right-[-10%] w-[600px] h-[600px] bg-[#6C63FF]/5 blur-[120px] rounded-full z-0 pointer-events-none"></div>
        <div className="fixed bottom-[-10%] left-[260px] w-[500px] h-[500px] bg-[#3622ca]/5 blur-[120px] rounded-full z-0 pointer-events-none"></div>
      </div>
    </div>
  );
}
