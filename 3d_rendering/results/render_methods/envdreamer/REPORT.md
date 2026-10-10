# EnvDreamer (arXiv 2610.04301): report for the shared rendering test

Date: 2026-10-10. Paper: Swain, Han, Torralba, https://arxiv.org/abs/2610.04301 (v1, 3 Oct 2026; the
only version). Written by the EnvDreamer trial agent and saved by the lead. The lead checked that the
repository below exists and that its last commit is 2025-11-12, and that the snapshot has 187
object types.

**Short answer:** the framework in the paper has not been released, and neither has the
EnvDreamer-20k dataset. The first author's GitHub has a public, unlicensed early prototype
(Oct-Nov 2025). It cannot render the test:
- it needs the Unreal Engine 5.6 editor (Epic account and EULA);
- it was built on Windows;
- the furniture and object models it uses were left out of the repository.

None of the six test views were rendered. Unreal Engine 5 was checked to render offscreen on this
machine's GPU, using a different, ready-built UE5 program.

Each claim is marked **[paper]** (stated in the paper), **[repo]** (read in the public prototype),
**[checked]** (run or measured on this machine), or **[not stated]**.

## 0. Release status (2026-10-10)

| Where | What is there |
|---|---|
| arXiv 2610.04301 | v1 only (v2 returns 404). The abstract says "we release EnvDreamer-20k"; the checklist says "We will release the EnvDreamer framework and the EnvDreamer-20k dataset". There is no code, data or project-page URL in the HTML, the PDF or the TeX source. |
| https://github.com/kswain98/EnvDreamer | Public, no licence, README is only "# EnvDreamer". Owner is Kabir Swain (MIT), the first author. Created 2025-10-16, last push 2025-11-13 (36 commits), 636 MB, 2,508 files. A UE 5.6 project called "EnvGen": the scene-builder actor (`AJsonSceneBuilder`), the Python planner, the web builder, `asset_registry.json` and 43 saved layouts. No validators beyond a JSON schema check, no task programs, no robots, no dataset, no evaluator agent. The paper does not link to it. |
| Other kswain98 repos | `environment` is VirtualEnv (arXiv 2601.07553, the platform EnvDreamer builds on). Its README links are empty `https://` placeholders, and it says `pip install virtualenv`, which is the unrelated Python tool. `environment-docs` holds docs only. Neither has a licence. |
| github.com/sijie-han, github.com/torralba-lab, github.com/torralba | No EnvDreamer or VirtualEnv repository. |
| Hugging Face | "envdreamer" in datasets, models and spaces: nothing. There is no `kswain98` user. |
| kswain98.github.io, sijie-han.github.io | Link only to the arXiv pages. |
| Web search (two queries) | Only the arXiv pages. |

**Security note:** `EnvGen/Scripts/core/config.py` in the public repo contains a hard-coded OpenAI
API key. It was not used or copied. Our clone under `/mnt/nvme` also contains it.

## 1. Did it run?

**Untested for EnvDreamer.** It is not released, and the prototype needs the UE 5.6 editor, which
needs an Epic account and EULA acceptance. Both were ruled out for this trial.

Installed (no licence accepted, no account created):

| Path | Size | What |
|---|---|---|
| `/mnt/nvme/oliver/robot/render_methods/envdreamer/EnvDreamer_repo/` | 1.3 GB | clone of kswain98/EnvDreamer, for reading only |
| `.../envdreamer/ue5_probe/dl/` | 558 MB | Project AirSim `Blocks-Linux-1.0.1.zip` (MIT, UE 5.2.1 ready-built Linux program) |
| `.../envdreamer/ue5_probe/Blocks/` | 944 MB | the unpacked program |
| `.../envdreamer/ue5_probe/pas_src/` | 51 MB | sparse clone of the Project AirSim Python client |
| `.../envdreamer/ue5_probe/env/` | 601 MB | conda Python 3.10 env with that client |

Why the prototype cannot run here even with an engine:
- **Editor only [repo] [paper].** Camera and screenshot functions drive the editor's active viewport
  (`#if WITH_EDITOR`, `GEditor->GetActiveViewport()`); the paper calls them "editor-only". The
  project file asks for engine 5.6 plus the Remote Control and Pixel Streaming plugins.
- **Windows-built [repo].** Hard-coded `C:\Users\kswain\...` paths, `.bat` and `.vcxproj` files. The
  C++ would need compiling for Linux.
- **The models are missing [repo].** `.gitignore` excludes `Content/Interactable/*` and
  `Content/Characters/*`. Of 567 asset paths the blueprints and maps point to, 266 are absent:
  paid store packs ("TM...Pack" furniture and decorations, ConvenienceStore, Megascans) and the UE
  mannequins. Only Unreal's StarterContent (basic shapes, about 18 props) is included.
- **Hosted language model [repo].** The planner calls the OpenAI API (default `gpt-4o`).
  `OPENAI_BASE_URL` can point it at an OpenAI-compatible local server.

