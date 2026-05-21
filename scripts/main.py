"""
Prompt Formatter - cleans up whitespace, commas, and newlines in prompts before generation.

Features:
  - Removes spaces before commas
  - Ensures single space after commas
  - Collapses consecutive commas
  - Replaces newlines with spaces
  - Strips leading/trailing whitespace and commas
  - Collapses multiple whitespace into single space
  - Enable/disable toggle in the UI
  - Preview button reads directly from the main prompt textbox
  - Manual test input for experimenting
"""

import re

import gradio as gr

import modules.scripts as scripts
from modules import script_callbacks


# --- Prompt textbox references (captured via on_after_component) ---

txt2img_prompt_textbox = None
img2img_prompt_textbox = None


def _on_after_component(component, **_kwargs):
    eid = getattr(component, "elem_id", None)
    if eid == "txt2img_prompt":
        global txt2img_prompt_textbox
        txt2img_prompt_textbox = component
    elif eid == "img2img_prompt":
        global img2img_prompt_textbox
        img2img_prompt_textbox = component


script_callbacks.on_after_component(_on_after_component)


# --- Formatting logic ---


def format_prompt(text: str) -> str:
    """Clean up a prompt string.

    * Replaces newlines (\\n, \\r\\n) with spaces
    * Removes spaces *before* a comma
    * Normalises to a single space after each comma
    * Collapses consecutive commas into one
    * Collapses runs of whitespace into a single space
    * Strips leading / trailing whitespace and commas
    """
    if not text:
        return ""

    # 1. Replace newlines with spaces
    text = text.replace("\r\n", " ").replace("\n", " ")

    # 2. Collapse consecutive commas into one
    text = re.sub(r",+", ",", text)

    # 3. Remove whitespace before a comma  (e.g. "tag1 , tag2" -> "tag1, tag2")
    text = re.sub(r"\s+,", ",", text)

    # 4. Normalise to exactly ", " (single space after comma)
    text = re.sub(r",\s*", ", ", text)

    # 5. Collapse any remaining runs of whitespace
    text = re.sub(r"\s+", " ", text)

    # 6. Strip leading/trailing whitespace and commas
    text = text.strip().strip(",").strip()

    return text


# --- Gradio Script ---


class Script(scripts.Script):
    sorting_priority = 15.2

    def title(self):
        return "Prompt Formatter"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("Prompt Formatter", open=False):
            enabled = gr.Checkbox(
                False,
                label="Enable prompt formatting",
                elem_id=self.elem_id("enabled"),
            )

            # --- Preview section: reads from the main prompt textbox ---
            with gr.Row():
                preview_btn = gr.Button(
                    "Preview formatted prompt",
                    elem_id=self.elem_id("preview_btn"),
                    scale=1,
                )
                preview_output = gr.Textbox(
                    label="Formatted preview",
                    lines=2,
                    interactive=False,
                    elem_id=self.elem_id("preview_output"),
                    scale=2,
                )

            # Wire up the preview button.
            # The actual prompt textbox is captured via on_after_component above.
            prompt_textbox = (
                img2img_prompt_textbox if is_img2img else txt2img_prompt_textbox
            )

            if prompt_textbox is not None:
                preview_btn.click(
                    fn=format_prompt,
                    inputs=[prompt_textbox],
                    outputs=[preview_output],
                )

            # --- Manual section: type any text to test formatting ---
            with gr.Row():
                manual_input = gr.Textbox(
                    label="Manual test input",
                    lines=2,
                    placeholder="Type any prompt here to test formatting...",
                    elem_id=self.elem_id("manual_input"),
                    scale=1,
                )
                manual_output = gr.Textbox(
                    label="Manual formatted",
                    lines=2,
                    interactive=False,
                    elem_id=self.elem_id("manual_output"),
                    scale=1,
                )

            manual_input.change(
                fn=format_prompt,
                inputs=[manual_input],
                outputs=[manual_output],
            )

        return [enabled]

    def before_process_batch(self, p, enabled, *args, **kwargs):
        # Allow XYZ Grid to override the UI toggle
        if hasattr(p, "prompt_formatter_enabled"):
            enabled = p.prompt_formatter_enabled

        if not enabled:
            return

        batch_number = kwargs.get("batch_number", 0)
        bs = p.batch_size

        # Format positive prompts
        for i, raw in enumerate(p.prompts):
            formatted = format_prompt(raw)
            p.prompts[i] = formatted
            idx = batch_number * bs + i
            if idx < len(p.all_prompts):
                p.all_prompts[idx] = formatted

        # Format negative prompts
        for i, raw in enumerate(p.negative_prompts):
            formatted = format_prompt(raw)
            p.negative_prompts[i] = formatted
            idx = batch_number * bs + i
            if idx < len(p.all_negative_prompts):
                p.all_negative_prompts[idx] = formatted
