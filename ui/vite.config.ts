import { defineConfig } from "vitest/config";
import { sveltekit } from '@sveltejs/kit/vite';
import dotenv from 'dotenv';

dotenv.config({ override: true });
export default defineConfig({
    plugins: [sveltekit()],
    define: {
        __DOCUMENT_NAME__: JSON.stringify(process.env.DOCUMENT_NAME),
        __BACKEND__: JSON.stringify(process.env.BACKEND),
        __META_DESCRIPTION__: JSON.stringify(process.env.META_DESCRIPTION),
        __META_IMG_URL__: JSON.stringify(process.env.META_IMG_URL)
    },
    test: {
        include: ['src/**/*.{test,spec}.{js,ts}']
    }
});