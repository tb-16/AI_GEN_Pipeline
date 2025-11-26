from typing import Optional
from pathlib import Path

from fastapi import FastAPI
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


if __name__ == "__main__":
    # Simple dev server runner: `python api_server.py`
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


