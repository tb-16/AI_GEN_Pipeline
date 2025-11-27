import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Globe, Users, Wifi, Heart } from 'lucide-react';

export default function AboutSection() {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 tracking-tight mb-3">
          About the Project
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          AI-powered education for low-connectivity environments
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-blue-50/40 hover:shadow-xl transition-shadow duration-300">
          <CardContent className="p-8">
            <div className="w-14 h-14 rounded-2xl bg-blue-100 flex items-center justify-center mb-4">
              <Globe className="w-7 h-7 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              Initial Focus
            </h3>
            <p className="text-gray-700 leading-relaxed">
              We're focusing on <strong>rural China and Vietnam</strong> as example contexts, where teachers face large class sizes (40+ students), unreliable internet connectivity, and limited devices.
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-lg border-0 bg-gradient-to-br from-white to-green-50/40 hover:shadow-xl transition-shadow duration-300">
          <CardContent className="p-8">
            <div className="w-14 h-14 rounded-2xl bg-green-100 flex items-center justify-center mb-4">
              <Heart className="w-7 h-7 text-green-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              Generalizable System
            </h3>
            <p className="text-gray-700 leading-relaxed">
              The system is designed to work across <strong>any subject</strong> (Maths, Science, Geography, etc.) and <strong>any low-connectivity region</strong> worldwide.
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-xl border-0 bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
        <CardContent className="p-8">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
                <Users className="w-8 h-8 text-white" />
              </div>
            </div>
            
            <div className="flex-1 space-y-4">
              <h3 className="text-2xl font-bold text-gray-900">
                The Challenge
              </h3>
              <p className="text-gray-700 leading-relaxed text-lg">
                Teachers in low-resource environments often lack access to quality instructional materials, reliable internet, and engaging visual content. They teach large classes with minimal technology support.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
                <div className="flex items-center gap-3 p-4 rounded-lg bg-white/60 backdrop-blur">
                  <Wifi className="w-5 h-5 text-indigo-600 flex-shrink-0" />
                  <span className="text-sm font-medium text-gray-700">Low connectivity</span>
                </div>
                <div className="flex items-center gap-3 p-4 rounded-lg bg-white/60 backdrop-blur">
                  <Users className="w-5 h-5 text-purple-600 flex-shrink-0" />
                  <span className="text-sm font-medium text-gray-700">Large class sizes</span>
                </div>
                <div className="flex items-center gap-3 p-4 rounded-lg bg-white/60 backdrop-blur">
                  <Globe className="w-5 h-5 text-pink-600 flex-shrink-0" />
                  <span className="text-sm font-medium text-gray-700">Limited resources</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-white/50">
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              Our Solution
            </h3>
            <p className="text-gray-700 leading-relaxed text-lg">
              UnboundEd empowers teachers to create custom, curriculum-aligned micro-videos that can be <strong>downloaded once and used offline</strong>. No streaming required. Teachers can reuse these videos throughout the term, share them via USB or Bluetooth, and adapt them for different class levels.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}