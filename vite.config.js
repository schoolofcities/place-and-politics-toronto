import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import path from 'path';

export default defineConfig({
	plugins: [sveltekit()],
	resolve: {
		alias: {
			'$assets': path.resolve('./src/assets'),
			'$data': path.resolve('./src/data')
		}
	}
});
