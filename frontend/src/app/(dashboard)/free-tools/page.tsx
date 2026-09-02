'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Zap, Wand2, Shield, MessageSquare, Loader2, AlertCircle } from 'lucide-react';
import apiClient from '@/lib/apiClient';
import { useToast } from '@/hooks/useToast';

interface AnalysisResult {
  success: boolean;
  [key: string]: any;
}

export default function FreeToolsPage() {
  const { toast } = useToast();

  // Beat Analyzer State
  const [analyzeFile, setAnalyzeFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  // Copyright Scanner State
  const [copyrightFile, setCopyrightFile] = useState<File | null>(null);
  const [scanningCopyright, setScanningCopyright] = useState(false);
  const [copyrightResult, setCopyrightResult] = useState<AnalysisResult | null>(null);

  // Caption Generator State
  const [captionData, setCaptionData] = useState({
    beat_title: '',
    beat_genre: 'Afrobeat',
    beat_mood: 'energetic',
    bpm: 100,
    tone: 'casual',
    platform: 'instagram',
  });
  const [generatingCaption, setGeneratingCaption] = useState(false);
  const [captionResult, setCaptionResult] = useState<AnalysisResult | null>(null);

  // Beat Analyzer Handlers
  const handleAnalyzeFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setAnalyzeFile(e.target.files[0]);
    }
  };

  const handleAnalyzeBeat = async () => {
    if (!analyzeFile) {
      toast({
        title: 'No file selected',
        description: 'Please select an audio file to analyze',
        variant: 'error',
      });
      return;
    }

    try {
      setAnalyzing(true);
      const formData = new FormData();
      formData.append('file', analyzeFile);

      const response = await apiClient.post<AnalysisResult>(
        '/api/v1/free-tools/analyze-beat',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );

      if (response.data.success) {
        setAnalysisResult(response.data);
        toast({
          title: 'Analysis complete',
          description: 'Beat audio quality analyzed successfully',
          variant: 'success',
        });
      }
    } catch (error: any) {
      toast({
        title: 'Analysis failed',
        description: error.response?.data?.detail || 'Could not analyze beat',
        variant: 'error',
      });
    } finally {
      setAnalyzing(false);
    }
  };

  // Copyright Scanner Handlers
  const handleCopyrightFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setCopyrightFile(e.target.files[0]);
    }
  };

  const handleScanCopyright = async () => {
    if (!copyrightFile) {
      toast({
        title: 'No file selected',
        description: 'Please select an audio file to scan',
        variant: 'error',
      });
      return;
    }

    try {
      setScanningCopyright(true);
      const formData = new FormData();
      formData.append('file', copyrightFile);

      const response = await apiClient.post<AnalysisResult>(
        '/api/v1/free-tools/scan-copyright',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );

      if (response.data.success) {
        setCopyrightResult(response.data);
        toast({
          title: 'Scan complete',
          description: 'Copyright scan finished successfully',
          variant: 'success',
        });
      }
    } catch (error: any) {
      toast({
        title: 'Scan failed',
        description: error.response?.data?.detail || 'Could not scan copyright',
        variant: 'error',
      });
    } finally {
      setScanningCopyright(false);
    }
  };

  // Caption Generator Handlers
  const handleGenerateCaption = async () => {
    if (!captionData.beat_title) {
      toast({
        title: 'Missing information',
        description: 'Please enter a beat title',
        variant: 'error',
      });
      return;
    }

    try {
      setGeneratingCaption(true);
      const params = new URLSearchParams({
        beat_title: captionData.beat_title,
        beat_genre: captionData.beat_genre,
        beat_mood: captionData.beat_mood,
        bpm: captionData.bpm.toString(),
        tone: captionData.tone,
        platform: captionData.platform,
      });

      const response = await apiClient.get<AnalysisResult>(
        `/api/v1/free-tools/generate-caption?${params}`
      );

      if (response.data.success) {
        setCaptionResult(response.data);
        toast({
          title: 'Caption generated',
          description: 'Marketing caption created successfully',
          variant: 'success',
        });
      }
    } catch (error: any) {
      toast({
        title: 'Generation failed',
        description: error.response?.data?.detail || 'Could not generate caption',
        variant: 'error',
      });
    } finally {
      setGeneratingCaption(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'clear':
        return 'text-green-500 bg-green-500/10';
      case 'low':
        return 'text-blue-500 bg-blue-500/10';
      case 'medium':
        return 'text-yellow-500 bg-yellow-500/10';
      case 'high':
        return 'text-red-500 bg-red-500/10';
      case 'blocked':
        return 'text-red-600 bg-red-600/10';
      default:
        return 'text-gray-500 bg-gray-500/10';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">AI Promotion Tools</h1>
          <p className="text-gray-400">
            Free AI-powered tools to analyze, protect, and promote your beats
          </p>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="analyzer" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-gray-800 border border-gray-700">
            <TabsTrigger value="analyzer" className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Analyzer
            </TabsTrigger>
            <TabsTrigger value="copyright" className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Copyright
            </TabsTrigger>
            <TabsTrigger value="caption" className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Captions
            </TabsTrigger>
          </TabsList>

          {/* Beat Analyzer Tab */}
          <TabsContent value="analyzer" className="space-y-6">
            <div className="bg-card rounded-lg border border-border p-6 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-white">
                  Upload Beat Audio
                </label>
                <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-purple-500 transition cursor-pointer">
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleAnalyzeFile}
                    className="hidden"
                    id="analyze-input"
                  />
                  <label htmlFor="analyze-input" className="cursor-pointer block">
                    <Zap className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm font-medium text-white">
                      {analyzeFile?.name || 'Click or drag audio file here'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">MP3, WAV, FLAC supported</p>
                  </label>
                </div>
              </div>

              <Button
                onClick={handleAnalyzeBeat}
                disabled={analyzing || !analyzeFile}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    Analyze Audio Quality
                  </>
                )}
              </Button>

              {/* Analysis Results */}
              {analysisResult && analysisResult.success && (
                <div className="bg-gradient-to-br from-purple-500/10 to-cyan-500/10 rounded-lg border border-purple-500/30 p-6 space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-400">Quality Level</p>
                      <p className={`text-lg font-bold capitalize px-3 py-1 rounded ${
                        analysisResult.quality_level === 'excellent'
                          ? 'text-green-400'
                          : analysisResult.quality_level === 'good'
                          ? 'text-blue-400'
                          : 'text-yellow-400'
                      }`}>
                        {analysisResult.quality_level}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Confidence</p>
                      <p className="text-lg font-bold text-cyan-400">
                        {(analysisResult.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-gray-800/50 rounded p-3">
                      <p className="text-gray-400">Loudness</p>
                      <p className="text-white font-mono">{analysisResult.loudness_db.toFixed(1)} dB</p>
                    </div>
                    <div className="bg-gray-800/50 rounded p-3">
                      <p className="text-gray-400">Dynamic Range</p>
                      <p className="text-white font-mono">{analysisResult.dynamic_range_db.toFixed(1)} dB</p>
                    </div>
                    <div className="bg-gray-800/50 rounded p-3">
                      <p className="text-gray-400">SNR</p>
                      <p className="text-white font-mono">{analysisResult.signal_to_noise_ratio.toFixed(1)} dB</p>
                    </div>
                    <div className="bg-gray-800/50 rounded p-3">
                      <p className="text-gray-400">Clipping</p>
                      <p className={`font-mono ${analysisResult.clipping_detected ? 'text-red-400' : 'text-green-400'}`}>
                        {analysisResult.clipping_detected ? 'Detected' : 'None'}
                      </p>
                    </div>
                  </div>

                  {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-white mb-2">Recommendations:</p>
                      <ul className="space-y-1 text-sm text-gray-300">
                        {analysisResult.recommendations.map((rec: string, i: number) => (
                          <li key={i} className="flex gap-2">
                            <span className="text-purple-400">•</span>
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </TabsContent>

          {/* Copyright Scanner Tab */}
          <TabsContent value="copyright" className="space-y-6">
            <div className="bg-card rounded-lg border border-border p-6 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-white">
                  Upload Beat for Copyright Scan
                </label>
                <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-blue-500 transition cursor-pointer">
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={handleCopyrightFile}
                    className="hidden"
                    id="copyright-input"
                  />
                  <label htmlFor="copyright-input" className="cursor-pointer block">
                    <Shield className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm font-medium text-white">
                      {copyrightFile?.name || 'Click or drag audio file here'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Checks for similar content</p>
                  </label>
                </div>
              </div>

              <Button
                onClick={handleScanCopyright}
                disabled={scanningCopyright || !copyrightFile}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {scanningCopyright ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Scanning...
                  </>
                ) : (
                  <>
                    <Shield className="w-4 h-4 mr-2" />
                    Scan for Copyright Issues
                  </>
                )}
              </Button>

              {/* Copyright Results */}
              {copyrightResult && copyrightResult.success && (
                <div className={`rounded-lg border p-6 space-y-4 ${getRiskLevelColor(copyrightResult.risk_level).split(' ')[0] === 'text-green-500' ? 'bg-green-500/10 border-green-500/30' : getRiskLevelColor(copyrightResult.risk_level).split(' ')[0] === 'text-red-500' ? 'bg-red-500/10 border-red-500/30' : 'bg-yellow-500/10 border-yellow-500/30'}`}>
                  <div className="flex items-center gap-3">
                    <AlertCircle className={`w-6 h-6 ${getRiskLevelColor(copyrightResult.risk_level).split(' ')[0]}`} />
                    <div>
                      <p className="text-sm text-gray-400">Risk Level</p>
                      <p className={`text-lg font-bold capitalize ${getRiskLevelColor(copyrightResult.risk_level).split(' ')[0]}`}>
                        {copyrightResult.risk_level}
                      </p>
                    </div>
                    <div className="ml-auto text-right">
                      <p className="text-sm text-gray-400">Original Content</p>
                      <p className={`text-lg font-bold ${copyrightResult.is_original ? 'text-green-400' : 'text-red-400'}`}>
                        {copyrightResult.is_original ? '✓ Yes' : '✗ No'}
                      </p>
                    </div>
                  </div>

                  {copyrightResult.matches && copyrightResult.matches.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-white">Matches Found:</p>
                      {copyrightResult.matches.map((match: any, i: number) => (
                        <div key={i} className="bg-gray-800/50 rounded p-3 text-sm">
                          <p className="font-medium text-white">{match.beat_title}</p>
                          <p className="text-gray-400">
                            Similarity: {(match.similarity_score * 100).toFixed(0)}%
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  {copyrightResult.recommendations && copyrightResult.recommendations.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-white mb-2">Recommendations:</p>
                      <ul className="space-y-1 text-sm text-gray-300">
                        {copyrightResult.recommendations.map((rec: string, i: number) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </TabsContent>

          {/* Caption Generator Tab */}
          <TabsContent value="caption" className="space-y-6">
            <div className="bg-card rounded-lg border border-border p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-white">Beat Title</label>
                  <input
                    type="text"
                    value={captionData.beat_title}
                    onChange={(e) =>
                      setCaptionData({ ...captionData, beat_title: e.target.value })
                    }
                    placeholder="e.g., Smooth Vibes"
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-white">Genre</label>
                  <select
                    value={captionData.beat_genre}
                    onChange={(e) =>
                      setCaptionData({ ...captionData, beat_genre: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-purple-500"
                  >
                    <option>Afrobeat</option>
                    <option>Trap</option>
                    <option>Drill</option>
                    <option>Hip Hop</option>
                    <option>R&B</option>
                    <option>Electronic</option>
                    <option>Lo-Fi</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-white">Mood</label>
                  <select
                    value={captionData.beat_mood}
                    onChange={(e) =>
                      setCaptionData({ ...captionData, beat_mood: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-purple-500"
                  >
                    <option>energetic</option>
                    <option>chill</option>
                    <option>dark</option>
                    <option>happy</option>
                    <option>melancholic</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-white">BPM</label>
                  <input
                    type="number"
                    value={captionData.bpm}
                    onChange={(e) =>
                      setCaptionData({ ...captionData, bpm: parseFloat(e.target.value) })
                    }
                    min="40"
                    max="200"
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-white">Tone</label>
                  <select
                    value={captionData.tone}
                    onChange={(e) =>
                      setCaptionData({ ...captionData, tone: e.target.value })
                    }
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="hype">Hype</option>
                    <option value="poetic">Poetic</option>
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-white">Platform</label>
                <select
                  value={captionData.platform}
                  onChange={(e) =>
                    setCaptionData({ ...captionData, platform: e.target.value })
                  }
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="twitter">Twitter</option>
                  <option value="instagram">Instagram</option>
                  <option value="tiktok">TikTok</option>
                  <option value="facebook">Facebook</option>
                  <option value="youtube">YouTube</option>
                </select>
              </div>

              <Button
                onClick={handleGenerateCaption}
                disabled={generatingCaption || !captionData.beat_title}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {generatingCaption ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Generate Caption
                  </>
                )}
              </Button>

              {/* Caption Results */}
              {captionResult && captionResult.success && (
                <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-lg border border-green-500/30 p-6 space-y-4">
                  <div className="space-y-2">
                    <p className="text-sm text-gray-400">Generated Caption</p>
                    <div className="bg-gray-900/50 rounded p-4 border border-gray-700">
                      <p className="text-white whitespace-pre-wrap">{captionResult.content}</p>
                    </div>
                  </div>

                  {captionResult.hashtags && captionResult.hashtags.length > 0 && (
                    <div>
                      <p className="text-sm text-gray-400 mb-2">Hashtags:</p>
                      <div className="flex flex-wrap gap-2">
                        {captionResult.hashtags.map((tag: string, i: number) => (
                          <span
                            key={i}
                            className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-sm"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <p className="text-gray-400">Characters</p>
                      <p className="text-white font-mono">{captionResult.character_count}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-400">Words</p>
                      <p className="text-white font-mono">{captionResult.word_count}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-400">Confidence</p>
                      <p className="text-white font-mono">
                        {(captionResult.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>

                  <Button
                    onClick={() => {
                      navigator.clipboard.writeText(captionResult.content);
                      toast({
                        title: 'Copied!',
                        description: 'Caption copied to clipboard',
                        variant: 'success',
                      });
                    }}
                    variant="outline"
                    className="w-full"
                  >
                    Copy Caption
                  </Button>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
