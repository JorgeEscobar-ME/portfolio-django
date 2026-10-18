(function () {
    window.createImageSizeToolbarButton = function () {
        return {
            name: "image-size",
            title: "Tamaño de imagen",
            className: "fa fa-arrows-h",
            action: function (editor) {
                const codeMirror = editor.codemirror;
                const selectedText = codeMirror.getSelection();
                if (!selectedText) {
                    window.alert(
                        "Selecciona primero el Markdown de una o más imágenes."
                    );
                    return;
                }

                const imagePattern =
                    /(!\[[^\]]*\]\([^)\n]+\))(?:\s*\{\s*width\s*=\s*\d+\s*\})?/g;
                if (!imagePattern.test(selectedText)) {
                    window.alert(
                        "La selección no contiene Markdown de imagen con el formato ![texto](URL)."
                    );
                    return;
                }

                const selectionStart = codeMirror.getCursor("from");
                const selectionEnd = codeMirror.getCursor("to");
                const dialog = document.createElement("dialog");
                dialog.className = "markdown-image-size-dialog";

                const form = document.createElement("form");
                form.className = "markdown-image-size-dialog__form";

                const heading = document.createElement("h2");
                heading.id = "markdown-image-size-title";
                heading.textContent = "Cambiar tamaño de imagen";

                const label = document.createElement("label");
                label.htmlFor = "markdown-image-size-width";
                label.textContent = "Ancho en píxeles (100-900)";

                const input = document.createElement("input");
                input.id = "markdown-image-size-width";
                input.type = "number";
                input.name = "width";
                input.min = "100";
                input.max = "900";
                input.step = "1";
                input.required = true;
                input.value =
                    selectedText.match(/\{\s*width\s*=\s*(\d+)\s*\}/)?.[1] ||
                    "480";

                const actions = document.createElement("div");
                actions.className = "markdown-image-size-dialog__actions";

                const cancelButton = document.createElement("button");
                cancelButton.type = "button";
                cancelButton.className = "markdown-image-size-dialog__cancel";
                cancelButton.textContent = "Cancelar";
                cancelButton.addEventListener("click", () => dialog.close());

                const applyButton = document.createElement("button");
                applyButton.type = "submit";
                applyButton.className = "markdown-image-size-dialog__apply";
                applyButton.textContent = "Aplicar";

                actions.append(cancelButton, applyButton);
                form.append(heading, label, input, actions);
                dialog.append(form);
                dialog.setAttribute("aria-labelledby", heading.id);
                dialog.addEventListener("close", () => dialog.remove(), {
                    once: true,
                });
                form.addEventListener("submit", (event) => {
                    event.preventDefault();
                    if (!input.reportValidity()) {
                        return;
                    }

                    const width = Number(input.value);
                    codeMirror.replaceRange(
                        selectedText.replace(
                            imagePattern,
                            (_, image) => `${image}{ width=${width} }`
                        ),
                        selectionStart,
                        selectionEnd,
                        "image-size"
                    );
                    codeMirror.focus();
                    dialog.close();
                });

                document.body.append(dialog);
                dialog.showModal();
                input.focus();
                input.select();
            },
        };
    };
})();
