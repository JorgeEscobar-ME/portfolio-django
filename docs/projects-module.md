# Student projects

The existing `projects` Django app supports mixed project pages. The project
list displays responsive cards, with an optional cover image and a visual
fallback when no image is set. Any combination of article text, a YouTube video,
and Python code can be added to one project.
Projects marked as drafts are visible to staff in the Django admin but not to
public visitors. Existing projects remain published by default.

## Admin workflow

1. Create a project from **Admin > Projects** and fill in its title, slug,
   summary, description, and student authors. Optionally upload an **Imagen de
   portada**; the admin shows a preview, and cards have a built-in fallback if
   you leave it empty.
2. For a written article, use **Contenido del artículo**. It has the blog's
   Markdown editor and supports inline `$...$` and display `$$...$$` LaTeX.
   Images are centered and constrained to 900 px. Select an image's Markdown
   in the editor and use **Tamaño de imagen** to choose a smaller width.
   The corresponding Markdown syntax is
   `![Description](https://example.com/image.png){ width=420 }`; widths outside
   100-900 px are discarded.
3. For a video, paste its URL in **Enlace del video**. Supported YouTube links
   are embedded on the public page; other valid URLs are shown as external links.
   Add a video summary, main results, and conclusions in their corresponding
   fields.
4. AI-generated summaries must currently be generated outside this site and
   pasted into the admin fields. The site does not send video URLs or content to
   an AI provider.
5. Python source is displayed as escaped, read-only text and can be run in the
   visitor's browser in a sandboxed Web Worker inside an opaque-origin iframe.
   Standard-library code runs directly; NumPy, SciPy, and Matplotlib are loaded
   from Pyodide on demand. Matplotlib figures are shown below the console.
   PyTorch and arbitrary pip installs are not supported. Add a Google Colab link
   for projects requiring unsupported libraries.
6. Keep a project as **Borrador** until it is ready to publish.

Apply the project schema changes locally before using the new fields:

```powershell
python manage.py migrate
```

## Execution and content safety

Python project code is never evaluated or run on the Django host. It runs in a
browser Worker isolated inside an iframe with the `allow-scripts` sandbox flag,
an opaque origin, and a Content Security Policy restricting network access to
the pinned Pyodide CDN. The runner caps execution time and captured output,
renders text output without interpreting HTML, and lets visitors stop a run.
The console captures printed output; it does not provide interactive terminal
input such as `input()`.
This is not a substitute for reviewing student code: published code can still
consume browser resources, so only run reviewed projects. The code is
non-editable in the page UI, but visitors can still inspect it or alter their
own browser using developer tools.

Google Colab is linked in a separate tab rather than embedded into the
portfolio. Visitors who run a notebook do so in Google's environment and should
review the code before execution.

Article Markdown is processed through the same sanitizer as blog posts. Video
embeds are generated only for recognized YouTube URL formats and use YouTube's
privacy-enhanced host. External links opened in a new tab use `noopener
noreferrer`.

Links throughout the site use a contrasting color and underline, with an
outbound-link marker for links that open in a new tab. Navigation and brand
links keep their compact header styling.
