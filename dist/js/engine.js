/**
 * RegulaTrace research prototype engine.
 *
 * The engine intentionally keeps every prediction traceable. It is a transparent
 * lexical baseline, not a legal decision-maker. The UI exposes its evidence,
 * confidence, and failure states so it can later be compared with learned models.
 */

export const ENGINE_VERSION = "0.4.0-research";

const MODALITY_PATTERNS = [
  { label: "PROHIBITION", re: /\b(must\s+not|shall\s+not|may\s+not|is\s+prohibited\s+from|are\s+prohibited\s+from|is\s+forbidden\s+to)\b/i, weight: 0.98 },
  { label: "OBLIGATION", re: /\b(must|shall|is\s+required\s+to|are\s+required\s+to|has\s+to|have\s+to|is\s+obliged\s+to)\b/i, weight: 0.96 },
  { label: "RECOMMENDATION", re: /\b(should|ought\s+to|is\s+recommended\s+to|are\s+encouraged\s+to)\b/i, weight: 0.88 },
  { label: "PERMISSION", re: /\b(may|is\s+permitted\s+to|are\s+permitted\s+to|is\s+allowed\s+to)\b/i, weight: 0.90 },
];

const DEADLINE_PATTERNS = [
  /\b(?:no|not)\s+later\s+than\s+\d+\s+(?:hours?|days?|weeks?|months?|years?)(?:\s+after\s+[^,.;]+)?/i,
  /\bwithin\s+\d+\s+(?:hours?|days?|weeks?|months?|years?)(?:\s+(?:of|after|from)\s+[^,.;]+)?/i,
  /\bat\s+least\s+(?:once\s+)?every\s+\d+\s+(?:days?|weeks?|months?|years?)/i,
  /\bevery\s+\d+\s+(?:days?|weeks?|months?|years?)/i,
  /\bwithout\s+undue\s+delay/i,
  /\b(?:daily|weekly|monthly|quarterly|annually|immediately|promptly)\b/i,
  /\bas\s+soon\s+as\s+(?:practicable|possible)/i,
  /\bbefore\s+[^,.;]+/i,
];

const CONDITION_RE = /\b(?:if|when|where|whenever|in\s+the\s+event\s+that|provided\s+that)\s+([^.;]+)/i;
const EXCEPTION_RE = /\b(?:unless|except(?:\s+where|\s+when|\s+for)?|save\s+where|other\s+than)\s+([^.;]+)/i;
const CROSS_REF_RE = /\b(?:Article|Section|Clause|Paragraph|Annex)\s+[A-Za-z0-9().-]+/gi;
const SEVERITY_TERMS = /\b(?:breach|penalty|fine|sanction|suspend|revoke|incident|risk|harm|rights|security|safety)\b/i;
const STOPWORDS = new Set("a an the and or but if then than of to for from by with without in on at as is are was were be been being this that these those it its their they them shall should must may not no later where when which who whom into any all each every such under over".split(" "));

function clean(text = "") {
  return text.replace(/\s+/g, " ").replace(/^[-–—•\d.)\s]+/, "").trim();
}

function hash(input) {
  let h = 2166136261;
  for (let i = 0; i < input.length; i += 1) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(36).toUpperCase().padStart(7, "0");
}

