/**
 * GET /api/v1/sites
 *
 * Returns the list of supported social-network sites.
 *
 * Query parameters:
 *   nsfw=true          Include NSFW sites (default: false)
 *   filter=<string>    Case-insensitive substring search on site name
 *   page=<number>      Page number (1-based, default: 1)
 *   limit=<number>     Page size (1–200, default: 100)
 */

import { Hono } from "hono";
import { z } from "zod";
import { zValidator } from "@hono/zod-validator";
import { getSites } from "../utils/sites.js";

const QuerySchema = z.object({
  nsfw: z
    .enum(["true", "false", "1", "0"])
    .optional()
    .transform((v) => v === "true" || v === "1"),
  filter: z.string().max(100).optional(),
  page: z
    .string()
    .optional()
    .transform((v) => Math.max(1, parseInt(v ?? "1", 10) || 1)),
  limit: z
    .string()
    .optional()
    .transform((v) => Math.min(200, Math.max(1, parseInt(v ?? "100", 10) || 100))),
});

export const sitesRouter = new Hono();

sitesRouter.get(
  "/",
  zValidator("query", QuerySchema, (result, c) => {
    if (!result.success) {
      const messages = result.error.issues.map(
        (i) => `${i.path.join(".") || "query"}: ${i.message}`
      );
      return c.json({ success: false, error: messages }, 400);
    }
  }),
  (c) => {
  const { nsfw, filter, page, limit } = c.req.valid("query");

  const all = getSites({ nsfw, filter });
  const total = all.length;
  const totalPages = Math.ceil(total / limit);
  const offset = (page - 1) * limit;
  const items = all.slice(offset, offset + limit);

  return c.json({
    success: true,
    data: items,
    pagination: {
      page,
      limit,
      total,
      totalPages,
    },
  });
});
