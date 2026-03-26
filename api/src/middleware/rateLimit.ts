/**
 * Simple in-memory rate limiter middleware for Hono.
 *
 * Tracks request counts per IP address within a sliding window.
 * Not suitable for multi-process deployments; for those, swap out the
 * backing store for Redis / Upstash.
 */

import type { MiddlewareHandler } from "hono";

interface Window {
  count: number;
  resetAt: number;
}

const store = new Map<string, Window>();

// Periodically evict stale entries so the map doesn't grow forever.
setInterval(() => {
  const now = Date.now();
  for (const [key, win] of store) {
    if (win.resetAt < now) store.delete(key);
  }
}, 60_000);

export function rateLimit(opts: {
  max?: number;
  windowMs?: number;
}): MiddlewareHandler {
  const max = opts.max ?? parseInt(process.env.RATE_LIMIT_MAX ?? "30", 10);
  const windowMs =
    opts.windowMs ??
    parseInt(process.env.RATE_LIMIT_WINDOW_MS ?? "60000", 10);

  return async (c, next) => {
    // Prefer X-Forwarded-For when running behind a reverse proxy.
    const ip =
      c.req.header("x-forwarded-for")?.split(",")[0]?.trim() ??
      c.req.header("x-real-ip") ??
      "unknown";

    const now = Date.now();
    let win = store.get(ip);

    if (!win || win.resetAt < now) {
      win = { count: 0, resetAt: now + windowMs };
      store.set(ip, win);
    }

    win.count++;

    c.res.headers.set("X-RateLimit-Limit", String(max));
    c.res.headers.set(
      "X-RateLimit-Remaining",
      String(Math.max(0, max - win.count))
    );
    c.res.headers.set("X-RateLimit-Reset", String(Math.ceil(win.resetAt / 1000)));

    if (win.count > max) {
      return c.json(
        {
          success: false,
          error: "Too many requests. Please slow down.",
        },
        429
      );
    }

    await next();
  };
}
