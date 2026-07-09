import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { 
  User, 
  Settings as SettingsIcon, 
  Key, 
  Moon, 
  Sun, 
  Cpu, 
  Database,
  Save,
  UserCheck
} from 'lucide-react';
import { useAuthStore } from '@/store/auth-store';
import { useThemeStore } from '@/store/theme-store';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const Settings: React.FC = () => {
  const { user } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();

  const [fullName, setFullName] = useState<string>(user?.full_name || '');
  const [apiKey, setApiKey] = useState<string>(localStorage.getItem('user-openai-key') || '');
  const [llmProvider, setLlmProvider] = useState<string>(localStorage.getItem('user-llm-provider') || 'openai');
  const [ollamaUrl, setOllamaUrl] = useState<string>(localStorage.getItem('user-ollama-url') || 'http://localhost:11434');

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate updating user profile
    toast.success('Profile settings updated successfully!');
  };

  const handleAISettingsSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('user-openai-key', apiKey);
    localStorage.setItem('user-llm-provider', llmProvider);
    localStorage.setItem('user-ollama-url', ollamaUrl);
    toast.success('AI Model settings saved!');
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight font-sans">Settings</h1>
        <p className="text-muted-foreground mt-1">Configure your personal workspace, AI models, and theme preferences.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-12">
        {/* Profile Card */}
        <div className="md:col-span-6 space-y-6">
          <Card className="border-border/40 bg-card/60 backdrop-blur-md">
            <CardHeader>
              <div className="flex items-center gap-2">
                <div className="p-2 rounded bg-indigo-500/10 text-indigo-500">
                  <User className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="font-sans text-lg">Profile Details</CardTitle>
                  <CardDescription>Manage your workspace credentials.</CardDescription>
                </div>
              </div>
            </CardHeader>
            <form onSubmit={handleProfileSave}>
              <CardContent className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Username</label>
                  <Input 
                    disabled 
                    value={user?.username || ''} 
                    className="bg-background/20 border-border/40"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Email Address</label>
                  <Input 
                    disabled 
                    value={user?.email || ''} 
                    className="bg-background/20 border-border/40"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">Full Name</label>
                  <Input 
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Enter your name"
                    className="bg-background/40 border-border/40 focus-visible:ring-indigo-500"
                  />
                </div>
              </CardContent>
              <CardFooter className="border-t border-border/20 pt-4 flex justify-end bg-indigo-500/[0.01]">
                <Button type="submit" size="sm" className="bg-indigo-600 hover:bg-indigo-500">
                  <Save className="mr-2 h-4 w-4" /> Save Profile
                </Button>
              </CardFooter>
            </form>
          </Card>

          {/* Theme Preferences */}
          <Card className="border-border/40 bg-card/60 backdrop-blur-md">
            <CardHeader>
              <div className="flex items-center gap-2">
                <div className="p-2 rounded bg-indigo-500/10 text-indigo-500">
                  <SettingsIcon className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="font-sans text-lg">Appearance</CardTitle>
                  <CardDescription>Customize active theme mode.</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex items-center justify-between py-6">
              <span className="text-sm font-medium">Dark Mode / Light Mode</span>
              <Button 
                variant="outline" 
                onClick={toggleTheme}
                className="border-border/40 bg-card hover:bg-indigo-500/10 hover:text-indigo-400"
              >
                {theme === 'dark' ? (
                  <>
                    <Sun className="mr-2 h-4 w-4 text-amber-500" /> Light Mode
                  </>
                ) : (
                  <>
                    <Moon className="mr-2 h-4 w-4 text-indigo-400" /> Dark Mode
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* AI & Integration Settings */}
        <div className="md:col-span-6">
          <Card className="border-border/40 bg-card/60 backdrop-blur-md h-full flex flex-col justify-between">
            <CardHeader>
              <div className="flex items-center gap-2">
                <div className="p-2 rounded bg-indigo-500/10 text-indigo-500">
                  <Cpu className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="font-sans text-lg">AI Engine Settings</CardTitle>
                  <CardDescription>Configure remote/local Large Language Models.</CardDescription>
                </div>
              </div>
            </CardHeader>
            <form onSubmit={handleAISettingsSave} className="flex-1 flex flex-col justify-between">
              <CardContent className="space-y-4 mt-2">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">LLM Provider</label>
                  <select 
                    value={llmProvider}
                    onChange={(e) => setLlmProvider(e.target.value)}
                    className="w-full flex h-10 rounded-md border border-border/40 bg-background/40 px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="openai">OpenAI (or Compatible API)</option>
                    <option value="ollama">Ollama (Local LLM)</option>
                  </select>
                </div>

                {llmProvider === 'openai' ? (
                  <div className="space-y-1.5 animate-fadeIn">
                    <label className="text-xs font-semibold text-muted-foreground">API Key</label>
                    <div className="relative">
                      <Key className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input 
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="sk-..."
                        className="pl-9 bg-background/40 border-border/40 focus-visible:ring-indigo-500"
                      />
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-1">Your API key is stored locally in your browser.</p>
                  </div>
                ) : (
                  <div className="space-y-1.5 animate-fadeIn">
                    <label className="text-xs font-semibold text-muted-foreground">Ollama Server URL</label>
                    <div className="relative">
                      <Database className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input 
                        value={ollamaUrl}
                        onChange={(e) => setOllamaUrl(e.target.value)}
                        placeholder="http://localhost:11434"
                        className="pl-9 bg-background/40 border-border/40 focus-visible:ring-indigo-500"
                      />
                    </div>
                    <p className="text-[10px] text-muted-foreground mt-1">Make sure your local Ollama server is running and accessible.</p>
                  </div>
                )}
              </CardContent>
              <CardFooter className="border-t border-border/20 pt-4 flex justify-end bg-indigo-500/[0.01]">
                <Button type="submit" size="sm" className="bg-indigo-600 hover:bg-indigo-500">
                  <Save className="mr-2 h-4 w-4" /> Save AI Config
                </Button>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Settings;
export { Settings };
