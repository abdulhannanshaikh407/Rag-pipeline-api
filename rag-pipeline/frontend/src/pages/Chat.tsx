import { useState, useRef, useEffect } from 'react';
import { queryStream } from '../lib/api';

interface Message {
  id: string;
  role: 'user' | 'bot';
  text: string;
  timestamp: string;
  sources?: string[];
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'bot',
      text: 'Hello! I\'m Aether Engine. Upload documents and ask me anything about them.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      sources: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMessage]);
    const question = input;
    setInput('');
    setIsTyping(true);

    const botId = (Date.now() + 1).toString();
    const botMessage: Message = {
      id: botId,
      role: 'bot',
      text: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      sources: [],
    };
    setMessages(prev => [...prev, botMessage]);

    try {
      let fullText = '';
      for await (const chunk of queryStream(question)) {
        fullText += chunk;
        setMessages(prev =>
          prev.map(m => m.id === botId ? { ...m, text: fullText } : m)
        );
      }
    } catch (e: any) {
      setMessages(prev =>
        prev.map(m => m.id === botId ? { ...m, text: `Error: ${e.message}` } : m)
      );
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex gap-3 max-w-3xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              msg.role === 'user'
                ? 'bg-[#6C63FF]'
                : 'bg-gradient-to-br from-[#6C63FF] to-[#3622ca] border border-white/10'
            }`}>
              {msg.role === 'user' ? (
                <span className="material-symbols-outlined text-white text-[16px]">person</span>
              ) : (
                <span className="material-symbols-outlined text-white text-[16px]">auto_awesome</span>
              )}
            </div>
            <div className={`rounded-2xl px-6 py-4 ${
              msg.role === 'user'
                ? 'bg-[#6C63FF] text-white rounded-tr-none shadow-[0_4px_20px_rgba(108,99,255,0.2)]'
                : 'glass-card rounded-tl-none'
            }`}>
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.text || (msg.role === 'bot' && isTyping ? 'Thinking...' : '')}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="pt-4 border-t border-white/5">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 block mb-3">Sources Retrieved</span>
                  <div className="flex flex-wrap gap-2">
                    {msg.sources.map((s, i) => (
                      <button key={i} className="flex items-center gap-2 px-2 py-1 rounded bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                        <span className="material-symbols-outlined text-[14px] text-[#6C63FF]">description</span>
                        <span className="text-[11px] font-medium text-white/70">{s}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <p className="text-[10px] text-slate-500 mt-2">{msg.timestamp}</p>
            </div>
          </div>
        ))}
        {isTyping && messages[messages.length - 1]?.text === '' && (
          <div className="flex gap-3 max-w-3xl">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#6C63FF] to-[#3622ca] border border-white/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-[16px]">auto_awesome</span>
            </div>
            <div className="glass-card rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-1">
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:0s]"></span>
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:0.2s]"></span>
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:0.4s]"></span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="p-4">
        <div className="glass-card p-2 rounded-2xl border border-white/10 shadow-[0_0_40px_rgba(0,0,0,0.5)]">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Ask anything about your data cluster..."
            className="w-full bg-transparent border-none focus:ring-0 text-white placeholder:text-slate-500 text-sm min-h-[60px] max-h-[200px] p-4 resize-none"
            rows={1}
          />
          <div className="flex items-center justify-between p-2 border-t border-white/5">
            <div className="flex items-center gap-2">
              <button className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all">
                <span className="material-symbols-outlined text-[20px]">attach_file</span>
              </button>
              <div className="h-4 w-[1px] bg-white/10 mx-1"></div>
              <span className="px-2 py-1 rounded-full bg-[#6C63FF]/10 border border-[#6C63FF]/30 text-[10px] font-bold text-[#6C63FF]">
                &#x26AC; GPT-4o
              </span>
              <span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold text-slate-400">
                Hybrid Retrieval
              </span>
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className="w-10 h-10 bg-[#6C63FF] text-white rounded-xl flex items-center justify-center hover:shadow-[0_0_15px_rgba(108,99,255,0.5)] hover:scale-105 active:scale-95 transition-all disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[20px]">send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
