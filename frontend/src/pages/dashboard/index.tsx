import React from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  MessageSquare, 
  Notebook, 
  Activity, 
  Upload, 
  ExternalLink,
  BookOpen,
  ArrowRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth-store';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100 } },
};

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const stats = [
    { title: 'Total Papers', value: '12', icon: FileText, change: '+2 this week', color: 'text-blue-500' },
    { title: 'Questions Asked', value: '48', icon: MessageSquare, change: '+12 today', color: 'text-indigo-500' },
    { title: 'Notes Saved', value: '25', icon: Notebook, change: '15 referenced', color: 'text-emerald-500' },
    { title: 'Workspace Activity', value: '86%', icon: Activity, change: 'High productivity', color: 'text-amber-500' },
  ];

  const recentPapers = [
    { id: '1', title: 'Attention Is All You Need', author: 'Vaswani et al.', date: '2026-07-04', size: '1.2 MB' },
    { id: '2', title: 'BERT: Pre-training of Deep Bidirectional Transformers', author: 'Devlin et al.', date: '2026-07-03', size: '2.4 MB' },
    { id: '3', title: 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks', author: 'Lewis et al.', date: '2026-07-01', size: '945 KB' },
  ];

  const quickActions = [
    { title: 'Upload New Paper', description: 'Supports PDF, DOCX, TXT, and Markdown files.', icon: Upload, path: '/documents', buttonText: 'Upload', color: 'from-blue-600 to-indigo-600' },
    { title: 'Ask Researchmind', description: 'Ask questions and search semantically over your corpus.', icon: MessageSquare, path: '/chat', buttonText: 'Start Chat', color: 'from-indigo-600 to-violet-600' },
    { title: 'Compare Documents', description: 'Analyze models, methods, results, and datasets.', icon: FileText, path: '/compare', buttonText: 'Compare', color: 'from-violet-600 to-purple-600' },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-8"
    >
      {/* Welcome Header */}
      <motion.div variants={itemVariants} className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight font-sans bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            Welcome back, {user?.full_name || 'Researcher'}
          </h1>
          <p className="text-muted-foreground mt-1">
            Analyze papers, organize knowledge, and discover insights with your AI research co-pilot.
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => navigate('/documents')} className="bg-indigo-600 hover:bg-indigo-500">
            <Upload className="mr-2 h-4 w-4" /> Upload Paper
          </Button>
        </div>
      </motion.div>

      {/* Stats Section */}
      <motion.div variants={itemVariants} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="backdrop-blur-md bg-card/60 border-border/40 hover:border-indigo-500/30 transition-all duration-300">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-muted-foreground">{stat.title}</span>
                  <div className={`p-2 rounded-lg bg-indigo-500/10 ${stat.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                </div>
                <div className="mt-4">
                  <h3 className="text-3xl font-bold tracking-tight">{stat.value}</h3>
                  <p className="text-xs text-muted-foreground mt-1">{stat.change}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </motion.div>

      {/* Grid of Main Content */}
      <div className="grid gap-6 md:grid-cols-12">
        {/* Recent Uploads */}
        <motion.div variants={itemVariants} className="md:col-span-7">
          <Card className="h-full border-border/40 bg-card/60 backdrop-blur-md">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="font-sans">Recent Papers</CardTitle>
                <CardDescription>Recently uploaded research documents in your workspace.</CardDescription>
              </div>
              <Button variant="ghost" size="sm" onClick={() => navigate('/documents')} className="text-indigo-400 hover:text-indigo-300">
                View All <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentPapers.map((paper) => (
                  <div 
                    key={paper.id} 
                    className="flex items-center justify-between p-3 rounded-lg border border-border/30 bg-background/40 hover:bg-background/80 transition-all duration-200"
                  >
                    <div className="flex items-center space-x-3 overflow-hidden">
                      <div className="p-2 rounded bg-indigo-500/10 text-indigo-500 shrink-0">
                        <BookOpen className="h-5 w-5" />
                      </div>
                      <div className="overflow-hidden">
                        <p className="text-sm font-semibold truncate">{paper.title}</p>
                        <p className="text-xs text-muted-foreground">{paper.author} • {paper.size}</p>
                      </div>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => navigate('/chat')}
                      className="text-muted-foreground hover:text-indigo-400 shrink-0"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Actions / Getting Started */}
        <motion.div variants={itemVariants} className="md:col-span-5 flex flex-col gap-6">
          <Card className="flex-1 border-border/40 bg-card/60 backdrop-blur-md">
            <CardHeader>
              <CardTitle className="font-sans">Quick Operations</CardTitle>
              <CardDescription>Launch specific RAG-powered workflows immediately.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {quickActions.map((action, i) => {
                const Icon = action.icon;
                return (
                  <div 
                    key={i} 
                    className="group relative flex flex-col justify-between p-4 rounded-lg border border-border/30 bg-background/40 hover:border-indigo-500/30 transition-all duration-200"
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`p-2 rounded-lg bg-gradient-to-br ${action.color} text-white shrink-0`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold">{action.title}</h4>
                        <p className="text-xs text-muted-foreground mt-0.5">{action.description}</p>
                      </div>
                    </div>
                    <div className="mt-3 flex justify-end">
                      <Button 
                        size="sm" 
                        variant="secondary"
                        onClick={() => navigate(action.path)}
                        className="text-xs border border-border/50 hover:bg-indigo-600 hover:text-white transition-all duration-200"
                      >
                        {action.buttonText}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
export { Dashboard };
