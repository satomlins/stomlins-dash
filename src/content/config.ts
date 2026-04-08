import { defineCollection, z } from 'astro:content';

const cvCollection = defineCollection({
  type: 'data',
  schema: z.object({
    name: z.string(),
    role: z.string(),
    location: z.string(),
    contact: z.object({
      email: z.string().email(),
      linkedin: z.string().url(),
      github: z.string().url(),
      medium: z.string().url(),
    }),
    bio: z.string(),
    experience: z.array(z.object({
      company: z.string(),
      title: z.string(),
      start: z.string(),
      end: z.string().nullable(),
      location: z.string(),
    })),
    education: z.array(z.object({
      institution: z.string(),
      qualification: z.string(),
      field: z.string(),
      start: z.string(),
      end: z.string(),
    })),
  }),
});

const projectsCollection = defineCollection({
  type: 'data',
  schema: z.object({
    projects: z.array(z.object({
      name: z.string(),
      url: z.string(),
      description: z.string(),
      tags: z.array(z.string()),
      year: z.number(),
      image: z.string().optional(),
      pypi: z.string().url().optional(),
      github: z.string().url().optional(),
    })),
  }),
});

const nowCollection = defineCollection({
  type: 'data',
  schema: z.object({
    updated: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'ISO date required'),
    focus: z.array(z.string()),
    reading: z.string().optional(),
    listening: z.string().optional(),
  }),
});

export const collections = {
  cv: cvCollection,
  projects: projectsCollection,
  now: nowCollection,
};
