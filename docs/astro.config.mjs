import mdx from "@astrojs/mdx";
import starlight from "@astrojs/starlight";
import { defineConfig } from "astro/config";

export default defineConfig({
  integrations: [
    starlight({
      title: "Skaileup Skill Catalog",
      description:
        "Concept, build, and quality pipeline skills for the Skaile ecosystem.",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/skaile-ai/ai-assets-skaileup",
        },
      ],
      sidebar: [
        { label: "Overview", link: "/" },
        {
          label: "Introduction",
          items: [
            { label: "What is Skaileup", link: "/intro/what-is-skaileup/" },
            { label: "Mental Model", link: "/intro/mental-model/" },
            { label: "Pipeline Walkthrough", link: "/intro/pipeline/" },
            { label: "Tiers", link: "/intro/tiers/" },
            { label: "Workspace Zones", link: "/intro/workspace-zones/" },
            { label: "Slice Loops", link: "/intro/slice-loops/" },
            { label: "Flows & Bundles", link: "/intro/flows-and-bundles/" },
            { label: "How It's Consumed", link: "/intro/consumption/" },
          ],
        },
        {
          label: "Flows",
          collapsed: false,
          autogenerate: { directory: "flows" },
        },
        {
          label: "Concept",
          collapsed: false,
          items: [
            { label: "Overview", link: "/domains/concept-group/" },
            {
              label: "concept",
              autogenerate: { directory: "domains/concept" },
              collapsed: true,
            },
            {
              label: "design",
              autogenerate: { directory: "domains/design" },
              collapsed: true,
            },
            {
              label: "product-spec",
              autogenerate: { directory: "domains/product-spec" },
              collapsed: true,
            },
            {
              label: "experience",
              autogenerate: { directory: "domains/experience" },
              collapsed: true,
            },
            {
              label: "concept-slice",
              autogenerate: { directory: "domains/concept-slice" },
              collapsed: true,
            },
            {
              label: "mockup-component",
              autogenerate: { directory: "domains/mockup-component" },
              collapsed: true,
            },
            {
              label: "mockup-walkthrough",
              autogenerate: { directory: "domains/mockup-walkthrough" },
              collapsed: true,
            },
            {
              label: "mockup-feedback",
              autogenerate: { directory: "domains/mockup-feedback" },
              collapsed: true,
            },
          ],
        },
        {
          label: "Implementation",
          collapsed: false,
          items: [
            { label: "Overview", link: "/domains/impl-group/" },
            {
              label: "impl-architecture",
              autogenerate: { directory: "domains/impl-architecture" },
              collapsed: true,
            },
            {
              label: "impl-plan",
              autogenerate: { directory: "domains/impl-plan" },
              collapsed: true,
            },
            {
              label: "impl-slice",
              autogenerate: { directory: "domains/impl-slice" },
              collapsed: true,
            },
            {
              label: "impl-build",
              autogenerate: { directory: "domains/impl-build" },
              collapsed: true,
            },
            {
              label: "impl-quality",
              autogenerate: { directory: "domains/impl-quality" },
              collapsed: true,
            },
          ],
        },
        {
          label: "Meta",
          collapsed: false,
          items: [
            { label: "Overview", link: "/domains/meta-group/" },
            {
              label: "skaileup-orchestrator",
              autogenerate: { directory: "domains/skaileup-orchestrator" },
              collapsed: true,
            },
            {
              label: "ops",
              autogenerate: { directory: "domains/ops" },
              collapsed: true,
            },
            {
              label: "lab",
              autogenerate: { directory: "domains/lab" },
              collapsed: true,
            },
            {
              label: "contracts",
              autogenerate: { directory: "domains/contracts" },
              collapsed: true,
            },
          ],
        },
        {
          label: "Reference",
          collapsed: true,
          items: [
            { label: "Skill DSL Grammar", link: "/reference/skill-grammar/" },
            { label: "Asset Frontmatter", link: "/reference/asset-frontmatter/" },
            { label: "Iron Laws", link: "/reference/iron-laws/" },
            { label: "Golden Principles", link: "/reference/golden-principles/" },
            { label: "Naming Conventions", link: "/reference/naming/" },
            { label: "Flows & Bundles Schema", link: "/reference/flows-bundles/" },
            { label: "Skill Authoring Guide", link: "/reference/contributing/" },
          ],
        },
        { label: "Roadmap", link: "/improvements/" },
      ],
    }),
    mdx(),
  ],
});
