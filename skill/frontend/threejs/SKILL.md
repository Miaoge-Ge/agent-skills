---
name: threejs
description: "Three.js expert for 3D web scenes: setup, geometry, materials, lighting, textures, animation, model loading, shaders, post-processing, and interaction. Use for any Three.js/WebGL task, from a first scene to debugging rendering, controls, or performance."
metadata:
  version: "1.0.0"
---

# Three.js Expert

> Build the smallest scene that shows the effect, then add one feature at a time. Pin the Three.js version, read the matching reference before writing code, and verify the result in a browser.

## When to Use

- Creating or refactoring a Three.js scene, camera, renderer, or object hierarchy.
- Adding geometry, materials, lighting, shadows, textures, or environment maps.
- Playing GLTF animations, loading models, or building custom shaders and post-processing.
- Debugging rendering artifacts, controls, raycasting, or WebGL performance.

## When NOT to Use

- React component/state design without 3D → `react-expert`.
- Pure CSS layout or animation → `tailwind-expert`.
- General browser performance unrelated to WebGL → `performance-expert`.
- A different 3D engine (Babylon.js, PlayCanvas, Godot) → follow that engine's docs.

## Route by Task

| Task | Read |
|---|---|
| Scene, camera, renderer, Object3D hierarchy, transforms | [references/fundamentals.md](references/fundamentals.md) |
| Built-in shapes, BufferGeometry, custom meshes, instancing | [references/geometry.md](references/geometry.md) |
| PBR/basic/Phong materials, textures on materials, transparency | [references/materials.md](references/materials.md) |
| Light types, shadows, environment/IBL lighting | [references/lighting.md](references/lighting.md) |
| Texture types, UV mapping, environment maps, color space | [references/textures.md](references/textures.md) |
| Keyframes, skeletal/morph animation, AnimationMixer | [references/animation.md](references/animation.md) |
| GLTF/GLB, textures, HDR environments, async loading | [references/loaders.md](references/loaders.md) |
| GLSL, ShaderMaterial, uniforms, custom vertex/fragment effects | [references/shaders.md](references/shaders.md) |
| EffectComposer, bloom, depth of field, screen effects | [references/postprocessing.md](references/postprocessing.md) |
| Raycasting, OrbitControls, pointer/touch interaction | [references/interaction.md](references/interaction.md) |

## Quick Start

```js
import * as THREE from "three";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 1000);
camera.position.set(2, 2, 4);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2));
const key = new THREE.DirectionalLight(0xffffff, 2);
key.position.set(3, 5, 4);
scene.add(key);

const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x4f9cff }),
);
scene.add(cube);

renderer.setAnimationLoop(() => {
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
});

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
```

## Working Rules

- Pin the `three` version in `package.json` or the import map; the API differs between releases. Match addon imports (`three/addons/...`) to that version.
- Keep one render loop via `renderer.setAnimationLoop`; do not start a second `requestAnimationFrame` loop.
- Dispose of geometries, materials, textures, and render targets when removing objects or recreating scenes; otherwise GPU memory grows.
- Cap pixel ratio (`Math.min(devicePixelRatio, 2)`), handle resize, and pause rendering when the canvas is hidden.
- Set `outputColorSpace = THREE.SRGBColorSpace` and the intended tone mapping; verify lighting after changing either.
- Prefer `MeshStandardMaterial`/`MeshPhysicalMaterial` with an environment map for PBR; only write a custom shader when built-in materials cannot express the effect.
- Keep camera, controls, and scene in the same coordinate scale; mismatched units are the usual cause of invisible or clipped meshes.
- Check the browser console and WebGL warnings before changing code; they often name the exact missing file, uniform, or extension.

## Scripts

Scaffold a runnable scene (import map, camera, lights, OrbitControls, resize handling):

```bash
node scripts/create_scene.mjs --out ./my-scene --title "My Scene"
```

The generated files are `index.html` and `main.js`; open `index.html` through a local static server so ES module imports resolve.

## References

- [Fundamentals](references/fundamentals.md)
- [Geometry](references/geometry.md)
- [Materials](references/materials.md)
- [Lighting](references/lighting.md)
- [Textures](references/textures.md)
- [Animation](references/animation.md)
- [Loaders](references/loaders.md)
- [Shaders](references/shaders.md)
- [Post-processing](references/postprocessing.md)
- [Interaction](references/interaction.md)
