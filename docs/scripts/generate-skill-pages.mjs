#!/usr/bin/env node
// Generate Starlight content pages from SKILL.md and DOMAIN.md files in the collection.
//
// For every SKILL.md found under skaileup/ and ai-assets/{lab,contracts}/ (skipping
// /docs, /.git, /.worktrees, /.pytest_cache), emits an .mdx page under
// src/content/docs/domains/<domain>/<slug>.mdx that:
//   1. Sets `title` and `description` from frontmatter
//   2. Renders the SKILL.md body verbatim (no transforms)
//   3. Adds a metadata block (version, stage, tags) and links to the source file on GitHub
//
// For every DOMAIN.md, emits an index.mdx that lists the domain's skills.

import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync, existsSync, rmSync } from "node:fs";
import { dirname, join, relative, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, "..", "..");
const DOCS_ROOT = join(__dirname, "..", "src", "content", "docs");
const OUT_ROOT = join(DOCS_ROOT, "domains");
const FLOWS_SRC = join(REPO_ROOT, "skaileup", "flows");
const FLOWS_OUT = join(DOCS_ROOT, "flows");
const GITHUB_BASE =
  "https://github.com/skaile-ai/ai-assets-skaileup/blob/main";

// Real repo docs surfaced verbatim inside the site. The source file is the only
// copy that exists in git — these pages are generated build artifacts (gitignored)
// regenerated from the real file, so they can never drift. `out` is relative to
// src/content/docs/; `sidebar` drives menu placement.
const SOURCE_PAGES = [
  { src: "README.md", out: "project/readme.md", label: "README", order: 1 },
  { src: "CLAUDE.md", out: "project/claude.md", label: "CLAUDE.md", order: 2 },
  { src: "CONTRIBUTING.md", out: "project/contributing.md", label: "Contributing", order: 3 },
  { src: "skaileup/contracts/skill_grammar.md", out: "reference/skill-grammar.md", label: "Skill DSL Grammar", order: 1 },
  { src: "skaileup/contracts/asset_frontmatter.md", out: "reference/asset-frontmatter.md", label: "Asset Frontmatter", order: 2 },
  { src: "skaileup/contracts/iron_laws.md", out: "reference/iron-laws.md", label: "Iron Laws", order: 3 },
  { src: "skaileup/contracts/golden_principles.md", out: "reference/golden-principles.md", label: "Golden Principles", order: 4 },
  { src: "skaileup/contracts/semantic_types.md", out: "reference/semantic-types.md", label: "Semantic Types", order: 5 },
  { src: "skaileup/contracts/flows.md", out: "reference/flows-and-bundles.md", label: "Flows", order: 6 },
];

// Blanket-skipped at any depth. NOTE: "docs" is intentionally NOT here — a skill
// legitimately lives at skaileup/impl-build/docs/. The repo-root docs/ site is
// skipped by path in walk() instead.
const SKIP_DIRS = new Set([
  ".git",
  ".worktrees",
  ".pytest_cache",
  ".claude",
  ".skaile",
  "node_modules",
  "scripts",
  "tests",
  "bundles",
  "flows",
]);

function walk(dir, hits = []) {
  for (const entry of readdirSync(dir)) {
    if (SKIP_DIRS.has(entry)) continue;
    const p = join(dir, entry);
    // Skip only the repo-root docs/ site, not skill dirs named "docs".
    if (entry === "docs" && dir === REPO_ROOT) continue;
    const s = statSync(p);
    if (s.isDirectory()) walk(p, hits);
    else if (entry === "SKILL.md" || entry === "DOMAIN.md") hits.push(p);
  }
  return hits;
}

function parseFrontmatter(content) {
  const m = /^---\n([\s\S]*?)\n---\n?/.exec(content);
  if (!m) return { fm: {}, body: content };
  let fm = {};
  try {
    fm = parseYaml(m[1]) || {};
  } catch {
    fm = {};
  }
  return { fm, body: content.slice(m[0].length) };
}

function escapeForMdx(text) {
  // Escape characters that would break MDX parsing inside Markdown body.
  // Strategy: detect MDX-hostile constructs and wrap the entire body in a
  // safe code-rendering block. We pass through fenced code blocks unchanged.
  return text;
}

