"""
Sora Video Generator
Generates videos using OpenAI's Sora API with support for 12-second clips.
Can generate multiple clips and optionally stitch them together.
"""

import os
import time
import asyncio
from typing import List, Optional
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SoraVideoGenerator:
    """Class to handle Sora video generation with 12-second clips."""

    # Resolution mapping from common names to WxH format
    RESOLUTION_MAP = {
        "720p": "1280x720",
        "1080p": "1920x1080",
        "480p": "854x480",
        "4k": "3840x2160"
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Sora video generator.

        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = Path("generated_videos")
        self.output_dir.mkdir(exist_ok=True)

    def _get_size_format(self, resolution: str) -> str:
        """Convert resolution like '720p' to size format like '1280x720'."""
        if 'x' in resolution:
            return resolution
        return self.RESOLUTION_MAP.get(resolution.lower(), "1280x720")

    def generate_single_video(
        self,
        prompt: str,
        duration: int = 12,
        resolution: str = "720p",
        model: str = "sora-2",
        output_filename: Optional[str] = None
    ) -> dict:
        """
        Generate a single video using Sora API.

        Args:
            prompt: Text description for the video
            duration: Video duration in seconds (max 12 for API)
            resolution: Video resolution (e.g., "720p", "1080p")
            model: Sora model to use (default: "sora-2")
            output_filename: Optional custom filename for the output

        Returns:
            dict: Video generation result with status and metadata
        """
        if duration > 12:
            print(f"Warning: Duration {duration}s exceeds API limit. Setting to 12s.")
            duration = 12

        # Convert resolution to size format
        size = self._get_size_format(resolution)

        print(f"Creating video generation job...")
        print(f"Prompt: {prompt}")
        print(f"Duration: {duration}s")
        print(f"Size: {size}")

        try:
            # Create video generation job
            # API expects seconds as a string: "4", "8", or "12"
            video = self.client.videos.create(
                model=model,
                prompt=prompt,
                size=size,
                seconds=str(duration)
            )

            print(f"Job created with ID: {video.id}")
            print(f"Status: {video.status}")

            # Poll for completion
            video_result = self._poll_video_status(video.id)

            if video_result.get("status") == "completed":
                # Download the video
                video_path = self._download_video(
                    video_result,
                    output_filename or f"video_{int(time.time())}.mp4"
                )
                video_result["local_path"] = video_path
                print(f"[SUCCESS] Video saved to: {video_path}")

            return video_result

        except Exception as e:
            print(f"[ERROR] Error generating video: {e}")
            return {"status": "failed", "error": str(e)}

    def _poll_video_status(self, video_id: str, max_wait: int = 600, poll_interval: int = 5) -> dict:
        """
        Poll the video generation status until completion or timeout.

        Args:
            video_id: The video job ID
            max_wait: Maximum time to wait in seconds (default: 10 minutes)
            poll_interval: Time between polls in seconds (default: 5 seconds)

        Returns:
            dict: Video status information
        """
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                video = self.client.videos.retrieve(video_id)

                status = video.status
                print(f"Status: {status}", end="")

                if hasattr(video, 'progress'):
                    print(f" - Progress: {video.progress}%", end="")

                print()  # New line

                if status == "completed":
                    return {
                        "status": "completed",
                        "id": video_id,
                        "video": video
                    }
                elif status == "failed":
                    error_msg = getattr(video, 'error', 'Unknown error')
                    print(f"\n[ERROR] Video generation failed!")
                    print(f"[ERROR] Error details: {error_msg}")
                    print(f"[ERROR] Video ID: {video_id}")
                    return {
                        "status": "failed",
                        "id": video_id,
                        "error": error_msg
                    }

                time.sleep(poll_interval)

            except Exception as e:
                print(f"Error polling status: {e}")
                time.sleep(poll_interval)

        return {
            "status": "timeout",
            "id": video_id,
            "error": "Video generation timed out"
        }

    def _download_video(self, video_result: dict, filename: str) -> Path:
        """
        Download the generated video.

        Args:
            video_result: The video result dictionary
            filename: Filename to save the video

        Returns:
            Path: Path to the downloaded video file
        """
        output_path = self.output_dir / filename
        video_id = video_result.get("id")

        # Use the official download_content method
        try:
            print(f"Downloading video content...")
            # variant options: "video" (default, MP4), "thumbnail", "spritesheet"
            video_content = self.client.videos.download_content(video_id, variant="video")

            with open(output_path, 'wb') as f:
                f.write(video_content.read())

            print(f"Video downloaded successfully")
            return output_path

        except Exception as e:
            print(f"[ERROR] Failed to download video: {e}")
            raise

    def generate_multiple_clips(
        self,
        prompts: List[str],
        duration: int = 12,
        resolution: str = "720p"
    ) -> List[dict]:
        """
        Generate multiple video clips from a list of prompts.

        Args:
            prompts: List of text descriptions for videos
            duration: Duration for each clip in seconds (max 12)
            resolution: Video resolution

        Returns:
            List[dict]: List of video generation results
        """
        results = []

        for i, prompt in enumerate(prompts, 1):
            print(f"\n{'='*60}")
            print(f"Generating clip {i}/{len(prompts)}")
            print(f"{'='*60}")

            result = self.generate_single_video(
                prompt=prompt,
                duration=duration,
                resolution=resolution,
                output_filename=f"clip_{i:02d}_{int(time.time())}.mp4"
            )

            results.append(result)

            if result.get("status") != "completed":
                print(f"Warning: Clip {i} failed to generate")

        return results

    def stitch_videos(self, video_paths: List[Path], output_filename: str = "final_video.mp4") -> Path:
        """
        Stitch multiple video clips together into one video.
        Requires moviepy to be installed: pip install moviepy

        Args:
            video_paths: List of paths to video files to stitch
            output_filename: Filename for the final stitched video

        Returns:
            Path: Path to the stitched video
        """
        try:
            from moviepy import VideoFileClip, concatenate_videoclips
        except ImportError:
            raise ImportError("moviepy is required for video stitching. Install with: pip install moviepy")

        print(f"\nStitching {len(video_paths)} videos together...")

        clips = []
        for path in video_paths:
            if path.exists():
                clips.append(VideoFileClip(str(path)))
            else:
                print(f"Warning: Video not found: {path}")

        if not clips:
            raise ValueError("No valid video clips to stitch")

        final_clip = concatenate_videoclips(clips)
        output_path = self.output_dir / output_filename

        final_clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac'
        )

        # Close clips to free resources
        for clip in clips:
            clip.close()
        final_clip.close()

        print(f"[SUCCESS] Stitched video saved to: {output_path}")
        return output_path


