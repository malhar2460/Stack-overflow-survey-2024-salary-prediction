import vercel from '@sveltejs/adapter-vercel';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  kit: {
    // Use the Vercel adapter for optimal deploys on the Vercel platform
    adapter: vercel(),
    // Keep your lib alias pointed to the right folder
    alias: {
      $lib: 'frontend/src/lib'
    }
  }
};

export default config;
