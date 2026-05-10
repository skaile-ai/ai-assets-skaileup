#!/usr/bin/env node
// Generate Starlight content pages from SKILL.md and DOMAIN.md files in the catalog.
//
// For every SKILL.md found under the repo root (skipping /docs-site, /.git, /.worktrees,
// /.pytest_cache), emits an .mdx page under src/content/docs/domains/<domain>/<slug>.mdx
// that:
//   1. Sets `title` and `description` from frontmatter
//   2. Renders the SKILL.md body verbatim (no transforms)
//   3. Adds a metadata block (version, stage, tags) and links to the source file on GitHub
//
// For every DOMAIN.md, emits an index.mdx that lists the domain's skills.

import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync, existsSync } from "node:fs";
import { dirname, join, relative, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, "..", "..");
const OUT_ROOT = join(__dirname, "..", "src", "content", "docs", "domains");
const GITHUB_BASE =
  "https://github.com/skaile-ai/ai-assets-skaileup/blob/main";

const SKIP_DIRS = new Set([
  "docs-site",
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

// Top-level domain directories to include
const DOMAIN_DIRS = [
  "concept",
  "design",
  "product-spec",
  "experience",
  "concept-slice",
  "component-mockup",
  "walkthrough-mockup",
  "mockup-feedback",
  "impl-architecture",
  "impl-plan",
  "impl-slice",
  "impl-build",
  "impl-quality",
  "skaileup",
  "ops",
  "lab",
  "contracts",
];

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
sidebar:
  label: "${name.replace(new RegExp(`^${repoRel.split("/")[0]}-?`), "") || name}"
---

:::note[Skill manifest]
**Name:** \`${name}\`
**Stage:** ${stage} · **Version:** ${version}
**Tags:** ${tags}
**Source:** [\`${repoRel}\`](${GITHUB_BASE}/${repoRel})
:::

${asMdString(body)}
`;

  return front;
}

function renderDomainPage({ domainPath, fm, body, repoRel, skillsInDomain }) {
  const name = fm.name || basename(dirname(domainPath));
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
sidebar:
  label: "Overview"
  order: 0
---

:::note[Domain manifest]
**Source:** [\`${repoRel}\`](${GITHUB_BASE}/${repoRel})
:::

${asMdString(body)}

## Skills in this domain

${skillsList || "_No skills found._"}
`;
}

function main() {
  const files = walk(REPO_ROOT);
  // Group by domain (top-level directory under repo root)
  const byDomain = new Map();
  for (const f of files) {
    const rel = relative(REPO_ROOT, f);
    const top = rel.split("/")[0];
    if (!DOMAIN_DIRS.includes(top)) continue;
    if (!byDomain.has(top)) byDomain.set(top, { domainFile: null, skills: [] });
    const entry = byDomain.get(top);
    if (basename(f) === "DOMAIN.md") entry.domainFile = f;
    else entry.skills.push(f);
  }

  let count = 0;
  for (const [domain, { domainFile, skills }] of byDomain.entries()) {
    const outDir = join(OUT_ROOT, domain);
    ensureDir(outDir);

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
}

main();
