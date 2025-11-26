# Educational Video Pipeline - Usage Guide

## Quick Start

Before running the script you must start the backend API server and frontend so the generated video can be served:

1. Start backend API:

```bash
cd backend
python api_server.py
```

2. Start the frontend dev server (runs on `localhost:5173`):

```bash
cd frontend
npm run dev
```

3. Run the pipeline example:

```python
python educational_video_pipeline_openai_only.py
```

## Customization Options

The pipeline now supports flexible configuration:

### 1. Number of Scenes
Control the total length of your video:

```python
await pipeline.generate_video(
    lesson_request="Your topic here",
    num_scenes=6  # Default: 6 scenes
)
```

**Examples:**
- `num_scenes=4` - Short video (~20-32 seconds)
- `num_scenes=6` - Standard video (~30-48 seconds)
- `num_scenes=10` - Long video (~50-80 seconds)

### 2. Graph Proportion
Control how many data graphs vs SORA videos:

```python
await pipeline.generate_video(
    lesson_request="Your topic here",
    graph_proportion=0.2  # Default: 0.2 (20% graphs)
)
```

**Examples:**
- `graph_proportion=0.0` - Pure SORA video, no graphs
- `graph_proportion=0.2` - Mostly SORA with occasional graphs (1 graph out of 6 scenes)
- `graph_proportion=0.5` - Balanced mix (3 graphs, 3 SORA out of 6 scenes)
- `graph_proportion=1.0` - Pure data visualization video

### 3. Enable/Disable Graphs
Completely turn off OWID graphs:

```python
await pipeline.generate_video(
    lesson_request="Your topic here",
    enable_graphs=False  # Default: True
)
```

## Complete Examples

### Example 1: Standard Educational Video
```python
# 6 scenes, 20% graphs = 1 graph, 5 SORA videos
result = await pipeline.generate_video(
    lesson_request="Explain poverty reduction in rural China",
    output_filename="china_poverty.mp4",
    num_scenes=6,
    graph_proportion=0.2,
    enable_graphs=True
)
```

### Example 2: Pure SORA Video (No Graphs)
```python
# 8 scenes, all SORA - perfect for conceptual topics
result = await pipeline.generate_video(
    lesson_request="How do solar panels convert sunlight to electricity?",
    output_filename="solar_panels.mp4",
    num_scenes=8,
    enable_graphs=False
)
```

### Example 3: Data-Heavy Analysis Video
```python
# 10 scenes, 50% graphs = 5 graphs, 5 SORA videos
result = await pipeline.generate_video(
    lesson_request="Analyze global climate change trends since 1900",
    output_filename="climate_analysis.mp4",
    num_scenes=10,
    graph_proportion=0.5,
    enable_graphs=True
)
```

## Key Features

✅ **Cultural Consistency** - Maintains geographic/cultural setting across all scenes
✅ **Intelligent Metric Filtering** - Automatically removes incompatible metrics from graphs
✅ **Smart Audio Timing** - SORA audio speeds up, graph durations extend as needed
✅ **Validated Charts** - Only uses real OWID chart slugs (no hallucinations)
✅ **Short Scripts** - LLM automatically shortens narration to ≤20 words
✅ **720p Output** - All videos and graphs rendered at 1280x720

## Output Structure

```
generated_videos/
├── scenes/           # Individual scene files (SORA videos + voiceover)
├── graphs/           # Generated OWID chart images
├── video_plan_*.json # Planning documents
└── your_video.mp4    # Final stitched video
```

## Troubleshooting

**Problem:** "Incompatible scales detected"
**Solution:** The system will auto-fix by selecting relevant metrics via LLM

**Problem:** "No OWID charts found"
**Solution:** Video will use SORA scenes only

**Problem:** "Audio cut off in SORA scene"
**Solution:** Already handled - audio speeds up automatically to fit

**Problem:** Different cultural setting in final scene
**Solution:** Already fixed - cultural consistency enforced in planning prompt
