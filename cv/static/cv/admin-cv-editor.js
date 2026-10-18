document.addEventListener("DOMContentLoaded", function () {
    const textareas = document.querySelectorAll("textarea.markdown-editor");

    if (!textareas.length) {
        return;
    }

    if (typeof EasyMDE === "undefined") {
        console.error("The Markdown editor could not be loaded.");
        return;
    }

    textareas.forEach(function (textarea) {
        new EasyMDE({
            element: textarea,
            spellChecker: false,
            minHeight: "220px",
            placeholder: "Escribe en Markdown. Puedes crear listas con la barra de herramientas.",
            status: ["lines", "words", "cursor"],
            toolbar: [
                "bold",
                "italic",
                "heading",
                "|",
                "unordered-list",
                "ordered-list",
                "quote",
                "|",
                "link",
                "image",
                window.createImageSizeToolbarButton(),
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
});
