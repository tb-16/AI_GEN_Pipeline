import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GraduationCap, Sparkles, Workflow, Info, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import TeacherContextForm from '../components/lesson/TeacherContextForm';
import WorkflowSection from '../components/workflow/WorkflowSection';
import AboutSection from '../components/about/AboutSection';
import { generatePipelineVideo, listVideos, clearVideos, BACKEND_URL } from '@/api/pipeline';

export default function Home() {
  const [activeTab, setActiveTab] = useState('builder');
  const [isGenerating, setIsGenerating] = useState(false);
  const [lastGenerationResult, setLastGenerationResult] = useState(null);
  const [previousVideos, setPreviousVideos] = useState([]);
  const [downloadError, setDownloadError] = useState(null);
  const [clearError, setClearError] = useState(null);
  const [clearing, setClearing] = useState(false);

  // Fetch list of previously generated videos
  const fetchVideos = async () => {
    try {
      const data = await listVideos();
      setPreviousVideos(data.videos || []);
    } catch (error) {
      console.error('Failed to fetch videos:', error);
    }
  };

  // Load videos on mount and after each generation
  useEffect(() => {
    fetchVideos();
  }, []);

  useEffect(() => {
    if (lastGenerationResult?.status === 'completed') {
      fetchVideos();
    }
  }, [lastGenerationResult]);

  const handleDownloadVideo = async (video) => {
    try {
      setDownloadError(null);
      const response = await fetch(`${BACKEND_URL}${video.url}`);
      if (!response.ok) {
        throw new Error(`Download failed (${response.status})`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = video.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading video:', error);
      setDownloadError(error.message || 'Failed to download video');
    }
  };

  const handleGenerateLessonPlan = async (formPayload) => {
    setIsGenerating(true);
    setLastGenerationResult(null);

    try {
      const result = await generatePipelineVideo({
        lessonRequest: formPayload.lessonRequest,
        numScenes: formPayload.numScenes,
        graphProportion: formPayload.graphProportion,
        outputFilename: formPayload.outputFilename,
      });
      setLastGenerationResult(result);
    } catch (error) {
      console.error('Error generating video pipeline:', error);
      setLastGenerationResult({ status: 'failed', error: error.message });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClearVideos = async () => {
    try {
      setClearing(true);
      setClearError(null);
      await clearVideos();
      setPreviousVideos([]);
      setLastGenerationResult(null);
    } catch (error) {
      console.error('Failed to clear videos:', error);
      setClearError(error.message || 'Failed to clear videos');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/40">
      {/* Hero Header */}
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-sm flex items-center justify-center">
              <GraduationCap className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-4xl font-bold tracking-tight">
                UnboundEd
              </h1>
              <p className="text-blue-100 text-lg mt-1">
                AI micro-lessons for low-connectivity classrooms
              </p>
            </div>
          </div>
          <p className="text-white/90 text-base max-w-3xl leading-relaxed">
            Empower teachers in low-resource environments to create engaging, curriculum-aligned video lessons that work offline. 
            No streaming required.
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b bg-white/60 backdrop-blur-md sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="bg-transparent border-0 h-14">
              <TabsTrigger 
                value="builder" 
                className="data-[state=active]:bg-white data-[state=active]:shadow-sm gap-2 text-base"
              >
                <Sparkles className="w-4 h-4" />
                Lesson Builder
              </TabsTrigger>
              <TabsTrigger 
                value="workflow" 
                className="data-[state=active]:bg-white data-[state=active]:shadow-sm gap-2 text-base"
              >
                <Workflow className="w-4 h-4" />
                Teacher Workflow
              </TabsTrigger>
              <TabsTrigger 
                value="about" 
                className="data-[state=active]:bg-white data-[state=active]:shadow-sm gap-2 text-base"
              >
                <Info className="w-4 h-4" />
                About
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} className="w-full">
          <TabsContent value="builder" className="mt-0 space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left Column: Form */}
              <div>
                <TeacherContextForm 
                  onGenerate={handleGenerateLessonPlan}
                  isLoading={isGenerating}
                />
              </div>

              {/* Right Column: Video Player & Status */}
              <div className="space-y-6">
                {/* Latest Video Player */}
                {lastGenerationResult?.status === 'completed' && lastGenerationResult.videoUrl && (
                  <Card className="p-6 shadow-lg">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">
                      Latest Generated Video
                    </h3>
                    <video
                      className="w-full rounded-lg border border-gray-200 bg-black mb-4"
                      controls
                      src={`${BACKEND_URL}${lastGenerationResult.videoUrl}`}
                    >
                      Your browser does not support the video tag.
                    </video>
                    <div className="space-y-2 text-sm text-gray-600">
                      {lastGenerationResult.finalVideoPath && (
                        <p className="break-all">
                          <span className="font-medium">Saved at:</span> {lastGenerationResult.finalVideoPath}
                        </p>
                      )}
                      {typeof lastGenerationResult.elapsedTime === 'number' && (
                        <p>
                          <span className="font-medium">Time taken:</span> {lastGenerationResult.elapsedTime.toFixed(1)}s
                        </p>
                      )}
                    </div>
                  </Card>
                )}

                {/* Status / Placeholder */}
                {!lastGenerationResult && (
                  <div className="min-h-[220px] flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-200 bg-white/70 p-6 text-center text-gray-600">
                    <Sparkles className="w-10 h-10 text-blue-500 mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      Video generation
                    </h3>
                    <p className="text-sm leading-relaxed max-w-sm">
                      Fill in the teacher context form and click
                      {' '}
                      <span className="font-semibold">Generate Lesson Plan & Script</span>
                      {' '}
                      to start the backend pipeline. Your video will appear here.
                    </p>
                  </div>
                )}

                {lastGenerationResult?.status === 'failed' && (
                  <Card className="p-6 shadow-lg bg-red-50">
                    <p className="text-sm text-red-600">
                      Failed to generate video: {lastGenerationResult.error}
                    </p>
                  </Card>
                )}

                {/* Previous Videos List */}
                {previousVideos.length > 0 && (
                  <Card className="p-6 shadow-lg">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-gray-900">
                        Previously Generated Videos
                      </h3>
                      <Button
                        variant="destructive"
                        size="sm"
                        disabled={clearing}
                        onClick={handleClearVideos}
                        className="gap-2"
                      >
                        {clearing ? 'Clearing...' : 'Clear All'}
                      </Button>
                    </div>
                    <div className="space-y-3">
                      {previousVideos.map((video) => (
                        <div
                          key={video.filename}
                          className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                        >
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {video.filename}
                            </p>
                            <p className="text-xs text-gray-500">
                              {new Date(video.created * 1000).toLocaleString()} • {(video.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        <Button
                          size="sm"
                          variant="outline"
                          className="gap-2 ml-4"
                          onClick={() => handleDownloadVideo(video)}
                        >
                          <Download className="w-4 h-4" />
                          Download
                        </Button>
                        </div>
                      ))}
                    {downloadError && (
                      <p className="text-xs text-red-600">
                        {downloadError}
                      </p>
                    )}
                    </div>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="workflow" className="mt-0">
            <div className="py-8">
              <WorkflowSection />
            </div>
          </TabsContent>

          <TabsContent value="about" className="mt-0">
            <div className="py-8">
              <AboutSection />
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Footer */}
      <div className="border-t bg-white/60 backdrop-blur-sm mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-gray-600">
            <p className="mb-2">
              <strong>UnboundEd</strong> • AI for Education in Low-Resource Environments
            </p>
            <p className="text-gray-500">
              Hackathon Demo • Mock AI Integration
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
