import asyncio
import os
import shutil
import sys
import time
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from educational_video_pipeline_openai_only import EducationalVideoPipelineOpenAI


app = FastAPI(title="Educational Video Pipeline API")

# Allow the Vite dev server (frontend) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated videos as static files so the frontend can play them
VIDEOS_DIR = Path("generated_videos")
VIDEOS_DIR.mkdir(exist_ok=True)
app.mount("/videos", StaticFiles(directory=str(VIDEOS_DIR)), name="videos")

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in {"1", "true", "yes"}
DEMO_VIDEO_PATH = Path(__file__).parent / "demo" / "poverty_reduction.mp4"

OWID_SERVER_PATH = Path(__file__).parent / "OWIDChart" / "server.py"
owid_process: Optional[asyncio.subprocess.Process] = None


async def _log_process_output(process: asyncio.subprocess.Process) -> None:
    assert process.stdout is not None
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        print(f"[OWID Server] {line.decode(errors='ignore').rstrip()}")


@app.on_event("startup")
async def start_owid_server() -> None:
    global owid_process
    if not OWID_SERVER_PATH.exists():
        print(f"[OWID Server] Skipping start; {OWID_SERVER_PATH} not found.")
        return

    print(f"[OWID Server] Starting MCP server ({OWID_SERVER_PATH})...")
    owid_process = await asyncio.create_subprocess_exec(
        sys.executable,
        str(OWID_SERVER_PATH),
        cwd=str(OWID_SERVER_PATH.parent),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    asyncio.create_task(_log_process_output(owid_process))


@app.on_event("shutdown")
async def stop_owid_server() -> None:
    global owid_process
    if owid_process:
        if owid_process.returncode is None:
            print("[OWID Server] Terminating MCP server...")
            owid_process.terminate()
            try:
                await asyncio.wait_for(owid_process.wait(), timeout=10)
            except asyncio.TimeoutError:
                owid_process.kill()
        owid_process = None


class GenerateVideoRequest(BaseModel):
    lessonRequest: str
    numScenes: int
    graphProportion: float
    outputFilename: Optional[str] = None


class GenerateVideoResponse(BaseModel):
    status: str
    finalVideoPath: Optional[str] = None
    videoUrl: Optional[str] = None
    elapsedTime: Optional[float] = None
    error: Optional[str] = None


class VideoFile(BaseModel):
    filename: str
    url: str
    size: int
    created: float


class ClearVideosResponse(BaseModel):
    deletedVideos: List[str]
    deletedScenes: List[str]
    deletedGraphs: List[str]


async def run_demo_generation(output_filename: Optional[str]) -> GenerateVideoResponse:
    if not DEMO_VIDEO_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Demo video not found at {DEMO_VIDEO_PATH}")

    print("[DEMO MODE] Simulating generation pipeline...")
    start_time = time.time()
    await asyncio.sleep(15)

    # Always publish the demo asset under its canonical name so the frontend sees a consistent file.
    if output_filename and output_filename != DEMO_VIDEO_PATH.name:
        print(f"[DEMO MODE] Ignoring requested filename '{output_filename}' and using demo asset name.")

    target_name = DEMO_VIDEO_PATH.name
    target_path = VIDEOS_DIR / target_name

    # Replace previous demo output so the UI always points to the same file.
    if target_path.exists():
        target_path.unlink()

    shutil.copy2(DEMO_VIDEO_PATH, target_path)
    elapsed_time = time.time() - start_time
    print(f"[DEMO MODE] Copied demo video to {target_path}")

    return GenerateVideoResponse(
        status="completed",
        finalVideoPath=str(target_path),
        videoUrl=f"/videos/{target_path.name}",
        elapsedTime=elapsed_time,
    )


@app.post("/generate-video", response_model=GenerateVideoResponse)
async def generate_video_endpoint(payload: GenerateVideoRequest) -> GenerateVideoResponse:
    """
    Trigger the educational video pipeline.

    This endpoint is called by the frontend when the teacher clicks
    "Generate Lesson Plan & Script". The frontend has already:
      - built `lessonRequest` from the Subject + Topic/Concept + Level fields
      - computed `numScenes` from the preferred video length slider
      - mapped the graph frequency select to `graphProportion`
    """
    if DEMO_MODE:
        return await run_demo_generation(payload.outputFilename)

    pipeline = EducationalVideoPipelineOpenAI()

    result = await pipeline.generate_video(
        lesson_request=payload.lessonRequest,
        output_filename=payload.outputFilename or "output.mp4",
        num_scenes=payload.numScenes,
        graph_proportion=payload.graphProportion,
        enable_graphs=True,  # internally disabled when graph_proportion == 0.0
    )

    if result.get("status") == "completed":
        final_path = Path(result.get("final_video_path"))
        # We mount the whole `generated_videos` directory at /videos,
        # so expose just the file name as the URL component.
        video_url = f"/videos/{final_path.name}" if final_path.name else None
        return GenerateVideoResponse(
            status="completed",
            finalVideoPath=str(result.get("final_video_path")),
            videoUrl=video_url,
            elapsedTime=result.get("elapsed_time"),
        )

    return GenerateVideoResponse(
        status="failed",
        error=result.get("error", "Unknown error"),
    )


@app.get("/list-videos")
async def list_videos_endpoint():
    """
    List all generated videos sorted by creation time (newest first).
    Returns a list of video files with their metadata.
    """
    videos = []
    for video_file in VIDEOS_DIR.glob("*.mp4"):
        if video_file.is_file():
            stat = video_file.stat()
            videos.append(
                VideoFile(
                    filename=video_file.name,
                    url=f"/videos/{video_file.name}",
                    size=stat.st_size,
                    created=stat.st_mtime,
                )
            )
    
    # Sort by creation time, newest first
    videos.sort(key=lambda v: v.created, reverse=True)
    return {"videos": videos}


@app.delete("/clear-videos", response_model=ClearVideosResponse)
async def clear_videos_endpoint():
    """
    Delete generated assets:
      1. All .mp4 and .json in `generated_videos/`
      2. All .mp4 and .mp3 in `generated_videos/scenes/`
      3. All .png in `generated_videos/graphs/`
    """
    deleted_videos: List[str] = []
    deleted_scenes: List[str] = []
    deleted_graphs: List[str] = []

    def delete_matching_files(directory: Path, patterns: List[str], collector: List[str]) -> None:
        for pattern in patterns:
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        collector.append(str(file_path.name))
                    except OSError as exc:
                        raise HTTPException(status_code=500, detail=f"Failed to delete {file_path}: {exc}") from exc

    delete_matching_files(VIDEOS_DIR, ["*.mp4", "*.json"], deleted_videos)
    delete_matching_files(VIDEOS_DIR / "scenes", ["*.mp4", "*.mp3"], deleted_scenes)
    delete_matching_files(VIDEOS_DIR / "graphs", ["*.png"], deleted_graphs)

    return ClearVideosResponse(
        deletedVideos=deleted_videos,
        deletedScenes=deleted_scenes,
        deletedGraphs=deleted_graphs,
    )


if __name__ == "__main__":
    # Simple dev server runner: `python api_server.py`
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


