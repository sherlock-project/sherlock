/**
 * Site list utility.
 *
 * Reads the bundled sherlock data.json directly (pure Node.js, no Python),
 * so the /sites endpoint is fast and has zero Python startup overhead.
 */

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const DATA_JSON_PATH = path.resolve(
  __dirname,
  "../../../sherlock_project/resources/data.json"
);

export interface SiteEntry {
  name: string;
  urlMain: string;
  url: string;
  errorType: string;
  isNSFW: boolean;
  tags?: string[];
}

let _cache: SiteEntry[] | null = null;

function load(): SiteEntry[] {
  if (_cache) return _cache;

  const raw = readFileSync(DATA_JSON_PATH, "utf-8");
  const data = JSON.parse(raw) as Record<string, Record<string, unknown>>;

  _cache = Object.entries(data)
    .filter(([key]) => key !== "$schema")
    .map(([name, info]) => ({
      name,
      urlMain: String(info.urlMain ?? ""),
      url: String(info.url ?? ""),
      errorType: String(info.errorType ?? ""),
      isNSFW: Boolean(info.isNSFW ?? false),
      tags: Array.isArray(info.tags)
        ? (info.tags as string[])
        : undefined,
    }));

  return _cache;
}

export function getSites(opts: {
  nsfw?: boolean;
  filter?: string;
}): SiteEntry[] {
  let sites = load();

  if (!opts.nsfw) {
    sites = sites.filter((s) => !s.isNSFW);
  }

  if (opts.filter) {
    const q = opts.filter.toLowerCase();
    sites = sites.filter((s) => s.name.toLowerCase().includes(q));
  }

  return sites;
}

export function getSiteNames(nsfw = false): string[] {
  return getSites({ nsfw }).map((s) => s.name);
}
