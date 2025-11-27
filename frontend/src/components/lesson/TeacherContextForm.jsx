import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles } from 'lucide-react';

const SCENE_DURATION_SECONDS = 6;
const MIN_SEGMENT_DURATION_SECONDS = 24; // 4 scenes
const MAX_SEGMENT_DURATION_SECONDS = 60; // 10 scenes
const SEGMENT_DURATION_STEP = 6;

const GRAPH_PROPORTION_BY_FREQUENCY = {
  None: 0,
  Few: 0.2,
  Moderate: 0.4,
  Many: 0.6,
  'Only Data': 1.0
};
const DEFAULT_GRAPH_FREQUENCY = 'Few';

const secondsToSceneCount = (seconds) => {
  if (!seconds) return 4;
  const estimatedScenes = Math.round(seconds / SCENE_DURATION_SECONDS);
  return Math.max(4, Math.min(10, estimatedScenes));
};

const graphProportionFromFrequency = (frequency) =>
  GRAPH_PROPORTION_BY_FREQUENCY[frequency] ?? GRAPH_PROPORTION_BY_FREQUENCY[DEFAULT_GRAPH_FREQUENCY];

const buildLessonRequest = ({ topic, subject, country, level }) => {
  const safeTopic = topic?.trim() || 'the topic';
  const location = country?.trim() ? ` in ${country.trim()}` : '';
  const subjectMention = subject?.trim() ? ` (${subject.trim()})` : '';
  return `Create a short educational video about ${safeTopic}${location}${subjectMention}. Make the lesson appropriate for a ${level} student.`;
};

export default function TeacherContextForm({ onGenerate, isLoading }) {
  const [formData, setFormData] = useState({
    country: 'China',
    subject: 'Maths',
    level: 'Lower Secondary',
    topic: '',
    outputFilename: 'output.mp4',
    graphFrequency: DEFAULT_GRAPH_FREQUENCY,
    videoLength: 36 // Default to 6 scenes (6s each)
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const numScenes = secondsToSceneCount(formData.videoLength);
    const graphProportion = graphProportionFromFrequency(formData.graphFrequency);
    const lessonRequest = buildLessonRequest(formData);
    onGenerate({
      ...formData,
      numScenes,
      graphProportion,
      lessonRequest,
      outputFilename: formData.outputFilename
    });
  };

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-blue-50/30">
      <CardHeader className="space-y-1 pb-6">
        <CardTitle className="text-2xl font-bold tracking-tight text-gray-900">
          Teacher Context
        </CardTitle>
        <CardDescription className="text-base text-gray-600">
          Tell us about your classroom and we'll create a customized micro-lesson plan about your countries enviorment.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="country" className="text-sm font-medium text-gray-700">
                Country / Region
              </Label>
              <Input
                id="country"
                value={formData.country}
                onChange={(e) => updateField('country', e.target.value)}
                placeholder="Type a country or region (e.g., rural China, Lagos, East Africa)"
                className="h-11 bg-white"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="subject" className="text-sm font-medium text-gray-700">
                Subject
              </Label>
              <Input
                id="subject"
                value={formData.subject}
                onChange={(e) => updateField('subject', e.target.value)}
                placeholder="Type the subject you would like to cover (e.g., Maths, Science, Geography)"
                className="h-11 bg-white"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="level" className="text-sm font-medium text-gray-700">
                Level
              </Label>
              <Select value={formData.level} onValueChange={(val) => updateField('level', val)}>
                <SelectTrigger id="level" className="h-11 bg-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Lower Secondary">Lower Secondary</SelectItem>
                  <SelectItem value="Upper Secondary">Upper Secondary</SelectItem>
                  <SelectItem value="Pre-GCSE">Pre-GCSE</SelectItem>
                  <SelectItem value="A-Level / Gaokao Prep">A-Level / Gaokao Prep</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="graphFrequency" className="text-sm font-medium text-gray-700">
                Graph frequency
              </Label>
              <Select
                value={formData.graphFrequency}
                onValueChange={(val) => updateField('graphFrequency', val)}
              >
                <SelectTrigger id="graphFrequency" className="h-11 bg-white">
                  <SelectValue placeholder="Select graph frequency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="None">None</SelectItem>
                  <SelectItem value="Few">Few</SelectItem>
                  <SelectItem value="Moderate">Moderate</SelectItem>
                  <SelectItem value="Many">Many</SelectItem>
                  <SelectItem value="Only Data">Only Data</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="topic" className="text-sm font-medium text-gray-700">
              Topic / Concept
            </Label>
            <Input
              id="topic"
              value={formData.topic}
              onChange={(e) => updateField('topic', e.target.value)}
              placeholder="e.g., Introduction to Functions or Climate Change & Flooding"
              className="h-11 bg-white"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="outputFilename" className="text-sm font-medium text-gray-700">
              Output File Name
            </Label>
            <Input
              id="outputFilename"
              type="text"
              value={formData.outputFilename}
              onChange={(e) => updateField('outputFilename', e.target.value)}
              placeholder="e.g., my_lesson_video.mp4"
              className="h-11 bg-white"
              required
            />
          </div>

          <div className="space-y-3">
            <Label htmlFor="videoLength" className="text-sm font-medium text-gray-700">
              Preferred Video Length per Segment: {formData.videoLength} seconds (~{secondsToSceneCount(formData.videoLength)} scenes)
            </Label>
            <Slider
              id="videoLength"
              value={[formData.videoLength]}
              onValueChange={(val) => updateField(
                'videoLength',
                val?.[0] ?? MIN_SEGMENT_DURATION_SECONDS
              )}
              min={MIN_SEGMENT_DURATION_SECONDS}
              max={MAX_SEGMENT_DURATION_SECONDS}
              step={SEGMENT_DURATION_STEP}
              aria-valuetext={`${formData.videoLength} seconds, ${secondsToSceneCount(formData.videoLength)} scenes`}
              className="py-2"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>24s • 4 scenes</span>
              <span>42s • 7 scenes</span>
              <span>60s • 10 scenes</span>
            </div>
            <p className="text-xs text-gray-500">
              Each scene is ~6 seconds. Use the slider to pick between 4 and 10 scenes per segment.
            </p>
          </div>

          <Button
            type="submit"
            disabled={isLoading || !formData.topic}
            className="w-full h-12 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium text-base shadow-lg hover:shadow-xl transition-all duration-200"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Generating Lesson Plan...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 mr-2" />
                Generate Lesson Plan & Script
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}