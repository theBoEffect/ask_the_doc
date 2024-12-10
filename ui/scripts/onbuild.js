import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const distDir = path.resolve('build'); // Adjust if the build directory differs
const indexPath = path.join(distDir, 'index.html');

// Read environment variables or defaults
const meta = `
<title>Ask ${process.env.DOCUMENT_NAME || 'Ask the Doc'}</title>
<meta name="description" content="${process.env.META_DESCRIPTION || 'An AI Agent to answer questions about a document.'}">
<meta property="og:type" content="website">
<meta property="og:title" content="${process.env.DOCUMENT_NAME || 'Ask the Doc'}">
<meta property="og:description" content="${process.env.META_DESCRIPTION || 'An AI Agent to answer questions about a document.'}">
<meta property="og:url" content="${process.env.BACKEND || 'http://localhost:8000'}">
<meta property="og:image" content="${process.env.META_IMG_URL || ''}">
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="${process.env.BACKEND || 'http://localhost:8000'}">
<meta property="twitter:title" content="${process.env.DOCUMENT_NAME || 'Ask the Doc'}">
<meta property="twitter:description" content="${process.env.META_DESCRIPTION || 'An AI Agent to answer questions about a document.'}">
<meta property="twitter:image" content="${process.env.META_IMG_URL || ''}">
`;

// Ensure the build directory exists
if (!fs.existsSync(distDir)) {
	console.error('Build directory does not exist. Make sure to build the app first.');
	process.exit(1);
}

// Read and modify the index.html file
let html = fs.readFileSync(indexPath, 'utf-8');
html = html
	.replace('<!-- $$meta -->', meta);

// Write the updated HTML back
fs.writeFileSync(indexPath, html);

console.log('Meta tags successfully replaced in index.html');
