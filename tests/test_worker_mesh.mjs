/**
 * Suite mesh Live Nodes + QNM-BUILD-1.0 contract.
 * Default OFF. live|locked|isolated. No Node Gate. No auto-heal. Not anonymity.
 */
import assert from "node:assert/strict";
import {
  QNM_SPEC,
  QNS_CD_SPEC,
  QNS_CD,
  MESH_DEFAULT_OFF,
  MESH_ANONYMITY_NETWORK,
  MESH_NODE_GATE,
  MESH_AUTO_HEAL,
  MESH_NOTE,
  MESH_OPS,
  MESH_PATH,
  MESH_IDENTITY,
  MESH_PRODUCT,
  alignLiveNodes,
  attachQnsCdCrossMap,
  emptyMesh,
  isMeshLiveNodesPath,
  meshOpenApiPaths,
  meshPointer,
  meshStatusLine,
  parseMeshDoc,
  publicMesh,
} from "../workers/download-tracker/src/mesh.js";
import { classifyV1Path, DEFAULT_RUNTIME_ORIGIN, doorTargetUrl, localOpFromPath } from "../workers/download-tracker/src/door.js";
import { handleRuntimeApi } from "../workers/download-tracker/src/runtime.js";
import { renderHome } from "../workers/download-tracker/src/home.js";

assert.equal(QNM_SPEC, "QNM-BUILD-1.0");
assert.equal(QNS_CD_SPEC, "QNS-CD-1.0");
assert.equal(QNS_CD.spec, "QNS-CD-1.0");
assert.equal(QNS_CD.kind, "photon QNS1 packet transfer");
assert.equal(QNS_CD.local, "qnsd");
assert.equal(QNS_CD.local_coded, "https://github.com/AzielEliab/qnm-node");
assert.equal(QNS_CD.runtime_cites, "https://github.com/AzielEliab/aziel-runtime");
assert.equal(QNS_CD.pair_custody, "https://github.com/AzielEliab/azinterface");
assert.equal(QNS_CD.softwares_tab, false);
assert.equal(QNS_CD.public_proxy, false);
assert.equal(QNS_CD.qnsd_proxy, false);
assert.equal(QNS_CD.node_gate, false);
assert.equal(QNS_CD.default_off, true);
assert.equal(QNS_CD.identity, "Aziel Eliab");
assert.match(MESH_NOTE, /QNS-CD-1\.0/);
assert.match(MESH_NOTE, /No public qnsd proxy/);
assert.equal(MESH_DEFAULT_OFF, true);
assert.equal(MESH_ANONYMITY_NETWORK, false);
assert.equal(MESH_NODE_GATE, false);
assert.equal(MESH_AUTO_HEAL, false);
assert.equal(MESH_IDENTITY, "Aziel Eliab");
assert.equal(MESH_PRODUCT, "aznet");
assert.ok(MESH_OPS.includes("status") && MESH_OPS.includes("nodes"));
assert.equal(MESH_PATH, "/v1/mesh");
assert.equal(isMeshLiveNodesPath("/v1/mesh"), true);
assert.equal(isMeshLiveNodesPath("/v1/mesh/nodes"), true);
assert.equal(isMeshLiveNodesPath("/v1/mesh/enable"), false);

const empty = emptyMesh();
assert.equal(empty.enabled, false);
assert.deepEqual(empty.rollup, { live: 0, locked: 0, isolated: 0 });
assert.equal(empty.node_gate, false);
assert.equal(empty.auto_heal, false);
assert.equal(empty.anonymity_network, false);
assert.equal(empty.identity, "Aziel Eliab");
assert.equal(empty.qns_cd_spec, "QNS-CD-1.0");
assert.equal(empty.qns_cd.spec, "QNS-CD-1.0");
assert.equal(empty.qns_cd.public_proxy, false);

const qnm = parseMeshDoc({
  spec: "QNM-BUILD-1.0",
  enabled: true,
  rollup: { live: 2, locked: 1, isolated: 3 },
  nodes: [{ id: "a" }, { id: "b" }, { id: "c" }],
});
assert.deepEqual(qnm.rollup, { live: 2, locked: 1, isolated: 3 });
assert.equal(qnm.live_nodes, 2);
assert.equal(qnm.node_gate, false);
assert.equal(qnm.auto_heal, false);