export function segmentClauses(text = "") {
  const normalized = text
    .replace(/\r/g, "")
    .replace(/\n{2,}/g, "\n")
    .replace(/([.;!?])\s+(?=[A-Z(\[])/g, "$1\n")
    .replace(/;\s+(?=(?:and|or|the|a|an|each|every|where|when|if|unless|provided)\b)/gi, ";\n");

  return normalized
    .split(/\n+/)
    .map(clean)
    .filter((part) => part.length >= 12)
    .flatMap((part) => {
      const numbered = part.split(/(?=\s*\([a-z0-9ivx]+\)\s+)/i).map(clean).filter((x) => x.length >= 12);
      return numbered.length > 1 ? numbered : [part];
    });
}

export function classifyModality(clause = "") {
  // "May not" is often epistemic (uncertainty), not a legal prohibition.
  // Keep these cases out of the prohibition bucket so the review queue can
  // distinguish "records may not be complete" from "records may not be sold".
  if (/\bmay\s+not\s+(?:be|have\s+been)\s+(?:available|complete|known|accurate|possible|sufficient|reliable|representative|applicable)\b/i.test(clause)) {
    return { label: "INFORMATION", cue: "may not (epistemic)", index: clause.search(/\bmay\s+not\b/i), confidence: 0.84 };
  }
  for (const pattern of MODALITY_PATTERNS) {
    const match = clause.match(pattern.re);
    if (match) return { label: pattern.label, cue: match[0], index: match.index ?? -1, confidence: pattern.weight };
  }
  return { label: "INFORMATION", cue: "descriptive", index: -1, confidence: 0.72 };
}

function firstMatch(text, patterns) {
  for (const re of patterns) {
    const match = text.match(re);
    if (match) return match[0];
  }
  return null;
}

function stripTrailingLogic(text) {
  return clean(text.split(/\b(?:if|when|where|unless|except|provided\s+that)\b/i)[0]).replace(/[,:;.]$/, "");
}

function tokenSet(text = "") {
  return new Set(
    text.toLowerCase().match(/[a-z][a-z-]{2,}/g)?.filter((token) => !STOPWORDS.has(token)) ?? []
  );
}

function jaccard(a, b) {
  const left = tokenSet(a);
  const right = tokenSet(b);
  if (!left.size || !right.size) return 0;
  let intersection = 0;
  left.forEach((token) => { if (right.has(token)) intersection += 1; });
  return intersection / (left.size + right.size - intersection);
}

function deriveActor(clause, modality) {
  if (modality.index < 1) return "Unresolved actor";
  let actor = clean(clause.slice(0, modality.index));
  actor = actor.replace(/^(?:if|when|where|whenever)\s+.+?,\s*/i, "");
  const comma = actor.lastIndexOf(",");
  if (comma >= 0) actor = actor.slice(comma + 1).trim();
  return actor.length > 80 || actor.length < 2 ? "Unresolved actor" : actor;
}

function deriveAction(clause, modality) {
  if (modality.index < 0) return stripTrailingLogic(clause);
  const after = clause.slice(modality.index + modality.cue.length);
  return stripTrailingLogic(after) || "Unresolved action";
}

function confidenceFor(record) {
  let score = record.modality === "INFORMATION" ? 0.54 : record.modalityConfidence;
  if (record.actor !== "Unresolved actor") score += 0.03;
  else score -= 0.14;
  if (record.action !== "Unresolved action" && record.action.length > 5) score += 0.02;
  if (record.evidence.length > 220) score -= 0.04;
  if (record.crossReferences.length) score -= 0.02;
  return Math.max(0.35, Math.min(0.99, score));
}

export function extractObligations(text = "", meta = {}) {
  const clauses = segmentClauses(text);
  return clauses.map((clause, index) => {
    const modality = classifyModality(clause);
    const condition = clause.match(CONDITION_RE)?.[1]?.trim() ?? null;
    const exception = clause.match(EXCEPTION_RE)?.[1]?.trim() ?? null;
    const deadline = firstMatch(clause, DEADLINE_PATTERNS);
    const crossReferences = [...clause.matchAll(CROSS_REF_RE)].map((m) => m[0]);
    const actor = deriveActor(clause, modality);
    const action = deriveAction(clause, modality);
    const authority = meta.authority ?? "Demo corpus";
    const section = meta.section ?? `Clause ${index + 1}`;
    const id = `RT-${hash(`${authority}|${section}|${clause}`)}`;
    const record = {
      id,
      sourceId: meta.sourceId ?? "demo://regulation",
      sourceVersion: meta.version ?? "v1",
      authority,
      jurisdiction: meta.jurisdiction ?? "EU",
      section,
      modality: modality.label,
      modalityCue: modality.cue,
      modalityConfidence: modality.confidence,
      actor,
      action,
      deadline,
      condition,
      exception,
      crossReferences,
      evidence: clause,
      reviewState: "UNREVIEWED",
      severity: SEVERITY_TERMS.test(clause) ? "HIGH" : deadline ? "MEDIUM" : "STANDARD",
      unresolved: [
        actor === "Unresolved actor" ? "actor" : null,
        crossReferences.length ? "cross-reference-context" : null,
      ].filter(Boolean),
    };
    return { ...record, confidence: confidenceFor(record) };
  });
}

export function analyzeDocument(text = "", meta = {}) {
  const records = extractObligations(text, meta);
  const normative = records.filter((r) => r.modality !== "INFORMATION");
  const counts = records.reduce((acc, r) => {
    acc[r.modality] = (acc[r.modality] ?? 0) + 1;
    return acc;
  }, {});
  const avgConfidence = normative.length
    ? normative.reduce((sum, r) => sum + r.confidence, 0) / normative.length
    : 0;
  const citationIntegrity = records.length
    ? records.filter((r) => r.sourceId && r.evidence).length / records.length
    : 0;
  return {
    engineVersion: ENGINE_VERSION,
    analyzedAt: new Date().toISOString(),
    source: meta,
    records,
    normative,
    summary: {
      clauseCount: records.length,
      obligationCount: normative.filter((r) => r.modality === "OBLIGATION").length,
      unresolvedCount: records.filter((r) => r.unresolved.length).length,
      avgConfidence,
      citationIntegrity,
      modalityCounts: counts,
    },
  };
}

function deadlineNumber(value) {
  if (!value) return null;
  const match = value.match(/(\d+)\s*(hour|day|week|month|year)/i);
  if (!match) return null;
  const multipliers = { hour: 1, day: 24, week: 168, month: 730, year: 8760 };
  return Number(match[1]) * multipliers[match[2].toLowerCase()];
}

export function comparePolicy(requirementText = "", policyText = "") {
  const requirement = extractObligations(requirementText)[0] ?? null;
  const policy = extractObligations(policyText)[0] ?? null;
  const lexical = jaccard(requirementText, policyText);
  const reqDeadline = deadlineNumber(requirement?.deadline);
  const policyDeadline = deadlineNumber(policy?.deadline);
  const dimensions = [
    {
      id: "actor",
      label: "Actor",
      score: requirement && policy ? jaccard(requirement.actor, policy.actor) : 0,
      detail: `${requirement?.actor ?? "Unresolved"} ↔ ${policy?.actor ?? "Unresolved"}`,
    },
    {
      id: "action",
      label: "Action & object",
      score: requirement && policy ? Math.max(lexical, jaccard(requirement.action, policy.action)) : 0,
      detail: policy?.action ?? "No policy action located",
    },
    {
      id: "polarity",
      label: "Polarity",
      score: requirement && policy && requirement.modality === policy.modality ? 1 : 0.3,
      detail: `${requirement?.modality ?? "?"} ↔ ${policy?.modality ?? "?"}`,
    },
    {
      id: "timing",
      label: "Timing",
      score: reqDeadline && policyDeadline ? (policyDeadline <= reqDeadline ? 1 : Math.max(0, reqDeadline / policyDeadline)) : (reqDeadline ? 0.2 : 0.8),
      detail: reqDeadline
        ? `${policy?.deadline ?? "No policy deadline"} against ${requirement?.deadline}`
        : "No numeric regulatory deadline detected",
    },
    {
      id: "exception",
      label: "Exception scope",
      score: requirement?.exception ? (policy?.exception ? jaccard(requirement.exception, policy.exception) : 0.25) : 0.9,
      detail: requirement?.exception ? (policy?.exception ?? "Regulatory exception not represented") : "No explicit exception in selected requirement",
    },
    {
      id: "evidence",
      label: "Evidence sufficiency",
      score: policyText.trim().length > 40 ? 0.92 : 0.45,
      detail: policyText.trim().length > 40 ? "Policy text is substantial enough for review" : "Policy evidence is too short",
    },
  ];
  const weights = { actor: 0.12, action: 0.24, polarity: 0.18, timing: 0.24, exception: 0.12, evidence: 0.10 };
  const score = dimensions.reduce((sum, d) => sum + d.score * weights[d.id], 0);
  const criticalFailure = dimensions.some((d) =>
    (d.id === "polarity" && d.score < 0.55)
    || (d.id === "timing" && reqDeadline && policyDeadline && policyDeadline > reqDeadline)
    || (d.id === "timing" && reqDeadline && !policyDeadline)
  );
  const outcome = criticalFailure || score < 0.62 ? "POTENTIAL_MISMATCH" : score >= 0.82 ? "LIKELY_ALIGNED" : "REVIEW_REQUIRED";
  return { requirement, policy, dimensions, score, outcome, lexicalSimilarity: lexical };
}

function changeSeverity(before, after) {
  const combined = `${before} ${after}`;
  const beforeModal = classifyModality(before).label;
  const afterModal = classifyModality(after).label;
  const beforeDeadline = deadlineNumber(firstMatch(before, DEADLINE_PATTERNS));
  const afterDeadline = deadlineNumber(firstMatch(after, DEADLINE_PATTERNS));
  if (beforeModal !== afterModal || (beforeDeadline && afterDeadline && afterDeadline < beforeDeadline) || SEVERITY_TERMS.test(combined)) return "CRITICAL";
  return "MATERIAL";
}

export function compareVersions(oldText = "", newText = "") {
  const oldClauses = segmentClauses(oldText);
  const newClauses = segmentClauses(newText);
  const matchedOld = new Set();
  const changes = [];

  newClauses.forEach((current) => {
    let bestIndex = -1;
    let bestScore = 0;
    oldClauses.forEach((previous, index) => {
      if (matchedOld.has(index)) return;
      const score = jaccard(previous, current);
      if (score > bestScore) { bestScore = score; bestIndex = index; }
    });
    if (bestIndex >= 0 && bestScore >= 0.38) {
      matchedOld.add(bestIndex);
      const previous = oldClauses[bestIndex];
      if (bestScore < 0.965 || clean(previous).toLowerCase() !== clean(current).toLowerCase()) {
        changes.push({ id: `CH-${hash(previous + current)}`, type: "MODIFIED", before: previous, after: current, similarity: bestScore, severity: changeSeverity(previous, current) });
      }
    } else {
      changes.push({ id: `CH-${hash(current)}`, type: "ADDED", before: null, after: current, similarity: 0, severity: SEVERITY_TERMS.test(current) ? "CRITICAL" : "MATERIAL" });
    }
  });

  oldClauses.forEach((previous, index) => {
    if (!matchedOld.has(index)) changes.push({ id: `CH-${hash(previous)}`, type: "REMOVED", before: previous, after: null, similarity: 0, severity: "CRITICAL" });
  });

  const counts = changes.reduce((acc, c) => { acc[c.type] = (acc[c.type] ?? 0) + 1; return acc; }, {});
  return {
    changes,
    counts,
    affectedObligations: changes.filter((c) => c.type !== "ADDED").length,
    criticalCount: changes.filter((c) => c.severity === "CRITICAL").length,
    materialityScore: Math.min(100, Math.round(changes.reduce((s, c) => s + (c.severity === "CRITICAL" ? 28 : 14), 0))),
  };
}

export function evidenceGraph(record) {
  if (!record) return { nodes: [], edges: [] };
  const nodes = [
    { id: "source", label: record.section, type: "source" },
    { id: "obligation", label: record.id, type: "obligation" },
    { id: "actor", label: record.actor, type: "entity" },
    { id: "action", label: record.action, type: "action" },
    { id: "review", label: record.reviewState, type: "review" },
  ];
  if (record.deadline) nodes.push({ id: "deadline", label: record.deadline, type: "temporal" });
  if (record.exception) nodes.push({ id: "exception", label: record.exception, type: "logic" });
  return {
    nodes,
    edges: [
      { from: "source", to: "obligation", label: "asserts" },
      { from: "obligation", to: "actor", label: "binds" },
      { from: "obligation", to: "action", label: "requires" },
      ...(record.deadline ? [{ from: "obligation", to: "deadline", label: "due" }] : []),
      ...(record.exception ? [{ from: "exception", to: "obligation", label: "limits" }] : []),
      { from: "obligation", to: "review", label: "awaits" },
    ],
  };
}

export function downloadJson(data, filename = "regulatrace-export.json") {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

