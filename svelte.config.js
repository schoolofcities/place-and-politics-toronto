import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import adapter from "@sveltejs/adapter-static";

const dev = "production" === "development";

/** @type {import('@sveltejs/kit').Config} */
const config = {
    preprocess: vitePreprocess(),
    kit: {
        adapter: adapter({
            pages: "docs",
            assets: "docs"
        }),
        paths: {
            // change below to your repo name
            base: dev ? "" : "/place-and-politics-toronto",
        }
		
    }
};

export default config;