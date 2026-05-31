import { defineCollection } from "astro:content";
import { z } from "astro:schema";
import { docsLoader } from "@astrojs/starlight/loaders";
import { docsSchema } from "@astrojs/starlight/schema";

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        // Repo-relative path to the authoritative source of a generated page
        // (e.g. skaileup/concept/brief/SKILL.md). Hand-written pages omit it;
        // the footer then falls back to the page's own location in docs/.
        sourcePath: z.string().optional(),
      }),
    }),
  }),
};
