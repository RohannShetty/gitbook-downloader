import fs from 'fs';
import path from 'path';

export interface ProjectMetadata {
  slug: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  featured: boolean;
  githubUrl: string;
  demoUrl?: string;
}

export interface BlogMetadata {
  slug: string;
  title: string;
  description: string;
  date: string;
  category: string;
  tags: string[];
}

export function parseFrontmatter(content: string): { data: Record<string, any>; body: string } {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) {
    return { data: {}, body: content };
  }
  const yamlLines = match[1].split('\n');
  const body = match[2];
  const data: Record<string, any> = {};

  for (const line of yamlLines) {
    const colonIndex = line.indexOf(':');
    if (colonIndex === -1) continue;
    const key = line.slice(0, colonIndex).trim();
    let val: any = line.slice(colonIndex + 1).trim();

    // Clean strings and arrays
    if (val.startsWith('"') && val.endsWith('"')) {
      val = val.slice(1, -1);
    } else if (val.startsWith("'") && val.endsWith("'")) {
      val = val.slice(1, -1);
    } else if (val.startsWith('[') && val.endsWith(']')) {
      val = val.slice(1, -1).split(',').map((s: string) => s.trim().replace(/^["'](.*)["']$/, '$1'));
    } else if (val === 'true') {
      val = true;
    } else if (val === 'false') {
      val = false;
    }
    data[key] = val;
  }
  return { data, body };
}

const contentDir = path.join(process.cwd(), 'content');

export function getProjects(): ProjectMetadata[] {
  const projectsDir = path.join(contentDir, 'projects');
  if (!fs.existsSync(projectsDir)) return [];
  
  const files = fs.readdirSync(projectsDir);
  return files
    .filter(file => file.endsWith('.mdx') || file.endsWith('.md'))
    .map(file => {
      const slug = file.replace(/\.mdx?$/, '');
      const fullPath = path.join(projectsDir, file);
      const fileContents = fs.readFileSync(fullPath, 'utf8');
      const { data } = parseFrontmatter(fileContents);
      
      return {
        slug,
        title: data.title || slug,
        description: data.description || '',
        category: data.category || '',
        tags: data.tags || [],
        featured: !!data.featured,
        githubUrl: data.githubUrl || '',
        demoUrl: data.demoUrl || ''
      };
    })
    .sort((a, b) => (a.featured ? -1 : 1));
}

export function getProjectBySlug(slug: string): { metadata: ProjectMetadata; body: string } | null {
  const projectsDir = path.join(contentDir, 'projects');
  const mdxPath = path.join(projectsDir, `${slug}.mdx`);
  const mdPath = path.join(projectsDir, `${slug}.md`);
  const fullPath = fs.existsSync(mdxPath) ? mdxPath : fs.existsSync(mdPath) ? mdPath : null;
  
  if (!fullPath) return null;
  
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const { data, body } = parseFrontmatter(fileContents);
  
  return {
    metadata: {
      slug,
      title: data.title || slug,
      description: data.description || '',
      category: data.category || '',
      tags: data.tags || [],
      featured: !!data.featured,
      githubUrl: data.githubUrl || '',
      demoUrl: data.demoUrl || ''
    },
    body
  };
}

export function getBlogPosts(): BlogMetadata[] {
  const blogDir = path.join(contentDir, 'blog');
  if (!fs.existsSync(blogDir)) return [];
  
  const files = fs.readdirSync(blogDir);
  return files
    .filter(file => file.endsWith('.mdx') || file.endsWith('.md'))
    .map(file => {
      const slug = file.replace(/\.mdx?$/, '');
      const fullPath = path.join(blogDir, file);
      const fileContents = fs.readFileSync(fullPath, 'utf8');
      const { data } = parseFrontmatter(fileContents);
      
      return {
        slug,
        title: data.title || slug,
        description: data.description || '',
        date: data.date || '',
        category: data.category || '',
        tags: data.tags || []
      };
    })
    .sort((a, b) => b.date.localeCompare(a.date));
}

export function getBlogPostBySlug(slug: string): { metadata: BlogMetadata; body: string } | null {
  const blogDir = path.join(contentDir, 'blog');
  const mdxPath = path.join(blogDir, `${slug}.mdx`);
  const mdPath = path.join(blogDir, `${slug}.md`);
  const fullPath = fs.existsSync(mdxPath) ? mdxPath : fs.existsSync(mdPath) ? mdPath : null;
  
  if (!fullPath) return null;
  
  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const { data, body } = parseFrontmatter(fileContents);
  
  return {
    metadata: {
      slug,
      title: data.title || slug,
      description: data.description || '',
      date: data.date || '',
      category: data.category || '',
      tags: data.tags || []
    },
    body
  };
}
