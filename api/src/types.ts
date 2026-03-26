/** Raw result entry from the Python bridge for a single (username, site) pair. */
export interface RawSiteResult {
  status: "Claimed" | "Available" | "Unknown" | "Illegal" | "WAF";
  url: string;
  responseTimeMs: number | null;
  context: string | null;
}

/** Raw dict keyed by site name, as returned by the Python bridge per username. */
export type RawUsernameResults = Record<string, RawSiteResult>;

/** Top-level envelope returned by the Python bridge. */
export interface BridgeResponse {
  success: boolean;
  error?: string;
  results?: Record<string, RawUsernameResults>;
  meta?: {
    totalSites: number;
    elapsedSeconds: number;
    usernames: string[];
  };
}

/** Config object sent to the Python bridge via stdin. */
export interface BridgeConfig {
  usernames: string[];
  options: {
    nsfw?: boolean;
    local?: boolean;
    sites?: string[];
    proxy?: string;
    timeout?: number;
    jsonFile?: string;
  };
}

// ── Structured API response types ─────────────────────────────────────────────

export interface ClaimedSite {
  site: string;
  url: string;
  responseTimeMs: number | null;
}

export interface ErroredSite {
  site: string;
  status: string;
  context: string | null;
}

export interface UsernameSearchResult {
  foundCount: number;
  totalChecked: number;
  found: ClaimedSite[];
  notFound: string[];
  errors: ErroredSite[];
}

export interface SearchResponseData {
  success: true;
  data: Record<string, UsernameSearchResult>;
  meta: {
    totalSites: number;
    elapsedSeconds: number;
    usernames: string[];
  };
}

export interface ErrorResponse {
  success: false;
  error: string;
}
