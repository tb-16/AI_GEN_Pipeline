export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

/**
 * Call the backend educational video pipeline.
 *
 * The caller should pass the exact values computed in `TeacherContextForm`:
 *  - lessonRequest: combined Subject + Topic/Concept + Level text
 *  - numScenes: derived from the preferred video length slider
 *  - graphProportion: mapped from the Graph Frequency select
 *  - outputFilename: the desired output filename (optional)
 */
export async function generatePipelineVideo({ lessonRequest, numScenes, graphProportion, outputFilename }) {
  const response = await fetch(`${BACKEND_URL}/generate-video`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      lessonRequest,
      numScenes,
      graphProportion,
      outputFilename,
    }),
  });

  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`Backend error (${response.status}): ${text || response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch the list of all generated videos from the backend.
 * Returns videos sorted by creation time (newest first).
 */
export async function listVideos() {
  const response = await fetch(`${BACKEND_URL}/list-videos`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch videos: ${response.statusText}`);
  }
  
  return response.json();
}

export async function clearVideos() {
  const response = await fetch(`${BACKEND_URL}/clear-videos`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`Failed to clear videos: ${text || response.statusText}`);
  }

  return response.json();
}

