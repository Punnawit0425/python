import imageio.v3 as iio
from PIL import Image
import numpy as np
import glob

# ── 1. Grab your image files ──────────────────────────────────────────────────
# Option A: list them manually
filenames = ['team-pic1.png', 'team-pic2.png', 'team-pic3.png']

# Option B: automatically grab all PNGs in a folder (uncomment to use)
# filenames = sorted(glob.glob('frames/*.png'))

# ── 2. Check original sizes ───────────────────────────────────────────────────
print("Original sizes:")
for filename in filenames:
    img = iio.imread(filename)
    print(f"  {filename}: {img.shape}")  # (height, width, channels)

# ── 3. Set target size ────────────────────────────────────────────────────────
# Option A: match the first image's size (recommended)
first = Image.open(filenames[0])
target_size = first.size  # (width, height)

# Option B: set a fixed size manually (uncomment to use)
# target_size = (800, 600)  # (width, height)

print(f"\nTarget size: {target_size}")

# ── 4. Load and resize all images ─────────────────────────────────────────────
images = []
for filename in filenames:
    img = Image.open(filename).convert("RGB")        # ensure consistent color mode
    img = img.resize(target_size, Image.LANCZOS)     # resize to target size
    images.append(np.array(img))                     # convert to numpy array
    print(f"  Loaded: {filename}")

# ── 5. Save as GIF ────────────────────────────────────────────────────────────
output_filename = 'team.gif'
iio.imwrite(
    output_filename,
    images,
    duration=500,   # milliseconds per frame (500 = 0.5 seconds)
    loop=0          # 0 = loop forever, 1 = play once, 2 = play twice, etc.
)

print(f"\n✅ GIF saved as '{output_filename}' with {len(images)} frames")