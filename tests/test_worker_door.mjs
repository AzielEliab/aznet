/**
 * Prove FragGate / runtime door paths are proxied — never local ops.
 * GET|POST /mcp is a pointer (never 404) to slug=aznet on aziel-runtime.
 */
import assert from "node:assert/strict";
import {
  classifyV1Path,
  DEFAULT_RUNTIME_ORIGIN,
  doorTargetUrl,
  localOpFromPath,
  mapDoorPath,
} from "../workers/download-tracker/src/door.js";
import { handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";

assert.deepEqual(classifyV1Path("/v1/fraggate/call"), {
  kind: "door",
  path: "/v1/fraggate/call",
  originPath: "/v1/fraggate/call",
});
assert.deepEqual(classifyV1Path("/v1/fraggate/list"), {
  kind: "door",
  path: "/v1/fraggate/list",
  originPath: "/v1/fraggate/list",
});
assert.deepEqual(classifyV1Path("/v1/fraggate/describe"), {
  kind: "door",
  path: "/v1/fraggate/describe",
  originPath: "/v1/fraggate/describe",
});
assert.deepEqual(classifyV1Path("/v1/fraggate/verify"), {
  kind: "door",
  path: "/v1/fraggate/verify",
  originPath: "/v1/fraggate/verify",
});
assert.deepEqual(classifyV1Path("/v1/runtime/list"), {
  kind: "door",
  path: "/v1/runtime/list",
  originPath: "/v1/fraggate/list",
});
assert.deepEqual(classifyV1Path("/v1/mesh"), {
  kind: "door",
  path: "/v1/mesh",
  originPath: "/v1/mesh",
});
assert.deepEqual(classifyV1Path("/v1/mesh/nodes"), {
  kind: "door",
  path: "/v1/mesh/nodes",
  originPath: "/v1/mesh/nodes",
});
assert.equal(localOpFromPath("/v1/mesh"), null);
assert.deepEqual(classifyV1Path("/v1/pair_status"), {
  kind: "local",
  path: "/v1/pair_status",
  op: "pair_status",
});
assert.deepEqual(classifyV1Path("/v1/garden_list"), {
  kind: "local",
  path: "/v1/garden_list",
  op: "garden_list",
});
assert.equal(localOpFromPath("/v1/fraggate/call"), null);
assert.equal(localOpFromPath("/v1/pair_status"), "pair_status");
assert.equal(mapDoorPath("/v1/runtime/list"), "/v1/fraggate/list");
assert.equal(
  doorTargetUrl("/v1/fraggate/call", "https://aznet-download-tracker.vibelock.workers.dev/v1/fraggate/call"),
  DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/call",
);
assert.equal(classifyV1Path("/v1/not/a/door").kind, "multi");
assert.equal(classifyV1Path("/count").kind, "none");

const fetches = [];
const previousFetch = globalThis.fetch;
globalThis.fetch = async (input, init) => {
  const url = typeof input === "string" ? input : input.url;
  fetches.push({ url, method: (init && init.method) || (input && input.method) || "GET" });
  return new Response(JSON.stringify({ ok: true, door: "fraggate", proxied: true, origin: url }), {
    status: 200,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
};

try {
  const mcpGet = new Request("https://aznet-download-tracker.vibelock.workers.dev/mcp", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const mcpGetRes = await handleRuntimeApi(mcpGet, new URL(mcpGet.url), {});
  assert.ok(mcpGetRes, "/mcp GET must not 404");
  assert.equal(mcpGetRes.status, 200);
  const mcpGetBody = await mcpGetRes.json();
  assert.equal(mcpGetBody.error, "not a product MCP");
  assert.equal(mcpGetBody.slug, "aznet");
  assert.equal(mcpGetBody.door, "fraggate");
  assert.ok(String(mcpGetBody.agent_path).includes("/v1/fraggate/call"));

  const mcpPost = new Request("https://aznet-download-tracker.vibelock.workers.dev/mcp", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list" }),
  });
  const mcpPostRes = await handleRuntimeApi(mcpPost, new URL(mcpPost.url), {});
  assert.ok(mcpPostRes, "/mcp POST must not 404");
  assert.equal(mcpPostRes.status, 200);
  const mcpPostBody = await mcpPostRes.json();
  assert.equal(mcpPostBody.slug, "aznet");
  assert.equal(mcpPostBody.door, "fraggate");

  const callReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/fraggate/call", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: JSON.stringify({ slug: "aznet", op: "health", payload: {} }),
  });
  const callRes = await handleRuntimeApi(callReq, new URL(callReq.url), {});
  assert.ok(callRes, "door path must be handled");
  const callBody = await callRes.json();
  assert.notEqual(callBody.code, "FG-HALLUC-TOOL");
  assert.equal(callBody.ok, true);
  assert.equal(callBody.proxied, true);
  assert.equal(callRes.headers.get("X-Aziel-Door"), "proxy");
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/call" && f.method === "POST"));

  fetches.length = 0;
  const listReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/runtime/list", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const listRes = await handleRuntimeApi(listReq, new URL(listReq.url), {});
  const listBody = await listRes.json();
  assert.equal(listBody.ok, true);
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/list"));

  fetches.length = 0;
  const describeReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/fraggate/describe?slug=aznet", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  await handleRuntimeApi(describeReq, new URL(describeReq.url), {});
  assert.ok(fetches.some((f) => String(f.url).startsWith(DEFAULT_RUNTIME_ORIGIN + "/v1/fraggate/describe")));

  const bindingFetches = [];
  const bindingEnv = {
    AZIEL_RUNTIME: {
      fetch: async (input) => {
        const url = typeof input === "string" ? input : input.url;
        bindingFetches.push(url);
        return new Response(JSON.stringify({ ok: true, via: "binding" }), {
          headers: { "content-type": "application/json" },
        });
      },
    },
  };
  const bindReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/fraggate/verify", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ slug: "aznet" }),
  });
  const bindRes = await handleRuntimeApi(bindReq, new URL(bindReq.url), bindingEnv);
  const bindBody = await bindRes.json();
  assert.equal(bindBody.via, "binding");
  assert.ok(bindingFetches[0].endsWith("/v1/fraggate/verify"));

  const pairReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/pair_status", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: JSON.stringify({ azbrowser: "https://github.com/AzielEliab/azbrowser" }),
  });
  const pairRes = await handleRuntimeApi(pairReq, new URL(pairReq.url), {});
  const pairBody = await pairRes.json();
  assert.equal(pairBody.pair_status, "PAIRED");
  assert.ok(pairBody.receipt);

  const gardenReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/garden_list", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const gardenRes = await handleRuntimeApi(gardenReq, new URL(gardenReq.url), {});
  const gardenBody = await gardenRes.json();
  assert.ok(Array.isArray(gardenBody.cards));

  const healthReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/health", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const healthRes = await handleRuntimeApi(healthReq, new URL(healthReq.url), {});
  const healthBody = await healthRes.json();
  assert.equal(healthBody.ok, true);
  assert.equal(healthBody.product, "aznet");
  assert.ok(healthBody.fraggate_live_ops.includes("pair_status"));
  assert.ok(!healthBody.fraggate_live_ops.includes("doctor"));

  const multiReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/not/a/door", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: "{}",
  });
  const multiRes = await handleRuntimeApi(multiReq, new URL(multiReq.url), {});
  const multiBody = await multiRes.json();
  assert.equal(multiBody.code, "NOT_LOCAL_OP");

  for (const path of ["/count", "/stats", "/download", "/"]) {
    const req = new Request("https://aznet-download-tracker.vibelock.workers.dev" + path, { method: "GET" });
    const res = await handleRuntimeApi(req, new URL(req.url), {});
    assert.equal(res, null, path + " must stay on the download tracker, not the runtime router");
  }
} finally {
  globalThis.fetch = previousFetch;
}

console.log("worker door proxy smoke ok");
