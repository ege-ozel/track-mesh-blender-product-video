// Builds demo-ui-v3 from the read-only Track Mesh desktop source with a synthetic Tauri mock.
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const root = path.resolve(import.meta.dirname, '..');
const source = process.env.TRACKMESH_SOURCE || 'D:/CodeSpace/track-mesh/apps/desktop';
const modules = path.join(source, 'node_modules');
const requireSource = createRequire(path.join(source, 'package.json'));
const { build } = await import(pathToFileURL(path.join(modules, 'vite/dist/node/index.js')));
const plugin = (await import(pathToFileURL(path.join(modules, '@vitejs/plugin-react/dist/index.js')))).default;
await build({ configFile: false, logLevel: 'warn', root: path.join(root, 'demo-ui-v3'), base: './', plugins: [plugin()],
  resolve: { alias: [
    { find: '@tauri-apps/api/core', replacement: path.join(root, 'demo-ui-v3/mock-core.ts') },
    { find: '@trackmesh', replacement: path.join(source, 'src') },
    ...['react/jsx-dev-runtime', 'react/jsx-runtime', 'react-dom/client', 'react-dom', 'react'].map(name => ({ find: name, replacement: requireSource.resolve(name) })),
  ] }, build: { outDir: path.join(root, 'demo-ui-v3/dist'), emptyOutDir: true } });
console.log('Built demo-ui-v3/dist');
