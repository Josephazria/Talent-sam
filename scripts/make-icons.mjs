// Génère les icônes PNG de l'app à partir d'un logo SVG (or sur bordeaux).
// Lancé une fois : `node scripts/make-icons.mjs`
import sharp from "sharp";
import { mkdirSync } from "node:fs";

mkdirSync("public/icons", { recursive: true });

const BG = "#250810";
const GOLD = "#c6a15b";

// Logo « nod » centré, serif, or. `pad` réserve une marge de sécurité
// (utile pour l'icône maskable).
function svg(size, pad) {
  const inset = Math.round(size * pad);
  const fontSize = Math.round((size - inset * 2) * 0.42);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <rect width="${size}" height="${size}" fill="${BG}"/>
  <text x="50%" y="50%" dy="0.02em" text-anchor="middle" dominant-baseline="central"
    font-family="Georgia, 'Times New Roman', serif" font-weight="500"
    font-size="${fontSize}" letter-spacing="${Math.round(size * 0.005)}"
    fill="${GOLD}">nod</text>
</svg>`;
}

async function render(size, pad, name) {
  await sharp(Buffer.from(svg(size, pad)))
    .png()
    .toFile(`public/icons/${name}`);
  console.log("écrit", name);
}

await render(192, 0.14, "icon-192.png");
await render(512, 0.14, "icon-512.png");
await render(180, 0.14, "apple-touch-icon.png");
// Maskable : plus de marge pour survivre au recadrage en cercle.
await render(512, 0.24, "icon-maskable-512.png");
