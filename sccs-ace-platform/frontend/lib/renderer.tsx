import React, { useState } from 'react';

const CodeBlock = ({ content }: { content: string }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative group">
            <div
                className="bg-[#161b22] border border-[#30363d] rounded-md p-4 pt-8 overflow-x-auto focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#58a6ff]"
                tabIndex={0}
                aria-label="Code block"
            >
                <pre className="text-sm font-mono text-[#7ee787]">
                    <code>{content}</code>
                </pre>
            </div>
            <button
                onClick={handleCopy}
                aria-label={copied ? "Copied to clipboard" : "Copy code"}
                className="absolute top-2 right-2 bg-[#21262d] hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9] px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 focus-within:opacity-100 focus:opacity-100 transition-opacity focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#58a6ff]"
                aria-live="polite"
            >
                {copied ? "Copied!" : "Copy"}
            </button>
        </div>
    );
};

export function renderBlock(block: any) {
    switch (block.block_type) {
        case 'text':
            return <p className="text-base text-[#c9d1d9] leading-relaxed">{block.content}</p>;
        case 'code':
            return <CodeBlock content={block.content} />;
        case 'quote':
            return (
                <blockquote className="border-l-4 border-[#58a6ff] pl-4 italic text-[#8b949e] my-4">
                    {block.content}
                </blockquote>
            );
        case 'image':
            // content could be an image URL
            // 🛡️ Sentinel: Sanitize image source to prevent XSS via javascript: URIs
            const isSafeImage = typeof block.content === 'string' &&
                (block.content.startsWith('http://') || block.content.startsWith('https://'));

            if (!isSafeImage) {
                return <p className="text-[#f85149] text-sm">Error: Invalid image source</p>;
            }

            return (
                <div className="my-4 border border-[#30363d] rounded-md overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    {/* ⚡ Bolt: Lazy load assets for better initial page performance */}
                    <img src={block.content} alt="Article graphic" className="w-full h-auto object-cover" loading="lazy" />
                </div>
            );
        case 'links':
            // assume content is comma separated or JSON string array
            return (
                <div className="bg-[#0d1117] border border-[#30363d] p-3 rounded text-sm text-[#58a6ff]">
                    References: {block.content}
                </div>
            );
        case 'youtube':
            // 🛡️ Sentinel: Sanitize iframe source to prevent XSS. Must be a valid youtube embed.
            const isSafeYoutube = typeof block.content === 'string' &&
                block.content.startsWith('https://www.youtube.com/embed/');

            if (!isSafeYoutube) {
                return <p className="text-[#f85149] text-sm">Error: Invalid video source</p>;
            }

            return (
                <div className="aspect-w-16 aspect-h-9 my-4">
                    {/* ⚡ Bolt: Lazy load assets for better initial page performance */}
                    <iframe
                        src={block.content}
                        title="YouTube video player"
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                        loading="lazy"
                        className="w-full h-64 rounded-md border border-[#30363d]"
                    ></iframe>
                </div>
            );
        default:
            return <p className="text-[#c9d1d9]">{block.content}</p>;
    }
}
