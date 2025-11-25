"""
Educational Video Pipeline - OpenAI Only Version
Uses GPT-4 for planning and SORA for video generation (no Anthropic required).
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from sora_video_generator import SoraVideoGenerator
import httpx
from PIL import Image

# Load environment variables
load_dotenv()


class EducationalVideoPipelineOpenAI:
    """Educational video pipeline using only OpenAI APIs."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the pipeline with OpenAI API key only.

        Args:
            openai_api_key: OpenAI API key for both GPT-4 and SORA
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment or parameters")

        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.sora_generator = SoraVideoGenerator(api_key=self.openai_api_key)

        # Create output directories
        self.output_dir = Path("generated_videos")
        self.scenes_dir = self.output_dir / "scenes"
        self.graphs_dir = self.output_dir / "graphs"
        self.output_dir.mkdir(exist_ok=True)
        self.scenes_dir.mkdir(exist_ok=True)
        self.graphs_dir.mkdir(exist_ok=True)

    def search_owid_charts(self, query: str) -> List[str]:
        """
        Search for OWID charts by keyword.

        Args:
            query: Search query

        Returns:
            List of chart slugs
        """
        # Import the search logic from MCP server
        common_charts = {
            "life expectancy": ["life-expectancy", "life-expectancy-at-birth"],
            "population": ["population", "population-growth-rates", "population-density"],
            "gdp": ["gdp-per-capita-worldbank", "gdp-growth"],
            "co2": ["annual-co2-emissions-per-country", "co-emissions-per-capita"],
            "climate": ["temperature-anomaly", "climate-change-impacts"],
            "education": ["mean-years-of-schooling", "literacy-rates"],
            "health": ["child-mortality", "maternal-mortality"],
            "poverty": ["share-of-population-in-extreme-poverty", "poverty-gap-index"],
            "democracy": ["democracy-index", "electoral-democracy"],
            "energy": ["modern-renewable-energy-consumption", "renewable-share-energy", "electricity-generation"],
            "inequality": ["economic-inequality-gini-index", "income-inequality"],
            "renewable": ["modern-renewable-energy-consumption", "renewable-share-energy", "electricity-prod-source-stacked"],
        }

        query_lower = query.lower()
        matches = []

        for topic, chart_slugs in common_charts.items():
            if query_lower in topic or topic in query_lower:
                matches.extend(chart_slugs)

        return matches if matches else []

    def plan_video(
        self,
        lesson_request: str,
        num_scenes: int = 6,
        graph_proportion: float = 0.2,
        enable_graphs: bool = True
    ) -> Dict[str, Any]:
        """
        Use GPT-4 to plan the video structure from a lesson request.
        Includes OWID chart search to validate chart slugs.

        Args:
            lesson_request: Description of the educational content to create
            num_scenes: Total number of scenes to generate (default: 6)
            graph_proportion: Proportion of scenes that should be graphs (0.0-1.0, default: 0.2)
            enable_graphs: Whether to include OWID graph scenes (default: True)

        Returns:
            dict: JSON specification of scenes
        """
        print("=" * 60)
        print("PLANNING VIDEO WITH GPT-4")
        print("=" * 60)
        print(f"Lesson request: {lesson_request}")
        print(f"Scenes: {num_scenes}")
        print(f"Graph proportion: {graph_proportion:.1%}")
        print(f"Graphs enabled: {enable_graphs}\n")

        # Calculate number of graph scenes
        num_graph_scenes = int(num_scenes * graph_proportion) if enable_graphs else 0
        num_sora_scenes = num_scenes - num_graph_scenes

        print(f"Target composition: {num_sora_scenes} SORA scenes, {num_graph_scenes} graph scenes\n")

        # Search for available charts (only if graphs enabled)
        available_charts = {}
        if enable_graphs and num_graph_scenes > 0:
            # First, let GPT-4 identify what data topics are needed
            topics_prompt = f"""Given this lesson request, identify the main data topics that would need OWID charts.

Lesson request: {lesson_request}

List 2-4 specific data topics (like "renewable energy", "co2 emissions", "life expectancy", "poverty", "gdp") that would be relevant for this lesson.
Return a JSON object with a "topics" key containing an array of topic strings.

Example: {{"topics": ["renewable energy", "co2 emissions"]}}"""

            topics_response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": topics_prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            try:
                topics_data = json.loads(topics_response.choices[0].message.content)
                topics = topics_data.get("topics", [])
                print(f"Identified topics: {', '.join(topics)}\n")
            except Exception as e:
                print(f"Warning: Could not parse topics response: {e}")
                topics = []

            # Search for available charts for each topic
            if topics:
                print(f"Searching OWID for topics: {', '.join(topics)}")
                for topic in topics:
                    charts = self.search_owid_charts(topic)
                    if charts:
                        available_charts[topic] = charts
                        print(f"  - {topic}: {len(charts)} charts found")
                print()

        # Build the available charts info for the planning prompt
        charts_info = ""
        if available_charts:
            charts_info = "\n\nAVAILABLE OWID CHARTS:\n"
            charts_info += "=" * 50 + "\n"
            charts_info += "WARNING: You MUST use ONLY these chart slugs. Do not invent or guess chart slugs!\n"
            charts_info += "=" * 50 + "\n\n"
            for topic, slugs in available_charts.items():
                charts_info += f"{topic.upper()}:\n"
                for slug in slugs:
                    charts_info += f"  - {slug}\n"
                charts_info += "\n"

        planning_prompt = f"""You are an educational video planner. Given a lesson request, create a detailed scene-by-scene specification for a short educational video.
{charts_info}

Lesson request: {lesson_request}

CRITICAL: SETTING AND CULTURAL CONSISTENCY
- First, identify the specific geographic location, country, or cultural setting from the lesson request
- If the lesson mentions a specific place (e.g., "rural China", "India", "Brazil", "Africa"), ALL scenes must maintain that setting
- SORA prompts MUST include specific cultural and geographic details matching the topic
- Example: If topic is "rural China", show Chinese architecture, Chinese people, Chinese landscapes, Chinese cultural elements
- Do NOT use generic or different geographic imagery when a specific location is mentioned
- Maintain consistent visual identity and cultural context across the entire video

SCENE REQUIREMENTS:
- Create EXACTLY {num_scenes} scenes total
- Include EXACTLY {num_sora_scenes} SORA video scenes
{"- Include EXACTLY " + str(num_graph_scenes) + " graph scenes using OWID charts" if num_graph_scenes > 0 else "- Do NOT include any graph scenes (SORA only)"}

Each scene should be either:
- A SORA video clip (for visual demonstrations, animations, or conceptual illustrations)
- A data graph from Our World in Data (for showing statistics, trends, and data)

RULES FOR GRAPH SCENES:
{"- You MUST use ONLY the chart slugs listed above under 'AVAILABLE OWID CHARTS'" if available_charts else "- No OWID charts are available for this lesson, use SORA scenes only"}
- NEVER make up or guess chart slugs
- If no relevant chart exists in the list, use a SORA scene instead
- CRITICAL: Choose charts with COMPATIBLE METRICS on similar scales
  * DO NOT mix absolute numbers (population, GDP in millions/billions) with rates/percentages (0-100 or 0-1)
  * Example BAD: Graphing "population (millions)" and "poverty rate (%)" together - incompatible scales
  * Example GOOD: Graphing only "poverty rate (%)" across multiple countries - same scale
  * Example GOOD: Graphing only "population (millions)" across multiple countries - same scale
  * If a chart contains mixed metrics, use the 'countries' filter strategically to show only comparable data
  * When in doubt, prefer charts with single clear metrics over multi-metric charts

For each scene, specify:
- scene_number: Sequential number starting from 1
- type: Either "sora" or "graph"
- duration: Duration in seconds (4, 8, or 12 for SORA; 5 for graphs)
- script: The narration/educational text for this scene (2-3 sentences)

For SORA scenes, also include:
- prompt: Detailed visual description for video generation (NO audio, NO narrator mentions - silent video only)
  * MUST maintain the geographic/cultural setting identified in the lesson request
  * Include specific location details (e.g., "in rural China", "Chinese village", "Chinese architecture")
  * Show culturally appropriate people, clothing, architecture, landscapes
- script: Short narration text (MUST be ideally 20 words - less is sometimes acceptable) that will be added via TTS

For GRAPH scenes, also include:
- chart_slug: The exact chart slug from the list above (REQUIRED - must match exactly)
- countries: List of countries to focus on (optional, e.g., ["United States", "China", "India"])
- time_range: Time range filter (optional, e.g., "1990..2020")

Output ONLY valid JSON in this format:
{{
  "title": "Video title",
  "description": "Brief description of the video",
  "scenes": [
    {{
      "scene_number": 1,
      "type": "sora",
      "duration": 8,
      "script": "Wind turbines harness clean energy, transforming our planet's future with every rotation.",
      "prompt": "Cinematic shot of modern wind turbines at sunrise in rural China, Chinese countryside with traditional architecture visible in background, golden hour lighting, professional documentary style, 4K quality, silent video with no audio"
    }},
    {{
      "scene_number": 2,
      "type": "graph",
      "duration": 5,
      "script": "Life expectancy has dramatically increased across major nations over seventy years.",
      "chart_slug": "life-expectancy",
      "countries": ["United States", "Japan", "India"],
      "time_range": "1950..2020"
    }}
  ]
}}

Make the video engaging and educational. Mix SORA and graph scenes appropriately.
Remember: Use ONLY the exact chart slugs from the provided list. Do not invent new slugs."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an educational video planning assistant. Always respond with valid JSON only."},
                {"role": "user", "content": planning_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        # Extract JSON from response
        response_text = response.choices[0].message.content

        try:
            video_plan = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text}")
            raise

        print(f"[OK] Video plan created: {video_plan.get('title', 'Untitled')}")
        print(f"[OK] {len(video_plan.get('scenes', []))} scenes planned\n")

        # Save the plan
        plan_file = self.output_dir / f"video_plan_{int(time.time())}.json"
        with open(plan_file, 'w') as f:
            json.dump(video_plan, f, indent=2)
        print(f"[OK] Plan saved to: {plan_file}\n")

        return video_plan

    def select_compatible_metrics(self, chart_slug: str, script: str, available_metrics: List[str]) -> List[str]:
        """Use LLM to intelligently select which metrics to plot when scales are incompatible."""
        prompt = f"""You are analyzing a data visualization for an educational video scene.

