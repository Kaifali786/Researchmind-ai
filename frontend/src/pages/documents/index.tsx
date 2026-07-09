import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { 
  Upload, 
  FileText, 
  Trash2, 
  LayoutGrid, 
  List, 
  Search, 
  Loader2, 
  BookOpen,
  Calendar,
  Layers,
  Database
} from 'lucide-react';
import api from '@/lib/api';
import type { Document } from '@/types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/documents/?per_page=100');
      // In FastAPI output of GET /documents/ is { documents: [...], total, page, per_page, total_pages }
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error(error);
      toast.error('Failed to load documents.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    setIsUploading(true);
    const uploadToast = toast.loading('Uploading document...');

    try {
      for (const file of acceptedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        
        await api.post('/documents/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      toast.success('Upload complete!', { id: uploadToast });
      fetchDocuments();
    } catch (error: any) {
      console.error(error);
      const errorMsg = error.response?.data?.detail || 'Failed to upload document.';
      toast.error(errorMsg, { id: uploadToast });
    } finally {
      setIsUploading(false);
    }
  }, []);

  const onDelete = async (docId: string) => {
    const confirmDelete = window.confirm('Are you sure you want to delete this document?');
    if (!confirmDelete) return;

    const deleteToast = toast.loading('Deleting document...');
    try {
      await api.delete(`/documents/${docId}`);
      toast.success('Document deleted.', { id: deleteToast });
      setDocuments(prev => prev.filter(doc => doc.id !== docId));
    } catch (error) {
      console.error(error);
      toast.error('Failed to delete document.', { id: deleteToast });
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/zip': ['.zip']
    },
    multiple: true,
    disabled: isUploading
  });

  const filteredDocuments = documents.filter(doc => 
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    (doc.filename && doc.filename.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const formatBytes = (bytes: number, decimals = 2) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-8">
      {/* Header section */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight font-sans">Research Library</h1>
          <p className="text-muted-foreground mt-1">Upload and manage papers, reports, and academic scripts.</p>
        </div>
        <div className="flex items-center gap-2 border border-border/40 p-1 rounded-lg bg-card/40 backdrop-blur-md">
          <Button 
            variant={viewMode === 'grid' ? 'secondary' : 'ghost'} 
            size="icon" 
            onClick={() => setViewMode('grid')}
            className="h-8 w-8"
          >
            <LayoutGrid className="h-4 w-4" />
          </Button>
          <Button 
            variant={viewMode === 'list' ? 'secondary' : 'ghost'} 
            size="icon" 
            onClick={() => setViewMode('list')}
            className="h-8 w-8"
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div 
        {...getRootProps()} 
        className={`relative overflow-hidden cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition-all duration-300 backdrop-blur-md
          ${isDragActive ? 'border-indigo-500 bg-indigo-500/10' : 'border-border/60 bg-card/20 hover:border-indigo-500/40 hover:bg-card/30'}
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="p-4 rounded-full bg-indigo-500/10 text-indigo-400">
            {isUploading ? (
              <Loader2 className="h-8 w-8 animate-spin" />
            ) : (
              <Upload className="h-8 w-8" />
            )}
          </div>
          <div>
            <p className="text-base font-semibold">
              {isDragActive ? 'Drop the files here...' : 'Drag & drop research papers here, or click to browse'}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Supports PDF, DOCX, TXT, MD, and ZIP files (max 25MB)
            </p>
          </div>
        </div>
        
        {/* Animated accent gradient lines */}
        <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 transform translate-y-full hover:translate-y-0 transition-transform duration-300"></div>
      </div>

      {/* Search & Filter tools */}
      <div className="flex items-center space-x-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search papers by title or filename..." 
            className="pl-9 bg-card/40 border-border/40 focus-visible:ring-indigo-500"
          />
        </div>
      </div>

      {/* Document displays */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh]">
          <Loader2 className="h-10 w-8 animate-spin text-indigo-500" />
          <span className="text-muted-foreground text-sm mt-3">Fetching document index...</span>
        </div>
      ) : filteredDocuments.length === 0 ? (
        <div className="flex flex-col items-center justify-center min-h-[35vh] text-center border border-border/20 rounded-xl p-8 bg-card/10">
          <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-bold">No documents found</h3>
          <p className="text-muted-foreground text-sm max-w-sm mt-1">
            {searchQuery ? 'No documents matched your search filter.' : 'Upload your first research paper to get started.'}
          </p>
        </div>
      ) : viewMode === 'grid' ? (
        <motion.div 
          layout 
          className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
        >
          <AnimatePresence>
            {filteredDocuments.map(doc => (
              <motion.div
                key={doc.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
              >
                <Card className="h-full flex flex-col justify-between border-border/40 bg-card/60 backdrop-blur-md hover:border-indigo-500/30 transition-all duration-300 group">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start gap-2">
                      <div className="p-2 rounded bg-indigo-500/10 text-indigo-500">
                        <FileText className="h-5 w-5" />
                      </div>
                      <Badge variant="outline" className="text-xs uppercase bg-indigo-500/5 text-indigo-400 border-indigo-500/20">
                        {doc.status}
                      </Badge>
                    </div>
                    <CardTitle className="text-base font-bold font-sans mt-3 line-clamp-2 leading-snug group-hover:text-indigo-400 transition-colors">
                      {doc.title}
                    </CardTitle>
                    <CardDescription className="text-xs line-clamp-1 mt-1">
                      {doc.filename}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="py-2 flex-grow">
                    <div className="space-y-1.5 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <Calendar className="h-3.5 w-3.5" />
                        <span>Uploaded: {new Date(doc.uploaded_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Layers className="h-3.5 w-3.5" />
                        <span>Pages: {doc.page_count || 'N/A'}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Database className="h-3.5 w-3.5" />
                        <span>Size: {formatBytes(doc.file_size)}</span>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="pt-3 border-t border-border/20 flex justify-end gap-2 bg-indigo-500/[0.01]">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => onDelete(doc.id)}
                      className="text-muted-foreground hover:text-red-500 hover:bg-red-500/10 h-8 w-8"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </CardFooter>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      ) : (
        <div className="border border-border/40 rounded-xl overflow-hidden bg-card/60 backdrop-blur-md">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-background/80 text-muted-foreground border-b border-border/40 text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3.5">Title</th>
                  <th className="px-6 py-3.5">Filename</th>
                  <th className="px-6 py-3.5">Date</th>
                  <th className="px-6 py-3.5">Size</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/20">
                {filteredDocuments.map(doc => (
                  <tr key={doc.id} className="hover:bg-background/40 transition-colors">
                    <td className="px-6 py-4 font-semibold text-foreground max-w-xs truncate">{doc.title}</td>
                    <td className="px-6 py-4 text-muted-foreground max-w-xs truncate">{doc.filename}</td>
                    <td className="px-6 py-4 text-muted-foreground">{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                    <td className="px-6 py-4 text-muted-foreground">{formatBytes(doc.file_size)}</td>
                    <td className="px-6 py-4 text-right">
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => onDelete(doc.id)}
                        className="text-muted-foreground hover:text-red-500 hover:bg-red-500/10 h-8 w-8"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Documents;
export { Documents };
