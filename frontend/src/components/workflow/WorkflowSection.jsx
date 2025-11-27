import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Calendar, Sparkles, Download, Presentation, RotateCcw } from 'lucide-react';

const workflowSteps = [
  {
    number: 1,
    title: 'Plan Week',
    description: 'On Sunday, Ms. Li plans next week\'s maths concepts',
    icon: Calendar,
    color: 'from-blue-500 to-blue-600',
    bgColor: 'bg-blue-50',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    number: 2,
    title: 'Generate Micro-Videos',
    description: 'She uses UnboundEd to create 2–3 short explanation videos per topic',
    icon: Sparkles,
    color: 'from-purple-500 to-purple-600',
    bgColor: 'bg-purple-50',
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600'
  },
  {
    number: 3,
    title: 'Download Once',
    description: 'She downloads them when internet is available at school or at home',
    icon: Download,
    color: 'from-green-500 to-green-600',
    bgColor: 'bg-green-50',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  },
  {
    number: 4,
    title: 'Teach Offline',
    description: 'She shows them in class using a laptop + projector, no streaming needed',
    icon: Presentation,
    color: 'from-orange-500 to-orange-600',
    bgColor: 'bg-orange-50',
    iconBg: 'bg-orange-100',
    iconColor: 'text-orange-600'
  },
  {
    number: 5,
    title: 'Reuse for Revision',
    description: 'She replays them before tests and shares them via USB/Bluetooth if needed',
    icon: RotateCcw,
    color: 'from-pink-500 to-pink-600',
    bgColor: 'bg-pink-50',
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600'
  }
];

export default function WorkflowSection() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight mb-3">
          How this fits into a teacher's week
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          A seamless workflow designed for real classroom constraints
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {workflowSteps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <Card 
              key={step.number}
              className={`${step.bgColor} border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 relative overflow-hidden group`}
            >
              {/* Gradient overlay on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${step.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
              
              <CardContent className="p-6 relative">
                <div className="flex items-start gap-4 mb-4">
                  <div className={`flex-shrink-0 w-12 h-12 rounded-xl ${step.iconBg} flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className={`w-6 h-6 ${step.iconColor}`} />
                  </div>
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br ${step.color} text-white text-sm font-bold flex items-center justify-center shadow-md`}>
                    {step.number}
                  </div>
                </div>
                
                <h3 className="text-lg font-bold text-gray-900 mb-2 tracking-tight">
                  {step.title}
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </CardContent>

              {/* Connection line for desktop */}
              {idx < workflowSteps.length - 1 && (
                <div className="hidden xl:block absolute top-1/2 -right-3 w-6 h-0.5 bg-gradient-to-r from-gray-300 to-transparent" />
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}