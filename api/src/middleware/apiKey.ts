/**
 * Optional static API-key authentication middleware.
 *
 * When the API_KEY environment variable is set, every request must carry:
 *   X-API-Key: <value>
 *
 * When API_KEY is empty / not set, authentication is disabled entirely.
 */

import type { MiddlewareHandler } from "hono";

export function apiKeyAuth(): MiddlewareHandler {
  return async (c, next) => {
    const requiredKey = process.env.API_KEY;
    if (!requiredKey) {
      // Auth not configured – let the request through.
      await next();
      return;
    }

    const provided = c.req.header("x-api-key");
    if (!provided || provided !== requiredKey) {
      return c.json(
        { success: false, error: "Unauthorized: missing or invalid API key." },
        401
      );
    }

    await next();
  };
}
