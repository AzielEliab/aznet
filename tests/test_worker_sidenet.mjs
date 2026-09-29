/**
 * GET /v1/sidenet is a local read. It is not a FragGate catalog op and it does not proxy.
 */
import assert from "node:assert/strict";
import { FRAGGATE_LIVE_OPS, handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";
import { sidenetSurface } from "../workers/download-tracker/src/sidenet.js";

const fetches = [];
const previousFetch = globalThis.fetch;
globalThis.fetch = async (input, init) => {
  const url = typeof input === "string" ? input : input.url;
  fetches.push({ url, method: (init && init.method) || "GET" });
  return new Response(JSON.stringify({ ok: true, proxied: true }), {
    status: 200,
    headers: { "content-type": "application/json" },
  });
};

try {
  const doc = sidenetSurface();
  assert.equal(doc.spec, "AZN-SIDENET-1.0");
  assert.equal(doc.naming_lock.sidenet, "aznet");
  assert.equal(doc.public_icann, false);
  assert.equal(doc.icann_registration, false);
  assert.equal(doc.second_door, false);
  assert.equal(doc.softwares_frozen, true);
  assert.equal(doc.sidenet_is_catalog_op, false);
  assert.equal(doc.qnm.bearer_status, "SLOT");
  assert.equal(doc.independent_live_shelves, 0);
  assert.equal(doc.multi_survival_complete, false);
  assert.ok(!doc.l0.ops.includes("sidenet"));
  assert.ok(!FRAGGATE_LIVE_OPS.includes("sidenet"));
  assert.deepEqual([...FRAGGATE_LIVE_OPS], doc.l0.ops);

  fetches.length = 0;
  const req = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/sidenet", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const res = await handleRuntimeApi(req, new URL(req.url), {});
  assert.equal(res.status, 200);
  const body = await res.json();
  assert.equal(body.spec, "AZN-SIDENET-1.0");
  assert.equal(body.naming_lock.sidenet, "aznet");
  assert.equal(fetches.length, 0);

  const healthReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/health", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const health = await (await handleRuntimeApi(healthReq, new URL(healthReq.url), {})).json();
  assert.equal(health.sidenet_is_catalog_op, false);
  assert.equal(health.sidenet_path, "/v1/sidenet");
  assert.ok(!health.fraggate_live_ops.includes("sidenet"));

  const openapiReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/openapi.json", {
    method: "GET",
  });
  const openapi = await (await handleRuntimeApi(openapiReq, new URL(openapiReq.url), {})).json();
  assert.ok(openapi.paths["/v1/sidenet"].get);
  assert.ok(openapi.paths["/v1/fraggate/call"].post);

  fetches.length = 0;
  const callReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/fraggate/call", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: JSON.stringify({ slug: "aznet", op: "health", payload: {} }),
  });
  const callRes = await handleRuntimeApi(callReq, new URL(callReq.url), {});
  const callBody = await callRes.json();
  assert.equal(callBody.proxied, true);
  assert.equal(fetches.length, 1);
} finally {
  globalThis.fetch = previousFetch;
}

console.log("worker sidenet smoke ok");
