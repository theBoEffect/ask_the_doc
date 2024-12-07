import { defineConfig } from "vitest/config";
import { sveltekit } from '@sveltejs/kit/vite';
import dotenv from 'dotenv';

dotenv.config();
export default defineConfig({
    plugins: [sveltekit()],
    define: {
        __DOCUMENT_NAME__: JSON.stringify(process.env.DOCUMENT_NAME)
    },
    test: {
        include: ['src/**/*.{test,spec}.{js,ts}']
    }
});
