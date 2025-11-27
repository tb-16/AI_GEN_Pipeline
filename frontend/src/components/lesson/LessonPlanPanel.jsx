import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Target, Globe, TrendingUp, CheckCircle } from 'lucide-react';
import VideoSegmentCard from './VideoSegmentCard';

export default function LessonPlanPanel({ lessonPlan, onGenerateVideo, generatedVideos, isGenerating }) {
  if (!lessonPlan) return null;

  return (
    <div className="space-y-6">
      {/* Lesson Overview */}
      <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-green-50/30">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <CardTitle className="text-2xl font-bold tracking-tight text-gray-900">
              Lesson Overview
            </CardTitle>
            <Badge className="bg-green-100 text-green-800 border-green-200 px-3 py-1">
              <CheckCircle className="w-3 h-3 mr-1" />
              Generated
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3 p-4 rounded-lg bg-white/60 backdrop-blur">
              <div className="p-2 rounded-lg bg-blue-100">
                <Target className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                  Lesson Goal
                </p>
                <p className="text-sm text-gray-900 leading-relaxed">
                  {lessonPlan.lessonGoal}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 rounded-lg bg-white/60 backdrop-blur">
              <div className="p-2 rounded-lg bg-indigo-100">
                <TrendingUp className="w-5 h-5 text-indigo-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                  Target Level
                </p>
                <p className="text-sm text-gray-900 leading-relaxed">
                  {lessonPlan.targetLevel}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-4 rounded-lg bg-white/60 backdrop-blur">
              <div className="p-2 rounded-lg bg-green-100">
                <Globe className="w-5 h-5 text-green-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
                  Context
                </p>
                <p className="text-sm text-gray-900 leading-relaxed">
                  {lessonPlan.context}
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-3">
              Key Points
            </h3>
            <ul className="space-y-2">
              {lessonPlan.keyPoints.map((point, idx) => (
                <li key={idx} className="flex items-start gap-3 text-gray-700">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold flex items-center justify-center mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="text-sm leading-relaxed">{point}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Micro-Video Segments */}
      <div>
        <div className="mb-4">
          <h2 className="text-xl font-bold text-gray-900 tracking-tight">
            Micro-Video Segments
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Generate short, offline-ready videos for each concept
          </p>
        </div>
        
        <div className="space-y-4">
          {lessonPlan.segments.map((segment, idx) => (
            <VideoSegmentCard
              key={idx}
              segment={segment}
              segmentIndex={idx}
              onGenerate={() => onGenerateVideo(segment, idx)}
              generatedVideo={generatedVideos[idx]}
              isGenerating={isGenerating === idx}
            />
          ))}
        </div>
      </div>
    </div>
  );
}