/**
 * Sherlock Hono API
 *
 * Entry point. Configures middleware, mounts routes, and starts the server.
 *
 * Environment variables (see .env.example):
 *   PORT                  TCP port (default: 3000)
 *   ALLOWED_ORIGINS       Comma-separated CORS origins (default: *)
 *   API_KEY               Static API key; leave blank to disable auth
 *   PYTHON_EXECUTABLE     Python binary path (default: python3)
 *   RATE_LIMIT_MAX        Max requests per window per IP (default: 30)
 *   RATE_LIMIT_WINDOW_MS  Window in ms (default: 60000)
 */

import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { cors } from "hono/cors";
import { secureHeaders } from "hono/secure-headers";
import { logger } from "hono/logger";
import { prettyJSON } from "hono/pretty-json";
import { requestId } from "hono/request-id";

import { rateLimit } from "./middleware/rateLimit.js";
import { apiKeyAuth } from "./middleware/apiKey.js";
import { healthRouter } from "./routes/health.js";
import { versionRouter } from "./routes/version.js";
import { sitesRouter } from "./routes/sites.js";
import { searchRouter } from "./routes/search.js";

const app = new Hono();

// ── Global middleware ──────────────────────────────────────────────────────────

app.use("*", requestId());
app.use("*", logger());
app.use("*", secureHeaders());
app.use(
  "*",
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(",").map((o) => o.trim()) ?? "*",
    allowMethods: ["GET", "POST", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization", "X-API-Key"],
    exposeHeaders: [
      "X-RateLimit-Limit",
      "X-RateLimit-Remaining",
      "X-RateLimit-Reset",
      "X-Request-Id",
    ],
  })
);
app.use("*", prettyJSON());

// Rate limiting applied before auth so the rate counter always increments.
app.use("*", rateLimit({}));

// Optional API-key authentication (skip the health endpoint).
app.use("/api/*", apiKeyAuth());

// ── Routes ─────────────────────────────────────────────────────────────────────

app.route("/health", healthRouter);
app.route("/api/v1/version", versionRouter);
app.route("/api/v1/sites", sitesRouter);
app.route("/api/v1/search", searchRouter);

// Root redirect to docs hint
app.get("/", (c) =>
  c.json({
    name: "sherlock-api",
    description: "REST API for Sherlock username search",
    version: "1.0.0",
    endpoints: {
      health: "GET /health",
      version: "GET /api/v1/version",
      sites: "GET /api/v1/sites",
      search: "POST /api/v1/search",
    },
    docs: "See README.md for full API documentation.",
  })
);

// ── Error handlers ─────────────────────────────────────────────────────────────

app.notFound((c) =>
  c.json({ success: false, error: `Route not found: ${c.req.method} ${c.req.path}` }, 404)
);

app.onError((err, c) => {
  console.error("[error]", err);
  return c.json({ success: false, error: "Internal server error." }, 500);
});

// ── Server bootstrap ───────────────────────────────────────────────────────────

const port = parseInt(process.env.PORT ?? "3000", 10);

serve({ fetch: app.fetch, port }, (info) => {
  console.log(`\nSherlock API listening on http://localhost:${info.port}`);
  console.log(`  Health : http://localhost:${info.port}/health`);
  console.log(`  Version: http://localhost:${info.port}/api/v1/version`);
  console.log(`  Sites  : http://localhost:${info.port}/api/v1/sites`);
  console.log(`  Search : POST http://localhost:${info.port}/api/v1/search\n`);
});

export default app;
