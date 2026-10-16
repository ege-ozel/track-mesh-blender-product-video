import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import fs from 'node:fs/promises';
const root = path.resolve(import.meta.dirname, '..');
const source = process.env.TRACKMESH_SOURCE || 'D:/CodeSpace/track-mesh/apps/desktop';
const modules = path.join(source, 'node_modules');
const requireSource = createRequire(path.join(source, 'package.json'));
const { build } = await import(pathToFileURL(path.join(modules, 'vite/dist/node/index.js')));
const plugin = (await import(pathToFileURL(path.join(modules, '@vitejs/plugin-react/dist/index.js')))).default;
await build({configFile: false, root: path.join(root, 'demo-ui'), base: './', plugins: [plugin()],
  resolve: {alias: [
    {find: '@tauri-apps/api/core', replacement: path.join(root, 'demo-ui/src/mock-core.ts')},
    ...['react/jsx-dev-runtime', 'react/jsx-runtime', 'react-dom/client', 'react-dom', 'react'].map(name => ({find: name, replacement: requireSource.resolve(name)}))
  ]}, build: {outDir: path.join(root, 'demo-ui/dist'), emptyOutDir: false}});
const crypto = await import('node:crypto');
const hashes = {};
for (const file of ['App.tsx', 'styles.css', 'api.ts', 'main.tsx']) {
  const original = await fs.readFile(path.join(source, 'src', file));
  const copied = await fs.readFile(path.join(root, 'demo-ui/src', file));
  if (!original.equals(copied)) throw new Error(`Source copy mismatch: ${file}`);
  hashes[file] = crypto.createHash('sha256').update(original).digest('hex');
}
await fs.writeFile(path.join(root, 'docs/ui-source-hashes.json'), JSON.stringify({source, hashes, syntheticOnly: true}, null, 2));
