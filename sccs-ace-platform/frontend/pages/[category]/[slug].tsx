import React from 'react';
import Head from 'next/head';

export default function ArticleODR() {
  return (
    <div className="min-h-screen bg-[#0d1117] text-[#c9d1d9] font-sans p-6">
      <Head>
        <title>SCCS Dynamic Render</title>
      </Head>
      <header className="mb-6">
        <h1 className="text-xl font-bold">Dynamic ODR Renderer</h1>
        <p className="text-sm text-[#8b949e]">Auto-generated longread execution</p>
      </header>
      <main className="bg-[#161b22] border border-[#30363d] rounded-lg p-5">
        <p>This is a placeholder for dynamically rendered content fetched via the lib/api.ts bridge.</p>
      </main>
    </div>
  );
}
