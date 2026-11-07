#!/usr/bin/env node
/**
 * Scaffold a minimal, runnable Three.js scene.
 *
 * Usage:
 *   node create_scene.mjs [--out <dir>] [--title <title>] [--force]
 *
 * Writes index.html + main.js into the target directory. No dependencies.
 */
import { access, mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const THREE_VERSION = "0.170.0";

function usage() {
  console.log(`Usage: node create_scene.mjs [options]

Options:
  --out <dir>       Output directory (default: threejs-scene)
  --title <text>    Page title (default: Three.js Scene)
  --force           Write into an existing directory
  -h, --help        Show this help`);
}

const args = process.argv.slice(2);
let out = "threejs-scene";
let title = "Three.js Scene";
let force = false;

for (let i = 0; i < args.length; i += 1) {
  const arg = args[i];
  if (arg === "--out") {
    out = args[i + 1];
    i += 1;
  } else if (arg === "--title") {
    title = args[i + 1];
    i += 1;
  } else if (arg === "--force") {
    force = true;
  } else if (arg === "-h" || arg === "--help") {
    usage();
    process.exit(0);
  } else {
    console.error(`Unknown argument: ${arg}`);
    usage();
    process.exit(1);
  }
}

if (!out || !title) {
  console.error("--out and --title require a value.");
  process.exit(1);
}

const dir = path.resolve(out);
if (!force) {
  try {
    await access(dir);
    console.error(`Directory already exists: ${dir}\nUse --force to write into it.`);
    process.exit(1);
  } catch {
    // Directory does not exist yet; continue.
  }
}

const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${title.replaceAll("&", "&amp;").replaceAll("<", "&lt;")}</title>
    <style>
      html, body { margin: 0; height: 100%; overflow: hidden; background: #111; }
      canvas { display: block; }
    </style>
    <script type="importmap">
      {
        "imports": {
          "three": "https://cdn.jsdelivr.net/npm/three@${THREE_VERSION}/build/three.module.js",
          "three/addons/": "https://cdn.jsdelivr.net/npm/three@${THREE_VERSION}/examples/jsm/"
        }
      }
    </script>
  </head>
  <body>
    <script type="module" src="./main.js"></script>
  </body>
</html>
`;

const js = `import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x101418);

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 100);
camera.position.set(2.5, 2, 3.5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

scene.add(new THREE.HemisphereLight(0xffffff, 0x334455, 2));
const key = new THREE.DirectionalLight(0xffffff, 2.5);
key.position.set(3, 5, 4);
scene.add(key);

const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x4f9cff, roughness: 0.35, metalness: 0.1 }),
);
cube.position.y = 0.5;
scene.add(cube);

const ground = new THREE.Mesh(
  new THREE.CircleGeometry(4, 64),
  new THREE.MeshStandardMaterial({ color: 0x1c2530, roughness: 0.9 }),
);
ground.rotation.x = -Math.PI / 2;
scene.add(ground);

const grid = new THREE.GridHelper(8, 16, 0x334455, 0x223344);
scene.add(grid);

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

renderer.setAnimationLoop(() => {
  controls.update();
  renderer.render(scene, camera);
});
`;

await mkdir(dir, { recursive: true });
await writeFile(path.join(dir, "index.html"), html, "utf8");
await writeFile(path.join(dir, "main.js"), js, "utf8");

console.log(`Created ${path.join(dir, "index.html")}`);
console.log(`Created ${path.join(dir, "main.js")}`);
console.log(`\nServe it locally, for example:\n  npx --yes serve ${dir}\nThen open the printed URL.`);