Chart: {chart_slug}
Scene script: {script}
Available metrics: {', '.join(available_metrics)}

These metrics have incompatible scales (e.g., one is in millions, another is a percentage).
Select which metric(s) should be plotted based on:
1. What the scene script is actually discussing
2. The chart name/topic
3. What would be most educational

Return ONLY a comma-separated list of the metric names to keep. Example: "Poverty rate, Extreme poverty rate"
If only one metric is relevant, return just that one."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            selected = response.choices[0].message.content.strip()
            # Parse the response into a list
            selected_metrics = [m.strip() for m in selected.split(',')]
            # Filter to only valid metrics
            valid_selected = [m for m in selected_metrics if m in available_metrics]
            return valid_selected if valid_selected else [available_metrics[0]]  # Fallback to first metric
        except Exception as e:
            print(f"  [WARN] Could not select metrics via LLM: {e}")
            return [available_metrics[0]]  # Fallback to first metric

    async def fetch_owid_chart_image(
        self,
        chart_slug: str,
        script: str = "",
        countries: Optional[List[str]] = None,
        time_range: Optional[str] = None
    ) -> Path:
        """Generate OWID chart using the MCP server visualization code."""
        print(f"  Creating OWID visualization: {chart_slug}")
        if countries:
            print(f"  Countries: {', '.join(countries)}")
        if time_range:
            print(f"  Time range: {time_range}")

        try:
            # Import the MCP server visualization functions
            import sys
            sys.path.insert(0, str(Path(__file__).parent / "OWIDChart"))
            from server import create_visualization
            import pandas as pd
            import io

            # Fetch the data from OWID
            url = f"https://ourworldindata.org/grapher/{chart_slug}.csv"
            params = {}
            if time_range:
                params["time"] = time_range

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                df = pd.read_csv(io.StringIO(response.text))

            # Filter by countries if specified
            if countries and 'Entity' in df.columns:
                df = df[df['Entity'].isin(countries)]

            # Limit to 10 countries max for readability
            if 'Entity' in df.columns:
                entities = df['Entity'].unique()
                if len(entities) > 10:
                    time_col = 'Year' if 'Year' in df.columns else ('Day' if 'Day' in df.columns else None)
                    if time_col:
                        non_data_cols = ['Entity', 'Code', 'Year', 'Day', 'time']
                        data_cols = [col for col in df.columns if col not in non_data_cols]
                        if data_cols:
                            latest_data = df.sort_values(time_col).groupby('Entity').last()
                            top_entities = latest_data.nlargest(10, data_cols[0]).index.tolist()
                            df = df[df['Entity'].isin(top_entities)]

            # Validate scale compatibility for multi-metric charts
            non_data_cols = ['Entity', 'Code', 'Year', 'Day', 'time']
            data_cols = [col for col in df.columns if col not in non_data_cols]

            if len(data_cols) > 1:
                # Check if metrics have vastly different scales
                ranges = []
                for col in data_cols:
                    numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(numeric_data) > 0:
                        col_min, col_max = numeric_data.min(), numeric_data.max()
                        col_range = col_max - col_min
                        ranges.append((col, col_max, col_range))

                if len(ranges) > 1:
                    # Check if max values differ by more than 100x
                    max_vals = [r[1] for r in ranges]
                    if max(max_vals) / min(max_vals) > 100:
                        print(f"  [WARNING] Incompatible scales detected:")
                        for col, max_val, range_val in ranges:
                            print(f"    - {col}: max={max_val:.2f}, range={range_val:.2f}")

                        # Use LLM to intelligently select which metrics to keep
                        print(f"  [AUTO-FIX] Using LLM to select relevant metrics based on scene context...")
                        selected_metrics = self.select_compatible_metrics(
                            chart_slug=chart_slug,
                            script=script,
                            available_metrics=data_cols
                        )
                        print(f"  [AUTO-FIX] Selected metrics: {', '.join(selected_metrics)}")

                        # Filter dataframe to only keep selected metrics
                        non_data_cols_set = set(non_data_cols)
                        cols_to_keep = [col for col in df.columns if col in non_data_cols_set or col in selected_metrics]
                        df = df[cols_to_keep]

            # Create visualization using MCP server code
            title = f"{chart_slug.replace('-', ' ').title()}"
            image_bytes = create_visualization(df, title, chart_slug)

            # Save the image
            image_filename = f"{chart_slug}_{int(time.time())}.png"
            image_path = self.graphs_dir / image_filename

            with open(image_path, 'wb') as f:
                f.write(image_bytes)

            print(f"  OK Chart visualization created: {image_path}")
            return image_path

        except Exception as e:
            print(f"  Error creating visualization: {e}")
            raise

    async def generate_graph_scene(self, scene: Dict[str, Any], scene_number: int) -> Dict[str, Any]:
        """
        Generate a graph scene by fetching OWID data.
        Adds AI-generated voiceover narration using OpenAI TTS.
        If audio is longer than intended duration, extends the graph duration to fit (audio + 1s).
        """
        print(f"\n{'='*60}")
        print(f"GRAPH SCENE {scene_number}")
        print(f"{'='*60}")
        script = scene.get('script', '')
        intended_duration = scene.get('duration', 5)
        print(f"Script: {script}")

        try:
            chart_slug = scene.get('chart_slug') or scene.get('chart_query', '').replace(' ', '-')
            countries = scene.get('countries')
            time_range = scene.get('time_range')

            image_path = await self.fetch_owid_chart_image(
                chart_slug=chart_slug,
                script=script,
                countries=countries,
                time_range=time_range
            )

            # Generate voiceover for the graph (no duration constraint - graphs are flexible)
            audio_path = None
            final_duration = intended_duration
            if script:
                try:
                    # Shorten script to 20 words or less
                    shortened_script = self.shorten_script(script, max_words=22)

                    # Generate voiceover without duration constraint (graphs are flexible)
                    audio_path = self.generate_voiceover(shortened_script, scene_number, target_duration=None)

                    # Check audio duration and extend graph if needed
                    if audio_path and audio_path.exists():
                        from moviepy import AudioFileClip
                        audio_clip = AudioFileClip(str(audio_path))
                        audio_duration = audio_clip.duration
                        audio_clip.close()

                        if audio_duration > intended_duration:
                            final_duration = int(audio_duration) + 1  # Audio duration + 1 second
                            print(f"  Graph duration extended from {intended_duration}s to {final_duration}s to fit voiceover")

                except Exception as e:
                    print(f"  [WARN] Could not generate voiceover: {e}")
            else:
                shortened_script = script

            return {
                "scene_number": scene_number,
                "type": "graph",
                "status": "completed",
                "image_path": image_path,
                "audio_path": audio_path,
                "script": shortened_script,
                "duration": final_duration  # Use extended duration if needed
            }

        except Exception as e:
            print(f"  [ERROR] Error generating graph scene: {e}")
            return {
                "scene_number": scene_number,
                "type": "graph",
                "status": "failed",
                "error": str(e)
            }

    def shorten_script(self, script: str, max_words: int = 20) -> str:
        """
        Use LLM to shorten script to max_words or less while preserving meaning.

        Args:
            script: Original script text
            max_words: Maximum number of words allowed

        Returns:
            Shortened script
        """
        word_count = len(script.split())
        if word_count <= max_words:
            return script

        print(f"  Shortening script from {word_count} to {max_words} words...")

        try:
            prompt = f"""Shorten this script to EXACTLY {max_words} words or less while keeping the core message clear and impactful.

Original script: "{script}"

Return ONLY the shortened script text, nothing else."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )

            shortened = response.choices[0].message.content.strip().strip('"')
            shortened_word_count = len(shortened.split())
            print(f"  Shortened to {shortened_word_count} words: '{shortened}'")
            return shortened

        except Exception as e:
            print(f"  [WARN] Could not shorten script: {e}, truncating...")
            # Fallback: simple truncation
            words = script.split()
            return ' '.join(words[:max_words])

    def generate_voiceover(self, script: str, scene_number: int, target_duration: int = None) -> Path:
        """
        Generate voiceover audio using OpenAI TTS API.
        If audio is longer than target_duration, speeds it up to fit.

        Args:
            script: The text to be spoken
            scene_number: Scene number for filename
            target_duration: Target duration in seconds (will speed up if needed)

        Returns:
            Path to the generated audio file
        """
        print(f"  Generating voiceover for scene {scene_number}...")

        try:
            # Use OpenAI TTS to generate speech
            response = self.openai_client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice="nova",  # Professional female voice (options: alloy, echo, fable, onyx, nova, shimmer)
                input=script
            )

            # Save the audio file
            audio_filename = f"voiceover_scene_{scene_number:02d}_{int(time.time())}.mp3"
            audio_path = self.scenes_dir / audio_filename

            response.stream_to_file(str(audio_path))

            # Check duration and speed up if needed
            if target_duration:
                from moviepy import AudioFileClip
                audio_clip = AudioFileClip(str(audio_path))
                actual_duration = audio_clip.duration

                if actual_duration > target_duration:
                    # Calculate speed factor needed
                    speed_factor = actual_duration / target_duration
                    print(f"  Audio is {actual_duration:.1f}s, speeding up by {speed_factor:.2f}x to fit {target_duration}s")

                    # Speed up audio - use speedx directly on the clip
                    sped_up_audio = audio_clip.with_speed_multiplier(speed_factor)

                    # Save sped-up version
                    sped_up_filename = f"voiceover_scene_{scene_number:02d}_{int(time.time())}_sped.mp3"
                    sped_up_path = self.scenes_dir / sped_up_filename
                    sped_up_audio.write_audiofile(str(sped_up_path))

                    # Clean up
                    audio_clip.close()
                    sped_up_audio.close()

                    print(f"  [OK] Voiceover generated and sped up: {sped_up_path}")
                    return sped_up_path
                else:
                    audio_clip.close()
                    print(f"  [OK] Voiceover generated ({actual_duration:.1f}s): {audio_path}")
                    return audio_path
            else:
                print(f"  [OK] Voiceover generated: {audio_path}")
                return audio_path

        except Exception as e:
            print(f"  [WARN] Could not generate voiceover: {e}")
            return None

    def add_voiceover_to_video(self, video_path: Path, audio_path: Path) -> Path:
        """
        Add voiceover audio to video (SORA videos are silent).

        Args:
            video_path: Path to the video file
            audio_path: Path to the voiceover audio file

        Returns:
            Path to the new video with voiceover
        """
        try:
            from moviepy import VideoFileClip, AudioFileClip
        except ImportError:
            raise ImportError("moviepy is required")

        print(f"  Adding voiceover to video...")

        # Load video and voiceover
        video = VideoFileClip(str(video_path))
        voiceover = AudioFileClip(str(audio_path))

        # Add voiceover as the audio track (SORA videos are silent)
        video_with_vo = video.with_audio(voiceover)

        # Save the new video
        output_filename = video_path.stem + "_with_voiceover.mp4"
        output_path = self.scenes_dir / output_filename

        video_with_vo.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',
            fps=24
        )

        # Clean up
        video.close()
        voiceover.close()
        video_with_vo.close()

        print(f"  [OK] Voiceover added: {output_path}")
        return output_path

    def generate_sora_scene(self, scene: Dict[str, Any], scene_number: int, max_retries: int = 3) -> Dict[str, Any]:
        """
        Generate a SORA video scene with retry logic for internal errors.
        SORA generates SILENT video, then we add TTS voiceover.

        Args:
            scene: Scene specification
            scene_number: Scene number
            max_retries: Maximum number of retry attempts (default: 3)
        """
        print(f"\n{'='*60}")
        print(f"SORA SCENE {scene_number}")
        print(f"{'='*60}")

        # SORA prompt should be silent - no narrator mentions
        prompt = scene.get('prompt', '')
        script = scene.get('script', '')
        duration = scene.get('duration', 8)

        print(f"Prompt: {prompt[:100]}...")
        print(f"Script for TTS: {script}")

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"  Retry attempt {attempt + 1}/{max_retries}...")
                    time.sleep(2)  # Brief delay before retry

                # Generate SORA video (silent)
                result = self.sora_generator.generate_single_video(
                    prompt=prompt,
                    duration=duration,
                    resolution="720p",
                    output_filename=f"scene_{scene_number:02d}_sora_{int(time.time())}.mp4"
                )

                if result.get('status') == 'completed':
                    original_path = result.get('local_path')
                    new_path = self.scenes_dir / Path(original_path).name
                    if Path(original_path).exists():
                        Path(original_path).rename(new_path)
                        result['local_path'] = new_path

                    print(f"  [OK] SORA scene generated successfully (silent)")

                    # Shorten script to 20 words or less
                    shortened_script = self.shorten_script(script, max_words=20)

                    # Generate TTS voiceover with duration constraint
                    audio_path = self.generate_voiceover(shortened_script, scene_number, target_duration=duration)

                    if audio_path:
                        # Add voiceover to silent SORA video
                        video_with_vo = self.add_voiceover_to_video(new_path, audio_path)
                        final_video_path = video_with_vo
                    else:
                        print(f"  [WARN] No voiceover generated, using silent video")
                        final_video_path = new_path

                    return {
                        "scene_number": scene_number,
                        "type": "sora",
                        "status": "completed",
                        "video_path": final_video_path,
                        "script": shortened_script,
                        "duration": duration
                    }
                else:
                    error_msg = result.get('error', 'Unknown error')
                    # Check if it's an internal error that should be retried
                    if 'internal' in error_msg.lower() or 'server' in error_msg.lower():
                        if attempt < max_retries - 1:
                            print(f"  [WARN] Internal error detected, will retry: {error_msg}")
                            continue
                    # Non-retryable error or final attempt
                    return {
                        "scene_number": scene_number,
                        "type": "sora",
                        "status": "failed",
                        "error": error_msg
                    }

            except Exception as e:
                error_msg = str(e)
                # Check if it's a retryable error
                if ('internal' in error_msg.lower() or
                    'server' in error_msg.lower() or
                    'timeout' in error_msg.lower()):
                    if attempt < max_retries - 1:
                        print(f"  [WARN] Error (will retry): {error_msg}")
                        continue

                print(f"  [ERROR] Error generating SORA scene: {e}")
                return {
                    "scene_number": scene_number,
                    "type": "sora",
                    "status": "failed",
                    "error": error_msg
                }

        # All retries exhausted
        return {
            "scene_number": scene_number,
            "type": "sora",
            "status": "failed",
            "error": f"Failed after {max_retries} attempts"
        }

    def image_to_video(self, image_path: Path, duration: int = 5, audio_path: Path = None) -> Path:
        """
        Convert a static image to a video clip at 720p (1280x720) resolution.
        Optionally adds voiceover audio.

        Args:
            image_path: Path to the image file
            duration: Duration in seconds
            audio_path: Optional path to audio file for voiceover
        """
        try:
            from moviepy import ImageClip, AudioFileClip
            import numpy as np
        except ImportError:
            raise ImportError("moviepy and numpy are required")

        print(f"  Converting image to {duration}s video clip at 720p...")

        # Load image with PIL and convert to RGB
        from PIL import Image
        img = Image.open(image_path).convert('RGB')

        # Resize to exactly 1280x720 (720p) to match SORA output
        target_size = (1280, 720)
        if img.size != target_size:
            print(f"    Resizing from {img.size} to {target_size}")
            img = img.resize(target_size, Image.Resampling.LANCZOS)

        img_array = np.array(img)

        # Create clip from numpy array
        clip = ImageClip(img_array, duration=duration)

        # Add voiceover if provided
        if audio_path and audio_path.exists():
            print(f"  Adding voiceover to graph video...")
            audio = AudioFileClip(str(audio_path))
            clip = clip.with_audio(audio)

        video_filename = image_path.stem + "_video.mp4"
        video_path = self.scenes_dir / video_filename

        clip.write_videofile(
            str(video_path),
            fps=24,
            codec='libx264',
            audio_codec='aac' if audio_path else None
        )

        clip.close()
        print(f"  OK Video clip created at 720p: {video_path}")
        return video_path

    def stitch_final_video(self, scene_results: List[Dict[str, Any]], output_filename: str) -> Path:
        """Stitch all scenes together into final video."""
        try:
            from moviepy import VideoFileClip, concatenate_videoclips
        except ImportError:
            raise ImportError("moviepy is required. Install with: pip install moviepy")

        print(f"\n{'='*60}")
        print("STITCHING FINAL VIDEO")
        print(f"{'='*60}")

        clips = []

        for scene_result in scene_results:
            if scene_result.get('status') != 'completed':
                print(f"[WARN] Skipping failed scene {scene_result.get('scene_number')}")
                continue

            scene_type = scene_result.get('type')

            if scene_type == 'graph':
                image_path = scene_result.get('image_path')
                audio_path = scene_result.get('audio_path')
                duration = scene_result.get('duration', 5)  # Use actual duration (may be extended for longer audio)
                if image_path and Path(image_path).exists():
                    print(f"Scene {scene_result.get('scene_number')}: Graph ({duration}s) with voiceover")
                    video_path = self.image_to_video(image_path, duration=duration, audio_path=audio_path)
                    clips.append(VideoFileClip(str(video_path)))

            elif scene_type == 'sora':
                video_path = scene_result.get('video_path')
                if video_path and Path(video_path).exists():
                    duration = scene_result.get('duration', 12)
                    print(f"Scene {scene_result.get('scene_number')}: SORA ({duration}s)")
                    clips.append(VideoFileClip(str(video_path)))

        if not clips:
            raise ValueError("No valid clips to stitch together")

        print(f"\nStitching {len(clips)} clips together...")

        # Concatenate clips - all have TTS voiceover:
        # - SORA clips: Silent video + OpenAI TTS voiceover (20 words max, audio sped up to fit fixed video duration)
        # - Graph clips: Static image + OpenAI TTS voiceover (20 words max, graph duration extended if audio is longer)
        final_clip = concatenate_videoclips(clips, method="compose")
        output_path = self.output_dir / output_filename

        final_clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac',  # AAC audio codec for compatibility
            fps=24
        )

        for clip in clips:
            clip.close()
        final_clip.close()

        print(f"\n[OK] Final video saved: {output_path}")
        return output_path

    async def generate_video_from_plan(self, video_plan: Dict[str, Any], output_filename: Optional[str] = None) -> Dict[str, Any]:
        """Generate video from a pre-made scene plan."""
        print("\n" + "="*60)
        print("EDUCATIONAL VIDEO PIPELINE (FROM PLAN)")
        print("="*60 + "\n")

        start_time = time.time()

        scene_results = []
        for scene in video_plan.get('scenes', []):
            scene_number = scene.get('scene_number', len(scene_results) + 1)
            scene_type = scene.get('type', 'unknown')

            if scene_type == 'graph':
                result = await self.generate_graph_scene(scene, scene_number)
            elif scene_type == 'sora':
                result = self.generate_sora_scene(scene, scene_number)
            else:
                continue

            scene_results.append(result)

        if not output_filename:
            output_filename = f"educational_video_{int(time.time())}.mp4"

        try:
            final_video_path = self.stitch_final_video(scene_results, output_filename)
            elapsed_time = time.time() - start_time

            return {
                "status": "completed",
                "video_plan": video_plan,
                "scene_results": scene_results,
                "final_video_path": final_video_path,
                "elapsed_time": elapsed_time
            }

        except Exception as e:
            return {
                "status": "failed",
                "video_plan": video_plan,
                "scene_results": scene_results,
                "error": str(e)
            }

    async def generate_video(
        self,
        lesson_request: str,
        output_filename: Optional[str] = None,
        num_scenes: int = 6,
        graph_proportion: float = 0.2,
        enable_graphs: bool = True
    ) -> Dict[str, Any]:
        """
        Full pipeline: Generate educational video from lesson request.

        Args:
            lesson_request: Description of the educational content
            output_filename: Optional custom output filename
            num_scenes: Total number of scenes (default: 6)
            graph_proportion: Proportion of scenes that are graphs (default: 0.2 = 20%)
            enable_graphs: Whether to include OWID graphs (default: True)
        """
        print("\n" + "="*60)
        print("EDUCATIONAL VIDEO PIPELINE (OpenAI Only)")
        print("="*60 + "\n")

        start_time = time.time()

        # Plan with GPT-4
        video_plan = self.plan_video(
            lesson_request,
            num_scenes=num_scenes,
            graph_proportion=graph_proportion,
            enable_graphs=enable_graphs
        )

        # Generate scenes
        scene_results = []
        for scene in video_plan.get('scenes', []):
            scene_number = scene.get('scene_number', len(scene_results) + 1)
            scene_type = scene.get('type', 'unknown')

            if scene_type == 'graph':
                result = await self.generate_graph_scene(scene, scene_number)
            elif scene_type == 'sora':
                result = self.generate_sora_scene(scene, scene_number)
            else:
                continue

            scene_results.append(result)

        # Stitch
        if not output_filename:
            output_filename = f"educational_video_{int(time.time())}.mp4"

        try:
            final_video_path = self.stitch_final_video(scene_results, output_filename)
            elapsed_time = time.time() - start_time

            print(f"\n{'='*60}")
            print("[SUCCESS] VIDEO GENERATION COMPLETE!")
            print(f"{'='*60}")
            print(f"Output: {final_video_path}")
            print(f"Time: {elapsed_time:.1f}s")
            print("="*60 + "\n")

            return {
                "status": "completed",
                "video_plan": video_plan,
                "scene_results": scene_results,
                "final_video_path": final_video_path,
                "elapsed_time": elapsed_time
            }

        except Exception as e:
            return {
                "status": "failed",
                "video_plan": video_plan,
                "scene_results": scene_results,
                "error": str(e)
            }


async def main():
    """Example usage of the educational video pipeline."""
    print("\n" + "="*60)
    print("EDUCATIONAL VIDEO PIPELINE")
    print("="*60)
    print("\nFeatures:")
    print("  • GPT-4 planning with validated OWID charts")
    print("  • Silent SORA video generation")
    print("  • OWID data graphs at 720p")
    print("  • TTS voiceover (≤20 words)")
    print("  • Intelligent metric filtering for readable graphs")
    print("  • Cultural consistency across scenes")
    print("="*60 + "\n")

    pipeline = EducationalVideoPipelineOpenAI()

    # Example 1: Standard video with graphs (6 scenes, 20% graphs)
    lesson_request = """
    Create a short educational video about poverty reduction in rural China.
    Show how poverty rates have declined over the past decades.
    Make it engaging with specific details and facts.
    """

    result = await pipeline.generate_video(
        lesson_request=lesson_request,
        output_filename="china_poverty_education.mp4",
        num_scenes=6,
        graph_proportion=0.2,  # 20% graphs = ~1 graph scene
        enable_graphs=True
    )

    # Example 2: SORA-only video (no graphs)
    # result = await pipeline.generate_video(
    #     lesson_request="Explain how solar panels work",
    #     output_filename="solar_panels.mp4",
    #     num_scenes=8,
    #     enable_graphs=False  # Pure SORA video
    # )

    # Example 3: Data-heavy video (50% graphs)
    # result = await pipeline.generate_video(
    #     lesson_request="Analyze global climate change trends",
    #     output_filename="climate_analysis.mp4",
    #     num_scenes=10,
    #     graph_proportion=0.5,  # 50% graphs = 5 graph scenes
    #     enable_graphs=True
    # )

    print("\n" + "="*60)
    if result.get('status') == 'completed':
        print("[SUCCESS]")
        print(f"Final video: {result.get('final_video_path')}")
        print(f"Time taken: {result.get('elapsed_time', 0):.1f}s")
    else:
        print("[FAILED]")
        print(f"Error: {result.get('error')}")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
