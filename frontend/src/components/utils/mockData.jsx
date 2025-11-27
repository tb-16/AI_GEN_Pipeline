// Mock lesson plan generator
export function generateLessonPlan(formData) {
  const { country, subject, level, topic, classSize, connectivity, graphFrequency, videoLength } = formData;
  const frequencyLabel = graphFrequency ?? connectivity ?? 'Few';

  // Different templates based on subject and country
  const templates = {
    Maths: {
      China: {
        lessonGoal: `Help students understand ${topic} through visual examples and step-by-step problem solving, designed for Gaokao preparation standards`,
        keyPoints: [
          'Build foundational understanding through concrete examples',
          'Connect concepts to real-world applications',
          'Practice problem-solving strategies step-by-step',
          'Review common mistakes and misconceptions',
          'Prepare for exam-style questions'
        ],
        segments: [
          {
            segmentTitle: `What is ${topic}?`,
            spokenText: `Today we'll explore ${topic}. Let's start with a simple definition and see why this concept is important in mathematics. This builds on what you already know about equations and relationships.`,
            visualInstruction: 'Show animated diagram introducing the concept with clear labels and step-by-step reveal',
            estimatedDuration: Math.min(videoLength, 50)
          },
          {
            segmentTitle: 'Worked Example',
            spokenText: `Let's work through a complete example together. Watch carefully as I solve this problem step by step. Notice how each step connects to the previous one.`,
            visualInstruction: 'Screen recording of problem being solved with annotations, highlighting each calculation step',
            estimatedDuration: Math.min(videoLength + 5, 60)
          },
          {
            segmentTitle: 'Common Mistakes',
            spokenText: `Many students make these common errors when working with ${topic}. Let's identify them so you can avoid these pitfalls in your homework and exams.`,
            visualInstruction: 'Split-screen showing incorrect vs correct approaches, with red X and green checkmark',
            estimatedDuration: Math.min(videoLength - 5, 40)
          }
        ]
      },
      Vietnam: {
        lessonGoal: `Introduce ${topic} with clear visual demonstrations suitable for Vietnamese curriculum standards and large classroom settings`,
        keyPoints: [
          'Start with familiar everyday examples students can relate to',
          'Use visual models to represent abstract concepts',
          'Practice with graduated difficulty levels',
          'Connect to national curriculum learning objectives'
        ],
        segments: [
          {
            segmentTitle: `Introduction to ${topic}`,
            spokenText: `Chúng ta sẽ học về ${topic} hôm nay. We'll start with something you see every day and build up to the mathematical concept.`,
            visualInstruction: 'Show real-world Vietnamese context (market, school, home) transitioning to mathematical representation',
            estimatedDuration: Math.min(videoLength, 45)
          },
          {
            segmentTitle: 'Visual Explanation',
            spokenText: `Let's see how this works with a clear visual model. Pay attention to how the parts relate to each other.`,
            visualInstruction: 'Animated diagram with Vietnamese labels, building complexity gradually',
            estimatedDuration: Math.min(videoLength, 50)
          },
          {
            segmentTitle: 'Practice Together',
            spokenText: `Now try to think along with me as we solve this example. What would you do first?`,
            visualInstruction: 'Interactive-style problem with pauses, showing solution steps one at a time',
            estimatedDuration: Math.min(videoLength - 5, 45)
          }
        ]
      },
      Other: {
        lessonGoal: `Introduce students to ${topic} with engaging visuals and clear explanations suitable for ${level}`,
        keyPoints: [
          'Introduce the concept with familiar examples',
          'Break down complex ideas into simple steps',
          'Provide visual representations for better understanding',
          'Include practice opportunities'
        ],
        segments: [
          {
            segmentTitle: `Understanding ${topic}`,
            spokenText: `Let's explore ${topic} together. We'll start simple and build your understanding step by step.`,
            visualInstruction: 'Clean animated introduction with labeled diagrams',
            estimatedDuration: Math.min(videoLength, 45)
          },
          {
            segmentTitle: 'Step-by-Step Example',
            spokenText: `Watch as I work through this example. Notice the strategy I use at each step.`,
            visualInstruction: 'Screen-recorded solution with voice-over and annotations',
            estimatedDuration: Math.min(videoLength, 50)
          }
        ]
      }
    },
    Geography: {
      China: {
        lessonGoal: `Explore ${topic} with focus on regional Chinese examples and environmental awareness`,
        keyPoints: [
          'Understand the geographical concepts and processes',
          'Examine case studies from China and surrounding regions',
          'Analyze human-environment interactions',
          'Connect to sustainable development goals'
        ],
        segments: [
          {
            segmentTitle: `What causes ${topic}?`,
            spokenText: `Understanding ${topic} helps us see how physical geography affects our lives. Let's look at the processes involved.`,
            visualInstruction: 'Show map animations of China/Asia with the geographical process highlighted',
            estimatedDuration: Math.min(videoLength, 48)
          },
          {
            segmentTitle: 'Case Study: China',
            spokenText: `Let's examine a real example from China. Notice how geography, climate, and human activity all play a role.`,
            visualInstruction: 'Satellite imagery and diagrams of Chinese location showing the phenomenon',
            estimatedDuration: Math.min(videoLength + 5, 55)
          },
          {
            segmentTitle: 'Impacts and Solutions',
            spokenText: `What are the effects on people and environment? What can we do about it? These are important questions for our future.`,
            visualInstruction: 'Split screen showing problems and solutions with icons and data',
            estimatedDuration: Math.min(videoLength, 45)
          }
        ]
      },
      Vietnam: {
        lessonGoal: `Study ${topic} through Vietnamese examples and regional geography, emphasizing local environmental challenges`,
        keyPoints: [
          'Identify key geographical features and processes',
          'Study Vietnamese case examples (Mekong Delta, Central Highlands, etc.)',
          'Understand impacts on local communities',
          'Consider adaptation and mitigation strategies'
        ],
        segments: [
          {
            segmentTitle: `Geography of ${topic}`,
            spokenText: `Vietnam's unique geography makes ${topic} particularly important here. Let's explore why.`,
            visualInstruction: 'Map of Vietnam highlighting relevant regions, rivers, or features',
            estimatedDuration: Math.min(videoLength, 50)
          },
          {
            segmentTitle: 'Mekong Delta Case Study',
            spokenText: `The Mekong Delta shows us a clear example. Let's look at the causes, effects, and what people are doing.`,
            visualInstruction: 'Satellite images and local photos of Mekong Delta with annotations',
            estimatedDuration: Math.min(videoLength + 5, 55)
          },
          {
            segmentTitle: 'Local Responses',
            spokenText: `Vietnamese communities and government are taking action. Here's what's being done and why it matters.`,
            visualInstruction: 'Photos and diagrams of adaptation measures with simple labels',
            estimatedDuration: Math.min(videoLength - 5, 42)
          }
        ]
      },
      Other: {
        lessonGoal: `Understand ${topic} through clear geographical examples and analysis`,
        keyPoints: [
          'Define key geographical terms and concepts',
          'Examine real-world case studies',
          'Analyze causes and effects',
          'Consider sustainable solutions'
        ],
        segments: [
          {
            segmentTitle: `Introduction to ${topic}`,
            spokenText: `Let's explore ${topic} and understand the geographical processes involved.`,
            visualInstruction: 'World map with highlighted regions showing the phenomenon',
            estimatedDuration: Math.min(videoLength, 45)
          },
          {
            segmentTitle: 'Case Study Analysis',
            spokenText: `Looking at a real example helps us understand the concepts better. Let's analyze what's happening.`,
            visualInstruction: 'Satellite imagery and diagrams with clear annotations',
            estimatedDuration: Math.min(videoLength, 50)
          }
        ]
      }
    },
    Science: {
      China: {
        lessonGoal: `Explain ${topic} through demonstrations and experiments aligned with Chinese science curriculum`,
        keyPoints: [
          'Observe and understand the scientific principle',
          'See practical demonstrations and real-world applications',
          'Learn the scientific method and inquiry process',
          'Connect to exam requirements and key knowledge points'
        ],
        segments: [
          {
            segmentTitle: `The Science of ${topic}`,
            spokenText: `Today we'll discover ${topic}. Science helps us understand how the world works. Let's investigate together.`,
            visualInstruction: 'Show animated scientific diagram or process with labeled parts',
            estimatedDuration: Math.min(videoLength, 48)
          },
          {
            segmentTitle: 'Demonstration',
            spokenText: `Watch this demonstration carefully. Notice what happens at each stage and think about why.`,
            visualInstruction: 'Video of simple experiment or simulation showing the scientific concept clearly',
            estimatedDuration: Math.min(videoLength + 5, 55)
          },
          {
            segmentTitle: 'Real-World Applications',
            spokenText: `Where do we see ${topic} in everyday life? Understanding this helps you remember and use the science.`,
            visualInstruction: 'Photos and clips of real-world examples with captions',
            estimatedDuration: Math.min(videoLength - 5, 40)
          }
        ]
      },
      default: {
        lessonGoal: `Learn ${topic} through visual demonstrations and clear scientific explanations`,
        keyPoints: [
          'Understand the core scientific principle',
          'Observe demonstrations and examples',
          'Connect to real-world applications',
          'Build scientific thinking skills'
        ],
        segments: [
          {
            segmentTitle: `Understanding ${topic}`,
            spokenText: `Let's explore the science behind ${topic}. We'll break it down into simple parts you can understand.`,
            visualInstruction: 'Clear scientific diagram with animations showing the process',
            estimatedDuration: Math.min(videoLength, 45)
          },
          {
            segmentTitle: 'Visual Demonstration',
            spokenText: `Seeing is believing in science. Watch this demonstration and think about what's happening.`,
            visualInstruction: 'Video demonstration or simulation with slow-motion and labels',
            estimatedDuration: Math.min(videoLength, 50)
          }
        ]
      }
    }
  };

  // Select appropriate template
  const subjectTemplates = templates[subject] || templates.Science;
  const template = subjectTemplates[country] || subjectTemplates.default || subjectTemplates.Other;

  return {
    lessonGoal: template.lessonGoal,
    targetLevel: level,
    context: `${country} • ${classSize} students • ${frequencyLabel} graph frequency`,
    keyPoints: template.keyPoints,
    segments: template.segments
  };
}

// Mock video generation
export function generateVideo(segment, segmentIndex) {
  return new Promise((resolve) => {
    // Simulate API call delay
    setTimeout(() => {
      resolve({
        videoId: `vid_${Date.now()}_${segmentIndex}`,
        segmentTitle: segment.segmentTitle,
        previewUrl: '/placeholder-video.mp4', // In real app, this would be actual video URL
        fileSizeMB: (8 + Math.random() * 4).toFixed(1), // Random size between 8-12 MB
        durationSeconds: segment.estimatedDuration,
        offlineReady: true
      });
    }, 1500 + Math.random() * 1000); // 1.5-2.5 second delay
  });
}