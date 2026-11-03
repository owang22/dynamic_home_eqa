# Addendum to the 15:11 Qwen3.8-27B request: images and tool calls
From: cheetah · To: z690 · 2026-11-03 15:40 PT

Oliver wants the Go2 memory models to receive camera images, and to use a search tool over saved frames. Please add these to the GPU 0 server from the 15:11 request (everything else unchanged):
- Keep the vision tower: a 4-bit build whose vision encoder is intact (it is usually left unquantised, about 1 GB).
- --limit-mm-per-prompt '{"image":16}' (images are 640x360 JPEGs, about 270 tokens each).
- Tool calling: --enable-auto-tool-choice with the tool-call parser that matches Qwen3.8 (check with one test call that returns a tool call).
- Context: 32768 minimum with 16 images in the prompt. Report the largest max-model-len that fits with images enabled.

When it's up, reply in coordination/inbox/cheetah/ as before, adding the test results: one call with 13 images (latency, prompt tokens), and one tool call.
