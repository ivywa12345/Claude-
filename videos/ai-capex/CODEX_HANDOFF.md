# If AI Capex Collapses, Where Does $1 Trillion Go? — image handoff

The narration is final (`audio/narration.mp3`, 13:06, Edge TTS `en-US-BrianNeural`). The storyboard is
cut against its real word timings. **293 still images** are needed, one per shot. Each one goes
on screen at the moment that part of the narration starts.

## What's here

| Path | What it is |
| --- | --- |
| `prompts/frame-NNN_MMmSSsMMMms.txt` | One complete, self-contained prompt per image (style + recurring characters + composition + colors + exact on-screen text) |
| `prompts_all.txt` | The same 293 prompts in one file, in order |
| `timeline.csv` | Human-readable table: id, start/end time, filename, narration line, on-screen text, composition |
| `storyboard.json` | The authoritative storyboard the video renderer reads |
| `style-reference/` | The character and style sheets; pass these to the image generator as references |
| `images/` | **Where the generated images go**, named exactly like the prompt files but `.png` |
| `tools/review.py` | Checks which images exist, builds a contact sheet, records your approvals |
| `tools/assemble_video.py` | Renders the final MP4 (from xigua-msvideo-skill, MIT) |

## Visual style (already inside every prompt)

Clean hand-inked chibi cartoon on white, matching `style-reference/`. No stick figures. The
recurring cast carries the story:

- **The Wall Street guy**: messy spiky dark-brown hair, black sunglasses, dark suit + white shirt + red tie
- **His husky**: fluffy black-and-white, tongue out, sunglasses, sometimes a red bandana
- **His cat**: chubby orange tabby, sunglasses, unimpressed face
- All three keep their sunglasses on; the lens style changes with the mood when a prompt says so
  (dollar signs, stars, hearts, spirals, flames, white round "shocked" lenses)
- **Other investors**: chibi people in grey/navy suits with green ties and **no** sunglasses
- **Big Tech**: building characters — MICROSOFT blue, GOOGLE red, AMAZON orange, META purple (no logos);
  **NVIDIA**: a green chip character
- **Money** = green, **power** = yellow, **bonds** = blue US TREASURY certificates, **danger** = red,
  **AI apps** = small orange robots, **data center** = grey building with server racks

## Prompt to paste into Codex

```text
In this folder, generate one image for every prompt file in prompts/.
Before generating, look at the images in style-reference/ and pass them to the image generator as
style and character references (not as images to edit) on every call.
For each prompts/<name>.txt, call the built-in image generator once with that file's full text
as the prompt, landscape (16:9 or the closest landscape size available), and save the result as
images/<name>.png (same name, .png). One call per frame. Never combine frames into a grid.
Work in order, frame 001 first. Skip any frame whose PNG already exists in images/.
Do not edit storyboard.json, prompts/, or audio/.
First generate only frames 001, 010, 029, 087, 155 and 293, then stop so I can check the style.
Once I approve, continue with the rest in batches of 20, and report after each batch how many
were saved and which frames come next.
Use the approved sample images as a style/character reference for later frames, but follow each
frame's own composition.
```

Do the six-frame style check first. It covers the full trio, the guy with Nvidia, Big Tech,
a data-center shot, a mood-sunglasses shot and the ending. If the look is off, adjust then, not after 293 images.

## After the images are made

```sh
python tools/review.py status              # missing / pending / approved counts
python tools/review.py sheet               # open contact_sheet.html and look through every frame
python tools/review.py reject 17 --note "extra arm"   # regenerate these, then review again
python tools/review.py approve 1-293       # only for frames you have actually looked at
python tools/assemble_video.py --storyboard storyboard.json --out final.mp4 --work work/render
```

The renderer refuses frames that aren't approved, or whose file changed after approval. Images are
scaled to fit and padded with white to 1920×1080 (never stretched or cropped). The narration plays
as one continuous track and the picture hard-cuts at each frame's start time. Or just hand the
folder back to Claude and it will review and render.

Things to check while reviewing: spelling of on-screen labels, company names on the right
colored buildings, no real logos, the guy/husky/cat looking like the same characters every time
(hair, sunglasses, fur colors), correct limbs and paws, and neighboring frames that actually look
different.
