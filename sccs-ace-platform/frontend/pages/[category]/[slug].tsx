import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { GetServerSideProps } from 'next';
import { renderBlock } from '../../lib/renderer';

interface ArticleBlock {
  id: number;
  block_type: 'text' | 'image' | 'youtube' | 'links' | 'code' | 'quote';
  content: string;
  position: number;
}

interface Article {
  id: number;
  title: string;
  slug: string;
  summary: string;
  category_name: string;
  published_at: string;
  blocks: ArticleBlock[];
}

interface Props {
  article: Article | null;
  error?: string;
}

export default function ArticleODR({ article, error }: Props) {
  if (error || !article) {
    return (
      <div className="min-h-screen bg-[#0d1117] text-[#c9d1d9] font-sans flex flex-col items-center justify-center p-6">
        <Head>
          <title>404: Knowledge Object Not Found - SCCS / ACE</title>
        </Head>
        <div className="bg-[#161b22] border border-[#30363d] border-dashed rounded-lg p-10 max-w-lg w-full text-center flex flex-col items-center">
          <span className="text-5xl mb-6 block" aria-hidden="true">🚫</span>
          <h1 className="text-xl font-bold text-[#f85149] mb-3">Error 404: Knowledge Object Not Found</h1>
          <p className="text-sm text-[#8b949e] mb-8">{error || "The requested article does not exist or has been archived by the Chronos Verifier."}</p>
          <Link
            href="/"
            className="bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] px-6 py-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#58a6ff] focus-visible:ring-offset-2 focus-visible:ring-offset-[#161b22]"
            aria-label="Return to SCCS Control Panel"
          >
            Return to Control Panel
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#c9d1d9] font-sans p-6 max-w-4xl mx-auto">
      <Head>
        <title>{article.title} - SCCS / ACE</title>
      </Head>

      <header className="mb-8 border-b border-[#21262d] pb-6">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-mono bg-[#1f242c] text-[#58a6ff] px-2 py-1 rounded">
            {article.category_name}
          </span>
          <span className="text-xs text-[#8b949e]">
            {new Date(article.published_at).toLocaleString()}
          </span>
        </div>
        <h1 className="text-3xl font-bold text-[#f0f6fc] mb-3">{article.title}</h1>
        <p className="text-lg text-[#8b949e]">{article.summary}</p>
      </header>

      <main className="flex flex-col gap-6">
        {article.blocks.map((block) => (
          <div key={block.id} className="article-block">
            {renderBlock(block)}
          </div>
        ))}
      </main>

      <footer className="mt-12 pt-6 border-t border-[#21262d] text-center text-xs text-[#8b949e] font-mono">
         &copy; 2026 SCCS-ACE PLATFORM // CONJUNCTIVE TRANSPARENCY PROTOCOLS
      </footer>
    </div>
  );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  // ⚡ Bolt: Cache expensive SSR renders at the edge using stale-while-revalidate
  context.res.setHeader(
    'Cache-Control',
    'public, s-maxage=60, stale-while-revalidate=300'
  );

  const { slug } = context.params as { slug: string };
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://backend:3000/api';

  try {
    // Determine host. If running locally vs docker.
    // For SSR, backend container name usually works if in same docker network.
    // Fallback to localhost if not found
    let fetchUrl = `${apiUrl}/articles/slug/${slug}`;
    if (process.env.NODE_ENV !== 'production' && typeof window === 'undefined') {
       fetchUrl = `http://localhost:3000/api/articles/slug/${slug}`;
    }

    const res = await fetch(fetchUrl);

    if (!res.ok) {
      return { props: { article: null, error: 'Article not found.' } };
    }

    const article: Article = await res.json();
    return { props: { article } };
  } catch (err: any) {
    console.error("Fetch error:", err);
    return { props: { article: null, error: 'Internal Server Error fetching data.' } };
  }
};
