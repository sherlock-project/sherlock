/**
 * POST /api/v1/search
 *
 * Run a Sherlock username search across social networks.
 *
 * Body (JSON):
 * {
 *   "usernames": ["john", "jane"],   // 1–5 usernames per request
 *   "options": {
 *     "sites":   ["GitHub","Twitter"],  // limit to specific sites
 *     "timeout": 60,                    // seconds (5–120, default 60)
 *     "proxy":   "socks5://...",        // optional proxy URL
 *     "nsfw":    false,                 // include NSFW sites
 *     "local":   true,                  // use bundled data.json (faster)
 *     "jsonFile": "https://..."         // custom site-data URL
 *   }
 * }
 */

import { Hono } from "hono";
import { zValidator } from "@hono/zod-validator";
import { z } from "zod";
import { runSherlock } from "../utils/bridge.js";
import { getSiteNames } from "../utils/sites.js";
import type {
  ClaimedSite,
  ErroredSite,
  UsernameSearchResult,
} from "../types.js";

// Usernames may include {?} placeholders (sherlock's fuzzy mode).
const USERNAME_RE = /^[a-zA-Z0-9._\-{}? ]+$/;

// Very loose proxy validation – sherlock itself will reject bad values.
const PROXY_RE = /^(https?|socks[45]):\/\/.+/;

const BodySchema = z.object({
  usernames: z
    .array(
      z
        .string()
        .min(1, "Username must not be empty.")
        .max(50, "Username must be at most 50 characters.")
        .regex(USERNAME_RE, "Username contains invalid characters.")
    )
    .min(1, "Provide at least one username.")
    .max(5, "At most 5 usernames per request."),

  options: z
    .object({
      sites: z
        .array(z.string().min(1).max(100))
        .max(100, "At most 100 sites per request.")
        .optional()
        .default([]),

      timeout: z
        .number({ invalid_type_error: "timeout must be a number." })
        .int()
        .min(5, "Minimum timeout is 5 seconds.")
        .max(120, "Maximum timeout is 120 seconds.")
        .optional()
        .default(60),

      proxy: z
        .string()
        .regex(PROXY_RE, "Invalid proxy URL. Must start with http://, https://, socks4://, or socks5://.")
        .optional(),

      nsfw: z.boolean().optional().default(false),

      local: z.boolean().optional().default(true),

      jsonFile: z
        .string()
        .url("jsonFile must be a valid URL.")
        .optional(),
    })
    .optional()
    .default({}),
});

export const searchRouter = new Hono();

searchRouter.post(
  "/",
  zValidator("json", BodySchema, (result, c) => {
    if (!result.success) {
      const messages = result.error.issues.map(
        (i) => `${i.path.join(".") || "body"}: ${i.message}`
      );
      return c.json({ success: false, error: messages }, 400);
    }
  }),
  async (c) => {
  const { usernames, options } = c.req.valid("json");

  // Validate that any requested sites actually exist in our data set.
  if (options.sites && options.sites.length > 0) {
    const knownSites = new Set(getSiteNames(true));
    const unknown = options.sites.filter((s) => !knownSites.has(s));
    if (unknown.length > 0) {
      return c.json(
        {
          success: false,
          error: `Unknown site(s): ${unknown.join(", ")}. Use GET /api/v1/sites to see valid names.`,
        },
        400
      );
    }
  }

  let bridgeResponse;
  try {
    bridgeResponse = await runSherlock({
      usernames,
      options: {
        sites: options.sites,
        timeout: options.timeout,
        proxy: options.proxy,
        nsfw: options.nsfw,
        local: options.local,
        jsonFile: options.jsonFile,
      },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Unknown bridge error.";
    return c.json({ success: false, error: msg }, 500);
  }

  if (!bridgeResponse.success) {
    return c.json({ success: false, error: bridgeResponse.error }, 500);
  }

  // ── Transform raw bridge output into the structured API response ────────────
  const data: Record<string, UsernameSearchResult> = {};

  for (const [username, siteResults] of Object.entries(
    bridgeResponse.results ?? {}
  )) {
    const found: ClaimedSite[] = [];
    const notFound: string[] = [];
    const errors: ErroredSite[] = [];

    for (const [site, result] of Object.entries(siteResults)) {
      if (site === "_error") continue;

      switch (result.status) {
        case "Claimed":
          found.push({
            site,
            url: result.url,
            responseTimeMs: result.responseTimeMs,
          });
          break;
        case "Available":
          notFound.push(site);
          break;
        default:
          errors.push({
            site,
            status: result.status,
            context: result.context,
          });
      }
    }

    // Sort found sites by response time (fastest first) for readability.
    found.sort((a, b) => (a.responseTimeMs ?? 0) - (b.responseTimeMs ?? 0));

    data[username] = {
      foundCount: found.length,
      totalChecked: found.length + notFound.length + errors.length,
      found,
      notFound,
      errors,
    };
  }

  return c.json({
    success: true,
    data,
    meta: bridgeResponse.meta,
  });
});
