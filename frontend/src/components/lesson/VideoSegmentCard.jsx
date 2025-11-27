import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Play, Download, Video, Clock, HardDrive, Image, Wifi } from 'lucide-react';

export default function VideoSegmentCard({ segment, segmentIndex, onGenerate, generatedVideo, isGenerating }) {
  return (
    <Card className="shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="flex-shrink-0 w-7 h-7 rounded-full bg-indigo-100 text-indigo-700 text-sm font-bold flex items-center justify-center">
                {segmentIndex + 1}
              </span>
              <CardTitle className="text-lg font-semibold text-gray-900">
                {segment.segmentTitle}
              </CardTitle>
            </div>
            <Badge variant="outline" className="text-xs">
              <Clock className="w-3 h-3 mr-1" />
              ~{segment.estimatedDuration}s
            </Badge>
          </div>
          
          {!generatedVideo && (
            <Button
              onClick={onGenerate}
              disabled={isGenerating}
              size="sm"
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md"
            >
              {isGenerating ? (
                <>
                  <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Generating...
                </>
              ) : (
                <>
                  <Video className="w-4 h-4 mr-2" />
                  Generate Video
                </>
              )}
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
              Spoken Text
            </h4>
            <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-lg">
              {segment.spokenText}
            </p>
          </div>
          
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
              <Image className="w-3.5 h-3.5" />
              Visual Instruction
            </h4>
            <p className="text-sm text-gray-600 italic bg-blue-50 p-3 rounded-lg">
              {segment.visualInstruction}
            </p>
          </div>
        </div>

        {/* Generated Video Preview */}
        {generatedVideo && (
          <div className="mt-4 p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border-2 border-green-200">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                  <Play className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">
                    Video Ready
                  </p>
                  <p className="text-xs text-gray-600">
                    {generatedVideo.durationSeconds}s • {generatedVideo.fileSizeMB} MB
                  </p>
                </div>
              </div>
              
              <Badge className="bg-green-600 text-white border-0 shadow-sm">
                <Wifi className="w-3 h-3 mr-1" />
                Offline-ready
              </Badge>
            </div>

            <div className="bg-gray-900 rounded-lg aspect-video flex items-center justify-center mb-3 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-purple-600/20" />
              <div className="relative z-10 text-center">
                <Play className="w-12 h-12 text-white/80 mx-auto mb-2" />
                <p className="text-xs text-white/70">Video Preview</p>
                <p className="text-xs text-white/50 mt-1">{generatedVideo.segmentTitle}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                className="flex-1 bg-white hover:bg-gray-50 border-green-300"
              >
                <Play className="w-3.5 h-3.5 mr-2" />
                Preview
              </Button>
              <Button
                size="sm"
                className="flex-1 bg-green-600 hover:bg-green-700 text-white"
              >
                <Download className="w-3.5 h-3.5 mr-2" />
                Download
              </Button>
            </div>

            <div className="mt-3 flex items-center gap-2 text-xs text-gray-600">
              <HardDrive className="w-3.5 h-3.5" />
              <span>Optimized for low-bandwidth sharing</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}