def main():
    """Example usage of the SoraVideoGenerator."""

    # Initialize generator
    generator = SoraVideoGenerator()

    # Example 1: Generate a single 12-second video
    print("Example 1: Single video generation")
    result = generator.generate_single_video(
        prompt="A majestic lion walking through the African savanna at sunset",
        duration=12,
        resolution="720p"
    )

    # Example 2: Generate multiple clips for a longer video
    print("\n\nExample 2: Multiple clips generation")
    prompts = [
        "A spaceship launching from Earth into space",
        "The spaceship traveling through a colorful nebula",
        "The spaceship approaching a distant planet",
    ]

    results = generator.generate_multiple_clips(
        prompts=prompts,
        duration=12,
        resolution="720p"
    )

    # Example 3: Stitch clips together (requires moviepy)
    print("\n\nExample 3: Stitching clips together")
    successful_clips = [
        result["local_path"]
        for result in results
        if result.get("status") == "completed" and "local_path" in result
    ]

    if successful_clips:
        try:
            final_video = generator.stitch_videos(
                successful_clips,
                output_filename="final_stitched_video.mp4"
            )
            print(f"\n[SUCCESS] All done! Final video: {final_video}")
        except ImportError as e:
            print(f"\nNote: To stitch videos, install moviepy: pip install moviepy")
    else:
        print("\nNo successful clips to stitch")


if __name__ == "__main__":
    main()
