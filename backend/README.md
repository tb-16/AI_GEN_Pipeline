# VeoLab - Educational Video Generation Platform

Comprehensive platform for generating educational videos using OpenAI's Sora API and Our World in Data visualizations. Features an automated pipeline that converts lesson requests into complete educational videos with AI-generated scenes and data visualizations.

## Features

### Core Video Generation
- ✅ Generate single 12-second video clips with Sora
- ✅ Generate multiple clips from a list of prompts
- ✅ Automatic polling and status tracking
- ✅ Video stitching to combine clips into longer videos
- ✅ Configurable resolution and duration
- ✅ Progress tracking and error handling

### Educational Video Pipeline (NEW)
- ✅ **LLM-powered video planning** - Converts lesson requests into structured scene specifications
- ✅ **Automatic scene type detection** - Intelligently chooses between SORA video and data graphs
- ✅ **OWID data integration** - Fetches and visualizes real-world data from Our World in Data
- ✅ **Graph scenes** - Creates 5-second pauses on data visualizations
- ✅ **Mixed media stitching** - Combines SORA video clips with graph images seamlessly
- ✅ **JSON scene specifications** - Machine-readable format for video structure

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Get your API key from:
- OpenAI (for Sora, GPT-4, and TTS): https://platform.openai.com/api-keys

### 3. Verify Installation

```bash
python sora_video_generator.py
```

## Usage

### Run Backend + Frontend

1. Start the backend API server so the frontend can trigger the pipeline and serve generated videos:

```bash
cd backend
python api_server.py
```

2. Launch the frontend dev server (Vite defaults to `http://localhost:5173`):

```bash
cd frontend
npm run dev
```

Once both servers are running, you can control the pipeline through the frontend UI.

## Educational Video Pipeline (Quick Start)

The fastest way to create educational videos:

```bash
python generate_educational_video.py
```

This will generate a complete educational video about climate change, mixing SORA video clips with OWID data visualizations.

### Custom Educational Video

```python
from educational_video_pipeline import EducationalVideoPipeline
import asyncio

async def main():
    # Initialize the pipeline
    pipeline = EducationalVideoPipeline()

    # Describe your lesson
    lesson_request = """
    Create a 40-second video about global poverty reduction.
    Start with a scene showing communities in developing nations.
    Show data on poverty rates declining over the past 30 years.
    Display income growth statistics.
    End with an inspiring scene of economic opportunity and growth.
    """

    # Generate the video
    result = await pipeline.generate_video(
        lesson_request=lesson_request,
        output_filename="poverty_reduction.mp4"
    )

    print(f"Video saved to: {result['final_video_path']}")

asyncio.run(main())
```

### How the Pipeline Works

1. **LLM Planning** - GPT-4 analyzes your lesson request and creates a scene-by-scene plan
2. **Scene Generation**:
   - **SORA scenes**: Generates cinematic video clips (4-12 seconds each)
   - **Graph scenes**: Fetches data visualizations from Our World in Data (5 seconds each)
3. **Stitching** - Combines all scenes into a final educational video
4. **Output** - Saves the complete video with proper transitions

### Example Output Structure

```json
{
  "title": "Global Poverty Reduction",
  "scenes": [
    {
      "scene_number": 1,
      "type": "sora",
      "duration": 8,
      "prompt": "A bustling marketplace in a developing nation...",
      "script": "Over the past 30 years, we've witnessed unprecedented economic growth..."
    },
    {
      "scene_number": 2,
      "type": "graph",
      "duration": 5,
      "chart_slug": "share-of-population-in-extreme-poverty",
      "countries": ["World", "India", "China"],
      "script": "Global extreme poverty rates have fallen dramatically..."
    }
  ]
}
```

---

## Basic SORA Video Generation

### Basic Usage - Single Video

```python
from sora_video_generator import SoraVideoGenerator

# Initialize generator
generator = SoraVideoGenerator()

# Generate a single 12-second video
result = generator.generate_single_video(
    prompt="A cat playing piano in a cozy living room",
    duration=12,
    resolution="720p"
)

print(f"Video saved to: {result['local_path']}")
```

