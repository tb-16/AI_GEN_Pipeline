# UnboundEd Frontend (AI_GEN Pipeline)

A Vite + React single-page app that showcases the **UnboundEd** lesson builder experience for low-connectivity classrooms. It contains a mock AI workflow for generating lesson plans and downloadable micro-videos, with optional hooks into Base44 authentication and backend services.

## Highlights
- Lesson Builder tab that captures teacher context and produces scripted segments via `generateLessonPlan()` mock data.
- Video generation cards that simulate offline-ready exports with `generateVideo()`.
- Workflow and About tabs that explain how the AI-assisted pipeline operates.
- Base44 SDK integration (auth, NavigationTracker, VisualEditAgent) that can be wired up to a live backend when tokens/server details are present.
- Tailwind CSS, Radix UI primitives, react-query, and shadcn-inspired components for rapid design iteration.

## Prerequisites
- Node.js **18.18+** (Vite 6 requires the modern runtime).  
  Check with `node -v`.
- npm 9+ (ships with Node 18). Using pnpm/yarn is possible but `package-lock.json` assumes npm.

## Quick Start
```bash
cd AI_GEN_Pipeline/frontend
npm install
npm run dev
```
Then open the printed Vite URL (default `http://localhost:5173`) in your browser.

### Available npm scripts

| Script | Purpose |
| ------ | ------- |
| `npm run dev` | Start Vite dev server with hot reload. |
| `npm run build` | Produce a production-ready bundle in `dist/`. |
| `npm run preview` | Serve the `dist/` build locally (what Vercel/Netlify would run). |
| `npm run lint` / `npm run lint:fix` | Run ESLint (with React, Hooks, and unused-imports plugins). |
| `npm run typecheck` | Run `tsc` against `jsconfig.json` for JS/JSX type safety. |

## Environment configuration
Create `.env` or `.env.local` at the project root when connecting to Base44 infrastructure:

```
VITE_BASE44_APP_ID=your-app-id
VITE_BASE44_BACKEND_URL=https://api.your-base44-instance.com
# Optional: toggle legacy import support for older SDK entry points
BASE44_LEGACY_SDK_IMPORTS=false
```

- `app_id`, `server_url`, `access_token`, `from_url`, and `functions_version` can also be injected via URL query params. They are persisted in `localStorage` through `src/lib/app-params.js`.
- Leaving these values unset keeps the app in **mock demo mode** (no authentication).

## Usage summary
1. **Launch the Lesson Builder:** On the default tab, fill out country, subject, grade band, class size, connectivity constraints, and desired clip length in `TeacherContextForm`.
2. **Generate plan & scripts:** Click **“Generate Lesson Plan & Script”**. The mock generator (`src/components/utils/mockData.jsx`) fabricates a goal statement, key talking points, and per-segment scripts tailored to the submitted context.
3. **Review segments:** Each `LessonPlanPanel` segment includes narrated script, visual direction, and an estimated runtime. Use this view to refine copy before exporting.
4. **Simulate video output:** Press **“Create Offline Video”** on a segment to trigger `generateVideo()`. A placeholder entry shows file size/duration, mimicking what a real render step would return.
5. **Explore supporting tabs:** The **Teacher Workflow** tab (`WorkflowSection`) illustrates how the tool fits classroom realities, while **About** (`AboutSection`) summarizes mission and hackathon constraints.
6. **Authentication states:** When Base44 tokens are present, `AuthProvider` (`src/lib/AuthContext.jsx`) enforces login, handles “user not registered” errors, and redirects via the SDK. Without tokens you’ll stay in anonymous demo mode.

## Project structure
- `src/pages/Home.jsx`: Tabbed landing page orchestrating the main experience.
- `src/components/lesson/*`: Form, plan panel, segment card UI.
- `src/components/utils/mockData.jsx`: Replace these mocks with real API calls when the backend is ready.
- `src/api/base44Client.js`: Thin Base44 SDK client seeded with env/query params.
- `src/lib/*`: Shared context (auth, query client, navigation tracking, visual edit agent helpers).
- `src/components/ui/*`: shadcn-inspired primitives already wired to Tailwind.

## Connecting to a real backend
1. Implement actual lesson/video endpoints (e.g., via the backend folder in `AI_GEN_Pipeline`).
2. Swap the mock generators in `src/components/utils/mockData.jsx` with fetchers that call your API (consider `@tanstack/react-query` for caching).
3. Supply the Base44 credentials described above or pass them via query string when embedding the app.
4. If your backend requires authentication, ensure `base44.auth.me()` returns a user or adjust `AuthContext` to handle your scheme.

## Deployment tips
- Run `npm run build`; the output in `dist/` is static and can be hosted on Netlify, Vercel, S3, etc.
- If embedding inside another Base44 product, keep the query-param bootstrap in place so the host can inject credentials.
- For debugging noisy plugin logs, adjust `logLevel` in `vite.config.js` (currently `error`).

## Troubleshooting
- **Blank screen after login redirect:** Confirm the query params include a valid `access_token` and that CORS is allowed for your `VITE_BASE44_BACKEND_URL`.
- **Styles missing:** Tailwind is imported via `src/index.css` and `App.css`. Ensure PostCSS/Tailwind config files remain at the repo root and restart Vite after edits.
- **Path alias errors:** The alias `@/* -> src/*` is configured in `jsconfig.json`. Most IDEs pick it up automatically; if not, re-open the folder or re-run your type tooling.

With the README updated, teammates now have everything needed to run, iterate, and eventually connect this frontend to the AI lesson generation pipeline. Happy building!