const off = parseMeshDoc({ enabled: false, live_nodes: 9, nodes: [{ id: "stale" }] });
assert.equal(off.enabled, false);
assert.equal(off.live_nodes, 0);
assert.deepEqual(off.rollup, { live: 0, locked: 0, isolated: 0 });

const pub = publicMesh(qnm);
assert.equal(pub.nodes, undefined);
assert.equal(pub.slug, "mesh");
assert.equal(pub.product, "aznet");
assert.equal(pub.qns_cd_spec, "QNS-CD-1.0");
assert.equal(pub.qns_cd.kind, "photon QNS1 packet transfer");
assert.equal(pub.enabled, true);
assert.equal(attachQnsCdCrossMap({ enabled: false }).qns_cd.spec, "QNS-CD-1.0");
assert.match(meshStatusLine(pub), /Suite mesh: on · live 2 · locked 1 · isolated 3/);
assert.match(meshStatusLine(emptyMesh()), /Suite mesh: off \(default\)\. QNM-BUILD-1\.0/);
assert.equal(alignLiveNodes({ mesh: { enabled: true, rollup: { live: 4, locked: 1, isolated: 0 } } }), 4);
assert.equal(alignLiveNodes({ mesh: { enabled: false, live_nodes: 9 } }), 0);

const pointer = meshPointer();
assert.equal(pointer.enabled_default, false);
assert.equal(pointer.rollup, "live|locked|isolated");
assert.equal(pointer.fraggate_slug, "mesh");
assert.equal(pointer.node_gate, false);
assert.equal(pointer.auto_heal, false);
assert.equal(pointer.anonymity_network, false);
assert.equal(pointer.anon_broadcast_publish_path, false);
assert.match(pointer.note, /AZBrowser is sibling software/);
assert.equal(pointer.qns_cd_spec, "QNS-CD-1.0");
assert.equal(pointer.qnsd_proxy, false);
assert.equal(pointer.softwares_tab, false);
assert.match(pointer.note, /QNS-CD-1\.0/);

assert.equal(classifyV1Path("/v1/mesh").kind, "door");
assert.equal(classifyV1Path("/v1/mesh/nodes").originPath, "/v1/mesh/nodes");
assert.equal(classifyV1Path("/v1/mesh/enable").kind, "door");
assert.equal(localOpFromPath("/v1/mesh"), null);
assert.equal(
  doorTargetUrl("/v1/mesh/nodes", "https://aznet-download-tracker.vibelock.workers.dev/v1/mesh/nodes"),
  DEFAULT_RUNTIME_ORIGIN + "/v1/mesh/nodes",
);

const html = renderHome({ views: 0, downloads: 0 });
assert.match(html, /id="meshStrip"/);
assert.match(html, /id="meshLiveCount"/);
assert.match(html, /id="meshLine"/);
assert.match(html, /QNM-BUILD-1\.0/);
assert.match(html, /QNS-CD-1\.0/);
assert.match(html, /no public qnsd proxy/);
assert.match(html, /Live Nodes/);
assert.match(html, /No Node Gate/);
assert.match(html, /No auto-heal/);
assert.match(html, /Not an anonymity network/);
assert.match(html, /\/v1\/mesh/);
assert.match(html, /Aziel Eliab only/);
assert.match(html, /AZBrowser is sibling/);
assert.doesNotMatch(html, /id="node-gate"/);
assert.doesNotMatch(html, /href="\/node-gate"/);
assert.doesNotMatch(html, /auto-heal this node/);

const fetches = [];
const previousFetch = globalThis.fetch;
globalThis.fetch = async (input, init) => {
  const url = typeof input === "string" ? input : input.url;
  fetches.push({ url, method: (init && init.method) || (input && input.method) || "GET" });
  return new Response(JSON.stringify({
    ok: true,
    enabled: false,
    mesh_default: "off",
    live_nodes: 0,
    rollup: { live: 0, locked: 0, isolated: 0 },
    proxied: true,
    origin: url,
  }), { status: 200, headers: { "content-type": "application/json; charset=utf-8" } });
};

