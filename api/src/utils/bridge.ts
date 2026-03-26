/**
 * Sherlock Python bridge utility.
 *
 * Spawns `sherlock_bridge.py` as a child process, writes JSON config to its
 * stdin, and reads the JSON result from stdout.
 */

import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import type { BridgeConfig, BridgeResponse } from "../types.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// sherlock_bridge.py lives two levels above api/src/utils/
const BRIDGE_SCRIPT = path.resolve(__dirname, "../../../sherlock_bridge.py");

// Hard wall-clock limit for the entire bridge invocation (all usernames).
// Per-username timeout is enforced inside the Python script.
const PROCESS_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

export function runSherlock(config: BridgeConfig): Promise<BridgeResponse> {
  return new Promise((resolve, reject) => {
    const python = process.env.PYTHON_EXECUTABLE ?? "python3";

    const proc = spawn(python, [BRIDGE_SCRIPT], {
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    const killer = setTimeout(() => {
      proc.kill();
      reject(new Error("Sherlock bridge process timed out after 5 minutes."));
    }, PROCESS_TIMEOUT_MS);

    proc.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString();
    });

    proc.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });

    proc.on("close", () => {
      clearTimeout(killer);

      const raw = stdout.trim();
      if (!raw) {
        reject(
          new Error(
            `Sherlock bridge produced no output. stderr: ${stderr.slice(0, 500)}`
          )
        );
        return;
      }

      try {
        resolve(JSON.parse(raw) as BridgeResponse);
      } catch {
        reject(
          new Error(
            `Failed to parse bridge output. stdout: ${raw.slice(0, 300)} | stderr: ${stderr.slice(0, 300)}`
          )
        );
      }
    });

    proc.on("error", (err) => {
      clearTimeout(killer);
      reject(new Error(`Failed to start sherlock bridge: ${err.message}`));
    });

    // Write config to bridge and close stdin to signal EOF.
    proc.stdin.write(JSON.stringify(config));
    proc.stdin.end();
  });
}