### Generate Multiple Clips

```python
# Create multiple clips for a longer story
prompts = [
    "A rocket launching from a launchpad at dawn",
    "The rocket traveling through Earth's atmosphere",
    "The rocket entering outer space with stars in background",
    "An astronaut floating in space looking at Earth"
]

results = generator.generate_multiple_clips(
    prompts=prompts,
    duration=12,  # Each clip will be 12 seconds
    resolution="720p"
)
```

### Stitch Clips Together

```python
# Get paths of successfully generated clips
video_paths = [
    result["local_path"]
    for result in results
    if result.get("status") == "completed"
]

# Stitch into one video
final_video = generator.stitch_videos(
    video_paths,
    output_filename="my_story.mp4"
)

print(f"Final video: {final_video}")
# Result: A 48-second video (4 clips × 12 seconds)
```

### Custom Example - Creating a ~90 Second Video

```python
# To create a ~90 second video, generate 8 clips of 12 seconds each
# (8 × 12s = 96 seconds ≈ 1.5 minutes)

prompts = [
    "A serene mountain landscape at sunrise",
    "A hiker starting their journey up the mountain trail",
    "The hiker climbing through a dense forest",
    "Reaching a clearing with a waterfall",
    "Crossing a wooden bridge over a stream",
    "Approaching the mountain summit",
    "Standing at the peak with panoramic views",
    "Sunset view from the mountain top"
]

# Generate all clips
results = generator.generate_multiple_clips(prompts, duration=12)

# Stitch together
video_paths = [r["local_path"] for r in results if r.get("status") == "completed"]
final = generator.stitch_videos(video_paths, "mountain_journey.mp4")
```

## API Limitations

- **Maximum duration per clip**: 12 seconds (API limit)
- **Workaround for longer videos**: Generate multiple 12s clips and stitch them together
- **Resolution options**: "720p", "1080p", etc.
- **Model**: Currently uses "sora-2"

## Output

All generated videos are saved to the `generated_videos/` directory.

## Troubleshooting

### "OpenAI API key not found"

Make sure you have:
1. Created a `.env` file
2. Added `OPENAI_API_KEY=your-key-here` to the file
3. The `.env` file is in the same directory as the script

### "moviepy is required"

The video stitching feature requires moviepy. Install it with:

```bash
pip install moviepy
```

### Video generation fails

Check:
- Your API key is valid and has access to Sora API
- You have sufficient API credits
- The prompt is appropriate and follows OpenAI's usage policies

## Cost Considerations

Sora API usage incurs costs based on:
- Video duration
- Resolution
- Number of generations

Check OpenAI's pricing page for current rates: https://openai.com/pricing

## Our World in Data MCP Server

The project includes an MCP (Model Context Protocol) server for accessing Our World in Data visualizations.

### Available Tools

- `search_charts` - Search for OWID charts by keyword
- `visualize_chart` - Generate chart visualizations
- `get_chart_summary` - Get statistical summaries of chart data
- `get_chart_metadata` - Fetch chart metadata and descriptions

### Running the MCP Server

```bash
cd OWIDChart
python server.py
```

## Project Structure

```
VeoLab/
├── educational_video_pipeline.py   # Main pipeline orchestrator
├── generate_educational_video.py   # Quick start example
├── sora_video_generator.py         # Sora video generation class
├── OWIDChart/
│   └── server.py                   # OWID MCP server
├── generated_videos/               # Output directory
│   ├── scenes/                     # Individual scene clips
│   └── graphs/                     # Generated graph images
├── requirements.txt                # Python dependencies
└── .env                           # API keys (not in git)
```

## API Documentation

For more information:
- [OpenAI Video Generation Guide](https://platform.openai.com/docs/guides/video-generation)
- [Azure OpenAI Sora Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/video-generation)
- [Our World in Data](https://ourworldindata.org/)

## License

MIT License - feel free to use and modify as needed.
