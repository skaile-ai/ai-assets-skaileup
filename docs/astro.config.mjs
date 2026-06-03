import mdx from "@astrojs/mdx";
import starlight from "@astrojs/starlight";
import { defineConfig } from "astro/config";
import mermaid from "astro-mermaid";

export default defineConfig({
  integrations: [
    // Must precede Starlight so it processes ```mermaid fences first.
    // Client-side rendering (no Playwright); autoTheme follows Starlight's data-theme.
    mermaid({ autoTheme: true }),
    starlight({
      title: "Skaileup Skill Collection",
      description:
        "Concept, build, and quality pipeline skills for the Skaile ecosystem.",
      components: {
        // Shows each page's source file path (linked to GitHub) on the first
        // line, above the title heading.
        PageTitle: "./src/components/PageTitle.astro",
      },
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
          label: "Project",
          collapsed: false,
          items: [
            { label: "README", link: "/project/readme/" },
            { label: "CLAUDE.md", link: "/project/claude/" },
            { label: "Contributing", link: "/project/contributing/" },
          ],
        },
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
              label: "contracts",
              autogenerate: { directory: "domains/contracts" },
              collapsed: true,
            },
          ],
        },
        {
          label: "Reference",
          collapsed: true,
          autogenerate: { directory: "reference" },
        },
        { label: "Roadmap", link: "/improvements/" },
      ],
    }),
    mdx(),
  ],
});
