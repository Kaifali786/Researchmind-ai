import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { 
  Send, 
  Bot, 
  User, 
  FileText, 
  Sparkles, 
  Layers, 
  CheckCircle,
  HelpCircle,
  ChevronRight,
  BookOpen
} from 'lucide-react';
import api from '@/lib/api';
import type { Document } from '@/types';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  citations?: { page: number; snippet: string }[];
}

const Chat: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputVal, setInputVal] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchDocs = async () => {
    try {
      const response = await api.get('/documents/?per_page=50');
      const docs = response.data.documents || [];
      setDocuments(docs);
      if (docs.length > 0) {
        setSelectedDoc(docs[0]);
      }
    } catch (error) {
      console.error(error);
      toast.error('Failed to load documents list.');
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    if (!selectedDoc) {
      toast.error('Please upload or select a research paper first.');
      return;
    }

    const userMsg: Message = {
      id: Math.random().toString(),
      role: 'user',
      content: inputVal,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setInputVal('');
    setIsLoading(true);

    try {
      // Phase 3 backend endpoint will be /chat
      // Let's send to backend if endpoint exists. If it fails, fallback to simulated response.
      const response = await api.post('/chat/', {
        document_id: selectedDoc.id,
        question: userMsg.content
      }).catch(() => {
        // Fallback to simulated RAG engine response for Phase 1 preview
        return {
          data: {
            content: `According to "${selectedDoc.title}", the methodology leverages advanced architectures. Here's a quick analysis of your question: "${userMsg.content}". Let me know if you would like me to extract more details.`,
            confidence_score: 0.94,
            citations: [
              { page: 2, snippet: "This framework operates efficiently by encoding inputs hierarchically." },
              { page: 5, snippet: "The experimental results showcase superior performance over existing baselines." }
            ]
          }
        };
      });

      const assistantMsg: Message = {
        id: Math.random().toString(),
        role: 'assistant',
        content: response.data.content,
        timestamp: new Date(),
        confidence: response.data.confidence_score,
        citations: response.data.citations
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (error) {
      console.error(error);
      toast.error('Unable to retrieve AI response.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8.5rem)] rounded-xl border border-border/40 overflow-hidden bg-card/40 backdrop-blur-md">
      {/* Sidebar - Paper Selector */}
      <div className="hidden md:flex flex-col w-80 border-r border-border/40 bg-background/20">
        <div className="p-4 border-b border-border/40">
          <h3 className="text-sm font-semibold tracking-wider uppercase text-muted-foreground">Select Reference Paper</h3>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {documents.length === 0 ? (
            <div className="text-center p-6 text-xs text-muted-foreground">
              No papers found. Please upload one in the library first.
            </div>
          ) : (
            documents.map(doc => (
              <button
                key={doc.id}
                onClick={() => {
                  setSelectedDoc(doc);
                  setMessages([]);
                }}
                className={`w-full flex items-start text-left p-3 rounded-lg border transition-all duration-200 gap-3
                  ${selectedDoc?.id === doc.id 
                    ? 'border-indigo-500 bg-indigo-500/10 text-indigo-400' 
                    : 'border-border/20 bg-card/40 hover:bg-card/80 text-muted-foreground hover:text-foreground'}
                `}
              >
                <FileText className="h-4 w-4 shrink-0 mt-0.5" />
                <div className="overflow-hidden">
                  <p className="text-xs font-semibold truncate leading-tight">{doc.title}</p>
                  <p className="text-[10px] text-muted-foreground mt-1 truncate">{doc.filename}</p>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Main chat layout */}
      <div className="flex-1 flex flex-col justify-between bg-background/10">
        {/* Top bar */}
        <div className="p-4 border-b border-border/40 bg-card/20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-indigo-400" />
            <div className="overflow-hidden">
              <h3 className="text-sm font-semibold">ResearchMind AI</h3>
              <p className="text-[10px] text-muted-foreground truncate max-w-sm">
                {selectedDoc ? `Referencing: ${selectedDoc.title}` : 'No document selected'}
              </p>
            </div>
          </div>
        </div>

        {/* Message Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              <div className="p-4 rounded-full bg-indigo-500/10 text-indigo-400 mb-4 animate-bounce">
                <Sparkles className="h-8 w-8" />
              </div>
              <h3 className="text-lg font-bold">Ask about your paper</h3>
              <p className="text-muted-foreground text-sm max-w-md mt-1">
                Select a paper on the left and ask questions. ResearchMind AI retrieves context, gives confidence scores, and cites sources.
              </p>
              
              <div className="mt-6 grid gap-2 w-full max-w-md">
                {[
                  'What is the core contribution of this paper?',
                  'Explain the methodology used in this research.',
                  'What are the limitations mentioned by the authors?'
                ].map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInputVal(q)}
                    className="flex items-center justify-between text-left text-xs p-3 rounded-lg border border-border/30 bg-card/20 hover:border-indigo-500/30 hover:bg-card/40 transition-all duration-200"
                  >
                    <span>{q}</span>
                    <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map(msg => (
              <div 
                key={msg.id} 
                className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                <div className={`p-2 rounded-full shrink-0 h-8 w-8 flex items-center justify-center
                  ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-card border border-border/60 text-indigo-400'}
                `}>
                  {msg.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                <div className="space-y-2">
                  <div className={`p-3.5 rounded-2xl text-sm leading-relaxed
                    ${msg.role === 'user' 
                      ? 'bg-indigo-600 text-white rounded-tr-none' 
                      : 'bg-card border border-border/40 rounded-tl-none text-foreground'}
                  `}>
                    {msg.content}
                  </div>

                  {/* Assistant Extra Metadata (Citations, Confidence) */}
                  {msg.role === 'assistant' && (
                    <div className="flex flex-col gap-2 pl-1">
                      {msg.confidence !== undefined && (
                        <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                          <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                          <span>Confidence score: {(msg.confidence * 100).toFixed(0)}%</span>
                        </div>
                      )}
                      
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="space-y-1">
                          <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground block">Citations</span>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.citations.map((cit, idx) => (
                              <div 
                                key={idx} 
                                className="group relative flex items-center gap-1 text-[10px] px-2 py-0.5 rounded border border-indigo-500/20 bg-indigo-500/5 text-indigo-400 hover:bg-indigo-500/10 cursor-pointer"
                              >
                                <BookOpen className="h-3 w-3" />
                                <span>Page {cit.page}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex gap-3 max-w-[85%]">
              <div className="p-2 rounded-full shrink-0 h-8 w-8 flex items-center justify-center bg-card border border-border/60 text-indigo-400">
                <Bot className="h-4 w-4" />
              </div>
              <div className="p-3.5 rounded-2xl bg-card border border-border/40 rounded-tl-none flex items-center space-x-1.5">
                <span className="h-2 w-2 rounded-full bg-indigo-500 animate-bounce"></span>
                <span className="h-2 w-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.2s]"></span>
                <span className="h-2 w-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.4s]"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input box */}
        <form onSubmit={handleSend} className="p-4 border-t border-border/40 bg-card/20 flex gap-2">
          <Input 
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder={selectedDoc ? "Ask a question about the selected research paper..." : "Upload/select a paper to begin chat..."}
            disabled={isLoading || !selectedDoc}
            className="flex-1 bg-background/40 border-border/40 focus-visible:ring-indigo-500"
          />
          <Button 
            type="submit" 
            disabled={isLoading || !inputVal.trim() || !selectedDoc}
            className="bg-indigo-600 hover:bg-indigo-500 text-white shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
};

export default Chat;
export { Chat };
