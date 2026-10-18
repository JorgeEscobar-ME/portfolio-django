document.addEventListener("DOMContentLoaded", function () {
    const contentField = document.getElementById("id_article_content");

    if (!contentField) {
        return;
    }

    if (typeof EasyMDE === "undefined") {
        console.error("The Markdown editor could not be loaded.");
        return;
    }

    new EasyMDE({
        element: contentField,
        spellChecker: false,
        minHeight: "420px",
        placeholder: "Escribe el artículo del proyecto en Markdown...",
        status: ["lines", "words", "cursor"],
        toolbar: [
            "bold",
            "italic",
            "heading",
            "|",
            "quote",
            "unordered-list",
            "ordered-list",
            "|",
            "link",
            "image",
            "table",
            "code",
            "horizontal-rule",
            "|",
            "preview",
            "side-by-side",
            "fullscreen",
            "guide",
        ],
    });
});