try {
  const meshReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/mesh", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const meshRes = await handleRuntimeApi(meshReq, new URL(meshReq.url), {});
  assert.ok(meshRes, "mesh path must be handled as a door proxy");
  const meshBody = await meshRes.json();
  assert.notEqual(meshBody.code, "FG-HALLUC-TOOL");
  assert.notEqual(meshBody.op, "mesh");
  assert.equal(meshBody.ok, true);
  assert.equal(meshBody.enabled, false);
  assert.equal(meshBody.qns_cd_spec, "QNS-CD-1.0");
  assert.equal(meshBody.qns_cd.spec, "QNS-CD-1.0");
  assert.equal(meshBody.qns_cd.kind, "photon QNS1 packet transfer");
  assert.equal(meshBody.qns_cd.public_proxy, false);
  assert.equal(meshRes.headers.get("X-Aziel-Door"), "proxy");
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/mesh" && f.method === "GET"));

  fetches.length = 0;
  const enableReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/mesh/enable", {
    method: "POST",
    headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" },
    body: "{}",
  });
  const enableRes = await handleRuntimeApi(enableReq, new URL(enableReq.url), {});
  const enableBody = await enableRes.json();
  assert.notEqual(enableBody.code, "NOT_LOCAL_OP");
  assert.ok(fetches.some((f) => f.url === DEFAULT_RUNTIME_ORIGIN + "/v1/mesh/enable" && f.method === "POST"));

  const bindingFetches = [];
  const bindingEnv = {
    AZIEL_RUNTIME: {
      fetch: async (input) => {
        const url = typeof input === "string" ? input : input.url;
        bindingFetches.push(url);
        return new Response(JSON.stringify({ ok: true, via: "binding", enabled: false }), {
          headers: { "content-type": "application/json" },
        });
      },
    },
  };
  const bindReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/mesh/nodes", {
    method: "GET",
    headers: { "user-agent": "Mozilla/5.0" },
  });
  const bindRes = await handleRuntimeApi(bindReq, new URL(bindReq.url), bindingEnv);
  const bindBody = await bindRes.json();
  assert.equal(bindBody.via, "binding");
  assert.equal(bindBody.enabled, false);
  assert.equal(bindBody.qns_cd_spec, "QNS-CD-1.0");
  assert.equal(bindBody.qns_cd.qnsd_proxy, false);
  assert.ok(bindingFetches[0].endsWith("/v1/mesh/nodes"));

  const specReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/openapi.json", { method: "GET" });
  const specRes = await handleRuntimeApi(specReq, new URL(specReq.url), {});
  const spec = await specRes.json();
  assert.ok(spec.paths["/v1/mesh"]);
  assert.ok(spec.paths["/v1/mesh/nodes"]);
  assert.ok(spec.paths["/v1/mesh/enable"]);
  assert.match(spec.info.description, /QNM-BUILD-1\.0/);
  assert.match(spec.info.description, /No Node Gate/);

  const mcpReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/mcp", { method: "GET" });
  const mcpRes = await handleRuntimeApi(mcpReq, new URL(mcpReq.url), {});
  const mcp = await mcpRes.json();
  assert.equal(mcp.mesh.pointer, true);
  assert.equal(mcp.mesh.enabled_default, false);
  assert.equal(mcp.mesh.fraggate_slug, "mesh");
  assert.equal(mcp.mesh.rollup, "live|locked|isolated");
  assert.match(mcp.note, /mesh_\*/);

  const healthReq = new Request("https://aznet-download-tracker.vibelock.workers.dev/v1/health", { method: "GET" });
  const healthRes = await handleRuntimeApi(healthReq, new URL(healthReq.url), {});
  const health = await healthRes.json();
  assert.equal(health.mesh.enabled_default, false);
  assert.equal(health.mesh.identity, "Aziel Eliab");

  const openapiPaths = meshOpenApiPaths();
  assert.ok(openapiPaths["/v1/mesh"].get);
  assert.ok(openapiPaths["/v1/mesh/broadcast"].post);
} finally {
  globalThis.fetch = previousFetch;
}

console.log("worker mesh Live Nodes / QNM smoke ok");
