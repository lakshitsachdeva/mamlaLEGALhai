import test from "node:test";
import assert from "node:assert/strict";
import {
  analyzeDocument,
  classifyModality,
  comparePolicy,
  compareVersions,
  evidenceGraph,
} from "../dist/js/engine.js";

const gdpr = "In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours after having become aware of it, notify the personal data breach to the supervisory authority, unless the breach is unlikely to result in a risk to the rights and freedoms of natural persons.";

test("classifies normative modality and epistemic may-not separately", () => {
  assert.equal(classifyModality("The provider must retain logs.").label, "OBLIGATION");
  assert.equal(classifyModality("The provider must not disclose secrets.").label, "PROHIBITION");
  assert.equal(classifyModality("Records may not be complete.").label, "INFORMATION");
});

test("extracts an evidence-linked deadline and exception", () => {
  const analysis = analyzeDocument(gdpr, { sourceId: "eur-lex://gdpr/33", section: "Article 33" });
  const record = analysis.normative[0];
  assert.equal(record.modality, "OBLIGATION");
  assert.match(record.actor, /controller/i);
  assert.match(record.deadline, /72 hours/i);
  assert.match(record.exception, /unlikely/i);
  assert.equal(record.sourceId, "eur-lex://gdpr/33");
  assert.equal(analysis.summary.citationIntegrity, 1);
});

test("flags a slower policy deadline as a mismatch", () => {
  const policy = "The controller shall notify the supervisory authority no later than 96 hours after confirming a reportable breach.";
  const result = comparePolicy(gdpr, policy);
  assert.equal(result.outcome, "POTENTIAL_MISMATCH");
  assert.ok(result.dimensions.find((d) => d.id === "timing").score < 1);
});

test("detects modified and added obligations across versions", () => {
  const before = "The organization shall review accounts every 90 days.";
  const after = "The organization shall review accounts every 60 days. Dormant accounts must be disabled immediately.";
  const result = compareVersions(before, after);
  assert.ok(result.changes.some((change) => change.type === "MODIFIED"));
  assert.ok(result.changes.some((change) => change.type === "ADDED"));
  assert.ok(result.criticalCount >= 1);
});

test("builds a navigable evidence graph", () => {
  const record = analyzeDocument(gdpr).normative[0];
  const graph = evidenceGraph(record);
  assert.ok(graph.nodes.some((node) => node.id === "source"));
  assert.ok(graph.nodes.some((node) => node.id === "obligation"));
  assert.ok(graph.edges.some((edge) => edge.label === "asserts"));
});