### What running UE5 headless on this machine would take

| Item | Finding |
|---|---|
| Getting the engine | Both routes need an Epic account and the UE EULA: the prebuilt Linux editor (https://www.unrealengine.com/en-US/linux, 403 without login) or the private source at github.com/EpicGames/UnrealEngine (needs a GitHub account linked to Epic). Not done. |
| Disk | Not verified for 5.6. A 2022 report for UE 5.0 said about 20 GB to download, about 60 GB installed (https://gamingonlinux.com/2022/07/unreal-engine-5-editor-quietly-gets-a-proper-linux-version/page=3). A source build is larger. Fits on `/mnt/nvme`. |
| OS and driver | Epic's Linux requirements page (https://dev.epicgames.com/documentation/en-us/unreal-engine/linux-development-requirements-for-unreal-engine) recommends Ubuntu 22.04, glibc 2.35+, NVIDIA driver 570+, Vulkan. This machine: Ubuntu 22.04.5, glibc 2.35, driver 580.178.04 [checked]. |
| Blackwell GPU, headless | [checked] A Vulkan test with no `DISPLAY` finds "NVIDIA RTX PRO 6000 Blackwell Workstation Edition, Vulkan 1.4.312". The UE 5.2.1 Blocks program with `-RenderOffScreen` and no display did not crash, used about 1.2-1.3 GB of GPU memory, and returned three lit 1280x720 pictures to Python: 2.4 s to load and connect, 0.13-0.18 s per picture. Files: `ue5_probe/blocks_*.png`, `ue5_probe/probe_views.json`, script `ue5_probe_capture.py`. **Caveat:** the 0.37 m and 1.0 m pictures look the same and the lower half of each is black; the camera pose was probably not applied as intended (not debugged). This shows offscreen UE5 works, not that the framing was right. |
| Offscreen editor | The prototype needs the editor; running the editor with `-RenderOffScreen` on Linux is untested. |

## 2. Placement

**Untested; 0 of 251 placed.** The snapshot has on_top 140, inside 84, next_to 19, worn_by 4,
in_pocket_of 3, under 1.
- **[paper]** `RC_AddAsset` spawns an asset at a given position, rotation and scale.
  `RC_GetComponentInfo` gives a "suggested placement_height" above surface-like parts, which covers
  `on_top`. A figure labels on, under, between, near and inside, but the paper never says how
  `inside` or `under` are placed.
- **[repo]** A layout JSON with explicit item poses can be applied with no language model
  (`apply_layout_update()`). The planner prompt puts items on the floor. There is no `inside`,
  `under` or `next_to` logic.
- **Hidden objects [not stated].** Unreal's normal drawing would hide things inside closed containers.
- **Doors and drawers.** Open/close and jointed parts are claimed [paper]. The repo has a door
  blueprint, one drawer blueprint, and cupboard animations from VirtualEnv [repo].

## 3. Objects

- **[paper]** A "large asset library". Source, licence and size [not stated].
- **[repo]** The registry has 89 entries plus 38 aliases (about 65 household objects). Name matches
  against the snapshot's **187 distinct types**: roughly 8 (apple, plate, milk, towel, book, remote
  control, bowl). Some are stand-ins: "apple" is `SM_AppleSculpture01`, "remote control" is
  `SM_AudioAmplifierController01`. None of these models are in the repo.
- **Same type, different look:** recolouring or retexturing one model is possible
  (`RC_SetMaterialColor`, `RC_SetMaterialTexture`). Distinct models per instance would need a larger
  library.

## 4. People

- **[paper]** "Multi agent interaction" in one place; "single-agent tasks only" in the limitations.
  The only human-shaped figure is a humanoid robot character. Residents [not stated].
- **[repo]** The registry names the UE mannequin and the Echo character, both missing. VirtualEnv's
  Sit, Talk, Wave, Pickup and LookAround animations are present. Nothing seats a person at a given
  place.

## 5. Look

**Untested.** From the paper's figures (copies in `paper_figures/`):
- `POV.jpg`: a clean, lit UE5 bedroom with plain grey slab walls and many ceiling-light pools.
  It looks like an architectural render: no clutter, and no small objects can be made out.
- **[paper]** Walls and floors are "entirely from a single cube asset" on a 100 cm grid.
- `webui.jpg`: untextured box rooms in a Windows browser titled "EnvGen - Simple Builder".
- Small objects at 0.37 m or 1.0 m: [not stated].

## 6. Speed

- **[paper]** 2-5 minutes per generated environment. On an RTX 5090 with a Ryzen 7950X, frame rate
  is capped at 120 fps per instance: 3 instances run at 119.8 fps each, 6 at 86.7, 12 at 53.6. The
  CPU limits scaling. GPU memory [not stated].
- **[checked]** Probe program only, see section 1.

## 7. Robot

- **[paper]** A Franka Panda arm and a Unitree Go1 with discrete navigation actions, RGB, depth and
  masks. The only Go1 figure (`paper_figures/unitree.jpg`) is a white model on black, not in a
  scene. No Go2.
- **[repo]** No robot. The camera is the editor viewport camera, settable over Remote Control.

## 8. Effort to make this the main renderer

**It makes its own environments and cannot take a given HSSD layout.** It writes box rooms on a
grid from a prompt. The explicit-pose layer is a thin wrapper around Unreal's own spawn call and
cannot load an HSSD house. Once HSSD is in Unreal, nothing EnvDreamer-specific is needed.

An Unreal route anyway would need:
1. UE 5.6 or later on Linux (Oliver: Epic account and EULA, about 60 GB or more).
2. HSSD scene `107734254_176000121` and its furniture converted from glTF to UE assets, with
   materials, collision and jointed parts checked.
3. Models for 187 object types, with a licence check for each pack.
4. A loader for `positions_*.json` that places by relation and hides or shows by container state.
5. Offscreen cameras at 0.37 m (100 degrees, up to 15 degrees down) and 1.0 m (75 degrees), via
   UnrealCV or the editor's Movie Render Queue.
6. Optionally, posed people and a Go2 model.
7. A rebuild for every 2-hour snapshot.

That is weeks of work. Habitat with HSSD already does steps 2-5.

**Photo-to-scene for the real lab [paper] [repo]:** one photo goes to a GPT-class model, which
returns the same box-room layout, treating the photo as "soft evidence" and allowed to deviate
from it. Mirrors and glass make it invent rooms. The result is a lookalike lab, not a copy.
Gaussian splatting from the Go2's daily photos, or ACDC digital cousins, would serve that study
better.

**Points that lower confidence in the paper:**
- Unfilled placeholders: "Table ... reserved", "Table S2 will be shown", "Numerical results can be
  inserted into Table S3".
- `envdreamer100k` / `ed100k` labels for a 20k dataset.
- "We release" versus "will release".
- Gains over ProcTHOR of 0.6-1.4 points with spreads of plus or minus 1-2, described as
  "consistent improvements".
- "Indoor and outdoor" in the intro versus "currently indoor" in the dataset section.

## 9. Verdict

Not released: no framework, no dataset, only an unlicensed 2025 Windows editor prototype with its
models missing. It generates its own box-room homes from prompts and cannot render our HSSD
layout; its photo mode makes a lookalike, not a copy. Not a candidate for the main renderer. UE5
itself does render offscreen on our GPU if an Unreal route is ever wanted.

## Released alternatives

The first seven were confirmed to exist (licence noted). The last two are named from memory,
unchecked, because the GitHub API rate limit ran out.

| Tool | How it fits |
|---|---|
| UnrealZoo, https://github.com/UnrealZoo/unrealzoo-gym (Apache-2.0); Linux binaries https://huggingface.co/datasets/UnrealZoo/UnrealZoo_UE5 (UE 5.6/5.7, about 72 GB) | Closest released UE5 option for embodied work: humans, a robot dog and a Unitree Go1, camera control through UnrealCV+. Fixed scenes; our objects would need its spawn API. |
| UnrealCV, https://github.com/unrealcv/unrealcv (MIT, `5.2` branch) | Standard Python camera, RGB, depth and mask control for any Unreal program. |
| Project AirSim, https://github.com/iamaisim/ProjectAirSim (MIT) | Used for the probe. Drone-focused; only useful as a tested UE5 camera harness. |
| Holodeck, https://github.com/allenai/Holodeck (Apache-2.0) | Released text-to-house generator on AI2-THOR with Objaverse models. Same "makes its own homes" limit; uses a hosted language model. |
| ProcTHOR, https://github.com/allenai/procthor (Apache-2.0) | Houses are JSON with explicit object poses, so given placements can be written in. Not HSSD. |
| ACDC "Digital Cousins", https://github.com/cremebrule/digital-cousins (Apache-2.0) | Real photo to matched BEHAVIOR models in OmniGibson: the released form of EnvDreamer's photo-to-scene idea. Relevant to the real lab and to the BEHAVIOR trial. |
| LayoutVLM, https://github.com/sunfanyunn/LayoutVLM (no licence file) | A vision-language model places a given object list in a given room. Could fill in poses for objects without exact spots. |
| Infinigen Indoors, https://github.com/princeton-vl/infinigen (BSD-3) | Photographic procedural homes in Blender; makes its own homes and is slow. |
| Gaussian splatting, nerfstudio / gsplat (https://github.com/nerfstudio-project) | Unchecked. Strongest released route to a simulated copy of the photographed lab that looks like the real camera. Objects are not separable without extra work. |

## Files

- `ue5_probe_capture.py`: the offscreen probe script.
- `ue5_probe/` (`blocks_*.png`, `probe_views.json`, `projectairsim_client.log`): probe output, not
  test views; camera heights unreliable.
- `paper_figures/` (`POV.jpg`, `unitree.jpg`, `webui.jpg`): downscaled paper figures.
