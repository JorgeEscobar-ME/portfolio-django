# Student projects

The existing `projects` Django app supports mixed project pages. Any combination
of article text, a YouTube video, and Python code can be added to one project.
Projects marked as drafts are visible to staff in the Django admin but not to
public visitors. Existing projects remain published by default.

## Admin workflow

1. Create a project from **Admin > Projects** and fill in its title, slug,
   summary, description, and student authors.
2. For a written article, use **Contenido del artículo**. It has the blog's
   Markdown editor and supports inline `$...$` and display `$$...$$` LaTeX.
3. For a video, paste its URL in **Enlace del video**. Supported YouTube links
   are embedded on the public page; other valid URLs are shown as external links.
   Add a video summary, main results, and conclusions in their corresponding
   fields.
4. AI-generated summaries must currently be generated outside this site and
   pasted into the admin fields. The site does not send video URLs or content to
   an AI provider.
5. Python source is displayed as escaped, read-only text. If students should be
   able to run it, add a Google Colab link. This site never executes submitted
   code or embeds an external execution environment.
6. Keep a project as **Borrador** until it is ready to publish.

Apply the project schema changes locally before using the new fields:

```powershell
python manage.py migrate
```

## Execution and content safety

Python project code is never evaluated or run on the Django host. Google Colab
is linked in a separate tab rather than embedded into the portfolio. Visitors
who run a notebook do so in Google's environment and should review the code
before execution.

Article Markdown is processed through the same sanitizer as blog posts. Video
embeds are generated only for recognized YouTube URL formats and use YouTube's
privacy-enhanced host. External links opened in a new tab use `noopener
noreferrer`.
