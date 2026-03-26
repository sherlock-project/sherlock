/**
 * GET /api/v1/version
 *
 * Returns sherlock version and a list of direct Python dependencies by
 * reading pyproject.toml without spawning Python.
 */

import { Hono } from "hono";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const PYPROJECT_PATH = path.resolve(
  __dirname,
  "../../../pyproject.toml"
);

function readVersion(): { version: string; dependencies: string[] } {
  try {
    const raw = readFileSync(PYPROJECT_PATH, "utf-8");

    // Extract version from [tool.poetry] section
    const poetrySection = raw.match(/\[tool\.poetry\]([\s\S]*?)(?=\[|$)/)?.[1] ?? "";
    const versionMatch = poetrySection.match(/^version\s*=\s*"([^"]+)"/m);
    const version = versionMatch?.[1] ?? "unknown";

    // Extract runtime dependency names from [tool.poetry.dependencies]
    const depsMatch = raw.match(
      /\[tool\.poetry\.dependencies\]([\s\S]*?)(?=\[|$)/
    );
    const dependencies: string[] = [];
    if (depsMatch) {
      const block = depsMatch[1];
      for (const line of block.split("\n")) {
        const dep = line.match(/^([A-Za-z][\w-]*)\s*=/);
        if (dep && dep[1].toLowerCase() !== "python") {
          dependencies.push(dep[1]);
        }
      }
    }

    return { version, dependencies };
  } catch {
    return { version: "unknown", dependencies: [] };
  }
}

export const versionRouter = new Hono();

versionRouter.get("/", (c) => {
  const { version, dependencies } = readVersion();
  return c.json({
    success: true,
    data: {
      name: "Sherlock: Find Usernames Across Social Networks",
      version,
      pythonDependencies: dependencies,
      api: {
        version: "1.0.0",
        framework: "Hono",
      },
    },
  });
});
