// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightImageZoom from 'starlight-image-zoom'

import node from '@astrojs/node';
import { config } from './lab-config.js';

export default defineConfig({
  trailingSlash: 'always',
  integrations: [
    starlight({
      plugins: [
        starlightImageZoom(),
      ],
      components: {
        Sidebar: './src/components/CustomSidebar.astro',
        Hero: './src/components/CustomHero.astro',
        PageFrame: './src/components/CustomPageFrame.astro'
      },
      pagefind: false,
      customCss: [
        './src/styles/custom.css',
      ],
      title: config.title,
      sidebar: config.sidebar,
    }),
  ],
  output: 'hybrid',
  adapter: node({
    mode: 'standalone',
  }),
  vite: {
    server: {
      allowedHosts: true,
    }
  }
});