function slugify(name) {
  return name.replace(/[^a-z0-9]+/gi, "-").replace(/^-+|-+$/g, "").toLowerCase();
}

// Domain directories to include.
// User-facing domains live under skaileup/<domain>/
// contracts is now also under skaileup/ (moved from ai-assets/)
const SKAILEUP_DOMAINS = new Set([
  "concept",
  "contracts",
  "design",
  "product-spec",
  "experience",
  "concept-slice",
  "mockup-component",
  "mockup-walkthrough",
  "mockup-feedback",
  "impl-architecture",
  "impl-plan",
  "impl-slice",
  "impl-build",
  "impl-quality",
  "skaileup-orchestrator",
  "ops",
]);

function ensureDir(p) {
  mkdirSync(p, { recursive: true });
}

function asMdString(s) {
  // We're rendering as plain Markdown (.md) so MDX-hostile syntax (angle-bracket
  // placeholders, JSX-looking tokens) goes through the Markdown parser, which
  // treats unrecognised inline HTML as text. No escaping needed.
  return s;
}

function renderSkillPage({ skillPath, fm, body, repoRel }) {
  const name = fm.name || basename(dirname(skillPath));
  const description =
    fm.description || `Skill: ${name}`;
  const meta = fm.metadata || {};
  const stage = meta.stage || "—";
  const version = meta.version || "—";
  const tags = (meta.tags || []).join(", ") || "—";

  const yamlDescription = description
    .replace(/\n/g, " ")
    .replace(/"/g, "'")
    .slice(0, 250);

  const front = `---
title: "${name}"
description: "${yamlDescription}"
sourcePath: "${repoRel}"
sidebar:
  label: "${name.replace(new RegExp(`^${repoRel.split("/")[0]}-?`), "") || name}"
---

:::note[Skill manifest]
**Name:** \`${name}\`
**Stage:** ${stage} · **Version:** ${version}
**Tags:** ${tags}
:::

${asMdString(body)}
`;

  return front;
}

function renderDomainPage({ domainPath, fm, body, repoRel, skillsInDomain }) {
  // DOMAIN.md carries the domain identifier in `slug:` (skaile-workspaces
  // domain schema); fall back to legacy `name:` then the directory basename.
  const name = fm.slug || fm.name || basename(dirname(domainPath));
  const description = fm.description || `Domain: ${name}`;
  const skillsList = skillsInDomain
    .map((s) => {
      const desc = (s.description || "")
        .replace(/\n/g, " ")
        .slice(0, 140);
      return `- [${s.name}](./${s.slug}/) — ${desc}`;
    })
    .join("\n");
  const yamlDescription = description.replace(/"/g, "'").slice(0, 250);

  return `---
title: "${name}"
description: "${yamlDescription}"
sourcePath: "${repoRel}"
sidebar:
  label: "Overview"
  order: 0
---

${asMdString(body)}

## Skills in this domain

${skillsList || "_No skills found._"}
`;
}

function renderFlowPage({ fm, body, type }) {
  // type is the flow directory name, e.g. "appbuilder-standard". Each carries a
  // self-contained <type>.flow.yaml (graph + top-level requires: manifest)
  // alongside the source markdown.
  const title = fm.title || type;
  const description = (fm.description || `Flow: ${type}`)
    .replace(/\n/g, " ")
    .replace(/"/g, "'")
    .slice(0, 250);
  const order = typeof fm.order === "number" ? fm.order : 99;
  const flowRel = `skaileup/flows/${type}/${type}.flow.yaml`;
  const mdRel = `skaileup/flows/${type}/${type}.md`;

  return `---
title: "${title}"
description: "${description}"
sourcePath: "${mdRel}"
sidebar:
  label: "${title}"
  order: ${order}
---

:::note[Flow manifest]
**Flow:** [\`${flowRel}\`](${GITHUB_BASE}/${flowRel}) — self-contained: graph + \`requires:\` install manifest.
:::

${asMdString(body)}
`;
}

function renderFlowsIndex({ fm, body }) {
  const title = fm.title || "Flows";
  const description = (fm.description || "Flows")
    .replace(/\n/g, " ")
    .replace(/"/g, "'")
    .slice(0, 250);
  return `---
title: "${title}"
description: "${description}"
sourcePath: "skaileup/flows/index.md"
sidebar:
  label: "Overview"
  order: 0
---

${asMdString(body)}
`;
}

function generateFlows() {
  if (!existsSync(FLOWS_SRC)) return 0;
  ensureDir(FLOWS_OUT);
  let count = 0;

  // Flows section overview from skaileup/flows/index.md
  const indexSrc = join(FLOWS_SRC, "index.md");
  if (existsSync(indexSrc)) {
    const { fm, body } = parseFrontmatter(readFileSync(indexSrc, "utf8"));
    writeFileSync(join(FLOWS_OUT, "index.md"), renderFlowsIndex({ fm, body }));
    count++;
  }

  // One page per flow directory that carries a <type>/<type>.md source.
  for (const entry of readdirSync(FLOWS_SRC)) {
    if (entry.startsWith("_")) continue; // skip _meta
    const flowDir = join(FLOWS_SRC, entry);
    if (!statSync(flowDir).isDirectory()) continue;
    const src = join(flowDir, `${entry}.md`);
    if (!existsSync(src)) continue;
    const { fm, body } = parseFrontmatter(readFileSync(src, "utf8"));
    writeFileSync(join(FLOWS_OUT, `${entry}.md`), renderFlowPage({ fm, body, type: entry }));
    count++;
  }
  return count;
}

// Pull the first H1 off a markdown body: Starlight renders the frontmatter
// `title` as the page's H1, so keeping the source's own H1 would double it.
function splitLeadingTitle(body) {
  const lines = body.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const m = /^#\s+(.+?)\s*$/.exec(line);
    if (m) {
      lines.splice(i, 1);
      if (lines[i] === "") lines.splice(i, 1); // drop the blank line under it
      return { title: m[1], body: lines.join("\n") };
    }
    if (line.trim() !== "") break; // real content before any H1 — leave body intact
  }
  return { title: null, body };
}

function firstParagraph(body) {
  for (const raw of body.split("\n")) {
    const line = raw.trim();
    if (!line || line.startsWith("#") || line.startsWith("```") || line.startsWith("|")) continue;
    return line.replace(/[*_`>]/g, "").slice(0, 160);
  }
  return "";
}

function renderSourcePage({ body, repoRel, label, order }) {
  const { title, body: stripped } = splitLeadingTitle(body);
  const desc = firstParagraph(stripped).replace(/"/g, "'");
  return `---
title: "${(title || label).replace(/"/g, "'")}"
description: "${desc}"
sourcePath: "${repoRel}"
sidebar:
  label: "${label}"
  order: ${order}
---

${asMdString(stripped)}
`;
}

function generateSourcePages() {
  let count = 0;
  for (const { src, out, label, order } of SOURCE_PAGES) {
    const srcPath = join(REPO_ROOT, src);
    if (!existsSync(srcPath)) {
      console.warn(`  skipped (missing source): ${src}`);
      continue;
    }
    const { body } = parseFrontmatter(readFileSync(srcPath, "utf8"));
    const outPath = join(DOCS_ROOT, out);
    ensureDir(dirname(outPath));
    writeFileSync(outPath, renderSourcePage({ body, repoRel: src, label, order }));
    count++;
  }
  return count;
}

function main() {
  // Walk skaileup/ for user-facing skill domains.
  // We walk REPO_ROOT but use the path structure to determine which domain each file belongs to.
  const files = walk(REPO_ROOT);
  // Group by domain name (second path segment for skaileup/*)
  const byDomain = new Map();
  for (const f of files) {
    const rel = relative(REPO_ROOT, f);
    const parts = rel.split("/");
    let domain = null;
    if (parts[0] === "skaileup" && SKAILEUP_DOMAINS.has(parts[1])) {
      domain = parts[1];
    }
    if (!domain) continue;
    if (!byDomain.has(domain)) byDomain.set(domain, { domainFile: null, skills: [] });
    const entry = byDomain.get(domain);
    if (basename(f) === "DOMAIN.md") {
      // Domains are non-nested (skaile-workspaces rule): exactly one DOMAIN.md
      // per domain, at its root. Keep the shallowest defensively in case a
      // stray sub-DOMAIN.md reappears. Compare on repo-relative depth
      // (`parts`), not the absolute path.
      const prevDepth = entry.domainFile
        ? relative(REPO_ROOT, entry.domainFile).split("/").length
        : Infinity;
      if (parts.length < prevDepth) entry.domainFile = f;
    } else entry.skills.push(f);
  }

  let count = 0;
  // Track exactly which files we write per domain, so we can prune stale ones.
  const writtenByDomain = new Map();
  for (const [domain, { domainFile, skills }] of byDomain.entries()) {
    const outDir = join(OUT_ROOT, domain);
    ensureDir(outDir);
    const written = new Set(["index.md"]);
    writtenByDomain.set(domain, written);

    // Collect skill metadata first to feed into the domain index page
    const skillMeta = [];
    for (const sk of skills) {
      const content = readFileSync(sk, "utf8");
      const { fm, body } = parseFrontmatter(content);
      const repoRel = relative(REPO_ROOT, sk);
      const name = fm.name || basename(dirname(sk));
      const slug = slugify(name);
      const description = fm.description || "";
      skillMeta.push({ name, slug, description, fm, body, repoRel, sk });
    }
    skillMeta.sort((a, b) => a.name.localeCompare(b.name));

    // Write per-skill pages
    for (const s of skillMeta) {
      const out = renderSkillPage({
        skillPath: s.sk,
        fm: s.fm,
        body: s.body,
        repoRel: s.repoRel,
      });
      const outPath = join(outDir, `${s.slug}.md`);
      writeFileSync(outPath, out);
      written.add(`${s.slug}.md`);
      count++;
    }

    // Write domain index page
    if (domainFile) {
      const content = readFileSync(domainFile, "utf8");
      const { fm, body } = parseFrontmatter(content);
      const repoRel = relative(REPO_ROOT, domainFile);
      const out = renderDomainPage({
        domainPath: domainFile,
        fm,
        body,
        repoRel,
        skillsInDomain: skillMeta,
      });
      writeFileSync(join(outDir, "index.md"), out);
      count++;
    } else {
      // Synthesize a minimal index when no DOMAIN.md exists
      const skillsList = skillMeta
        .map((s) => {
          const desc = (s.description || "")
            .replace(/\n/g, " ")
            .slice(0, 140);
          return `- [${s.name}](./${s.slug}/) — ${desc}`;
        })
        .join("\n");
      const out = `---
title: "${domain}"
description: "${domain} domain"
sidebar:
  label: "Overview"
  order: 0
---

# ${domain}

_(No DOMAIN.md authored yet.)_

## Skills in this domain

${skillsList}
`;
      writeFileSync(join(outDir, "index.md"), out);
      count++;
    }
  }

  console.log(`Generated ${count} pages under ${relative(process.cwd(), OUT_ROOT)}`);

  // Prune stale output: remove orphan domain dirs (old naming) and any per-domain
  // page no longer backed by a source SKILL.md/DOMAIN.md. Loose files at the
  // domains/ root (e.g. hand-written *-group.md overviews) are left untouched.
  const knownDomains = new Set([...SKAILEUP_DOMAINS]);
  let pruned = 0;
  for (const entry of readdirSync(OUT_ROOT)) {
    const entryPath = join(OUT_ROOT, entry);
    if (!statSync(entryPath).isDirectory()) continue;
    if (!knownDomains.has(entry)) {
      rmSync(entryPath, { recursive: true, force: true });
      pruned++;
      continue;
    }
    const keep = writtenByDomain.get(entry) || new Set(["index.md"]);
    for (const f of readdirSync(entryPath)) {
      if (!keep.has(f)) {
        rmSync(join(entryPath, f));
        pruned++;
      }
    }
  }
  if (pruned) console.log(`Pruned ${pruned} stale entries under ${relative(process.cwd(), OUT_ROOT)}`);

  const flowCount = generateFlows();
  console.log(`Generated ${flowCount} pages under ${relative(process.cwd(), FLOWS_OUT)}`);

  const sourceCount = generateSourcePages();
  console.log(`Generated ${sourceCount} source pages (README/CLAUDE/contracts) under ${relative(process.cwd(), DOCS_ROOT)}`);
}

main();
