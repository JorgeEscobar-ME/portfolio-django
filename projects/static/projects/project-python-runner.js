document.addEventListener("DOMContentLoaded", function () {
    const runner = document.querySelector("[data-python-runner]");
    const codeElement = document.getElementById("project-python-code");

    if (!runner || !codeElement) {
        return;
    }

    const runButton = runner.querySelector("[data-run]");
    const stopButton = runner.querySelector("[data-stop]");
    const status = runner.querySelector("[data-status]");
    const output = runner.querySelector("[data-output]");
    const plots = runner.querySelector("[data-plots]");
    const frame = runner.querySelector("[data-runner-frame]");
    const code = JSON.parse(codeElement.textContent);
    const pyodideVersion = "0.27.7";
    const pyodideUrl = `https://cdn.jsdelivr.net/pyodide/v${pyodideVersion}/full/`;
    const loadTimeoutMs = 120000;
    const packageTimeoutMs = 90000;
    const runTimeoutMs = 15000;
    const maxOutputChars = 50000;
    const maxPlotChars = 2000000;
    let loadTimer;
    let packageTimer;
    let runTimer;
    let outputLength = 0;
    let currentRun = 0;
    let pythonReady = false;
    let restartMessage = "";

    function appendOutput(text) {
        const remaining = maxOutputChars - outputLength;
        if (remaining <= 0) {
            return;
        }

        const clipped = text.slice(0, remaining);
        output.append(document.createTextNode(clipped));
        outputLength += clipped.length;
        if (clipped.length < text.length) {
            output.append(document.createTextNode("\n[Salida truncada.]"));
            outputLength = maxOutputChars;
        }
    }

    function setReady(message) {
        window.clearTimeout(loadTimer);
        window.clearTimeout(packageTimer);
        window.clearTimeout(runTimer);
        runButton.disabled = false;
        runButton.textContent = "Ejecutar código";
        stopButton.disabled = true;
        status.textContent = message;
    }

    function resetOutput() {
        output.textContent = "";
        plots.replaceChildren();
        outputLength = 0;
    }

    function sendToFrame(message) {
        if (frame && frame.contentWindow) {
            frame.contentWindow.postMessage(message, "*");
        }
    }

    function createFrame() {
        runButton.disabled = true;
        runButton.textContent = "Cargando Python...";
        stopButton.disabled = true;
        status.textContent = "Preparando el entorno aislado de Python...";

        frame.srcdoc = `<!doctype html>
<html><head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' 'wasm-unsafe-eval' https://cdn.jsdelivr.net; connect-src https://cdn.jsdelivr.net; worker-src blob:; img-src data:; style-src 'unsafe-inline'; object-src 'none'; base-uri 'none'; form-action 'none'">
</head><body><script>
const pyodideUrl = ${JSON.stringify(pyodideUrl)};
let worker;
let workerUrl;

function report(message) {
    parent.postMessage(message, "*");
}

function startWorker() {
    if (worker) {
        worker.terminate();
    }
    if (workerUrl) {
        URL.revokeObjectURL(workerUrl);
    }

    const bridgeKey = Array.from(
        crypto.getRandomValues(new Uint8Array(16)),
        (byte) => byte.toString(16).padStart(2, "0")
    ).join("");
    const workerSource = \`
importScripts(\${JSON.stringify(pyodideUrl + "pyodide.js")});

(() => {
let pyodide;
let busy = false;
let bridgeKey;

function send(message) {
    self.postMessage({ ...message, bridgeKey });
}

async function initialize() {
    pyodide = await loadPyodide({ indexURL: \${JSON.stringify(pyodideUrl)} });
    send({ type: "ready" });
}

self.onmessage = async (event) => {
    const message = event.data;
    if (!message || typeof message !== "object") {
        return;
    }
    if (message.type === "configure" && typeof message.bridgeKey === "string") {
        bridgeKey = message.bridgeKey;
        initialize().catch((error) => send({ type: "error", text: String(error) }));
        return;
    }
    if (message.type !== "run" || busy || typeof message.code !== "string") {
        return;
    }

    busy = true;
    const usesMatplotlib = message.code
        .split(String.fromCharCode(10))
        .some((line) => {
            const trimmedLine = line.trimStart();
            return (
                trimmedLine.startsWith("import matplotlib") ||
                trimmedLine.startsWith("from matplotlib")
            );
        });
    try {
        await pyodide.loadPackagesFromImports(message.code);
    } catch (error) {
        busy = false;
        send({ type: "error", runId: message.runId, text: String(error) });
        return;
    }
    send({ type: "started", runId: message.runId });
    pyodide.setStdout({
        batched: (text) =>
            send({
                type: "output",
                runId: message.runId,
                text: text + String.fromCharCode(10),
            }),
    });
    pyodide.setStderr({
        batched: (text) =>
            send({
                type: "output",
                runId: message.runId,
                text: text + String.fromCharCode(10),
            }),
    });
    pyodide.globals.set("project_source", message.code);
    pyodide.globals.set("send_project_plot", (image) => {
        send({ type: "plot", runId: message.runId, image });
    });

    try {
        if (usesMatplotlib) {
            await pyodide.runPythonAsync(
                "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; plt.show = lambda *args, **kwargs: None"
            );
        }
        await pyodide.runPythonAsync(
            "exec(compile(project_source, '<project>', 'exec'), {'__name__': '__main__'})"
        );
        const plottingSource = [
            "import base64",
            "import io",
            "import sys",
            "",
            'if "matplotlib.pyplot" in sys.modules:',
            "    import matplotlib.pyplot as plt",
            "    for figure_number in plt.get_fignums():",
            "        image_buffer = io.BytesIO()",
            '        plt.figure(figure_number).savefig(image_buffer, format="png", bbox_inches="tight")',
            '        send_project_plot(base64.b64encode(image_buffer.getvalue()).decode("ascii"))',
            "        plt.close(figure_number)",
        ].join("\\\\n");
        await pyodide.runPythonAsync(plottingSource);
        send({ type: "complete", runId: message.runId });
    } catch (error) {
        send({ type: "error", runId: message.runId, text: String(error) });
    } finally {
        busy = false;
    }
};

})();
\`;

    workerUrl = URL.createObjectURL(
        new Blob([workerSource], { type: "text/javascript" })
    );
    worker = new Worker(workerUrl);
    worker.onmessage = (event) => {
        if (!event.data || event.data.bridgeKey !== bridgeKey) {
            return;
        }
        const { bridgeKey: _bridgeKey, ...message } = event.data;
        report(message);
    };
    worker.onerror = (event) => {
        report({ type: "error", text: event.message || "No se pudo iniciar Python." });
    };
    worker.postMessage({ type: "configure", bridgeKey });
}

window.addEventListener("message", (event) => {
    if (event.source !== parent || !event.data || typeof event.data !== "object") {
        return;
    }
    if (event.data.type === "run") {
        if (worker) {
            worker.postMessage(event.data);
        }
    } else if (event.data.type === "reset") {
        startWorker();
    }
});

startWorker();
<\/script></body></html>`;

        loadTimer = window.setTimeout(() => {
            runButton.disabled = false;
            runButton.textContent = "Reintentar Python";
            stopButton.disabled = true;
            status.textContent = "La carga tardó demasiado. Puedes volver a intentarlo.";
            sendToFrame({ type: "reset" });
        }, loadTimeoutMs);
    }

    window.addEventListener("message", (event) => {
        if (!frame || event.source !== frame.contentWindow || !event.data) {
            return;
        }

        const message = event.data;
        if (message.type === "ready") {
            window.clearTimeout(loadTimer);
            window.clearTimeout(packageTimer);
            pythonReady = true;
            runButton.disabled = false;
            runButton.textContent = "Ejecutar código";
            status.textContent = restartMessage || "Python está listo.";
            restartMessage = "";
        } else if (message.type === "started" && message.runId === currentRun) {
            window.clearTimeout(packageTimer);
            status.textContent = "Código en ejecución...";
            runTimer = window.setTimeout(() => {
                sendToFrame({ type: "reset" });
                pythonReady = false;
                restartMessage =
                    "Ejecución detenida al superar el límite de 15 segundos. Python está listo para otra ejecución.";
                runButton.disabled = true;
                runButton.textContent = "Cargando Python...";
                stopButton.disabled = true;
                status.textContent = "Se detuvo el código. Reiniciando Python...";
            }, runTimeoutMs);
        } else if (message.type === "output" && message.runId === currentRun) {
            if (typeof message.text === "string") {
                appendOutput(message.text);
            }
        } else if (
            message.type === "plot" &&
            message.runId === currentRun &&
            typeof message.image === "string" &&
            message.image.length <= maxPlotChars &&
            /^[A-Za-z0-9+/=]+$/.test(message.image)
        ) {
            const image = document.createElement("img");
            image.alt = "Gráfica generada por el código Python";
            image.src = `data:image/png;base64,${message.image}`;
            plots.append(image);
        } else if (message.type === "complete" && message.runId === currentRun) {
            window.clearTimeout(runTimer);
            setReady("Ejecución finalizada.");
        } else if (message.type === "error") {
            window.clearTimeout(loadTimer);
            window.clearTimeout(packageTimer);
            window.clearTimeout(runTimer);
            appendOutput(message.text || "Error al preparar Python.");
            if (message.runId === currentRun) {
                setReady("El código terminó con un error.");
            } else {
                pythonReady = false;
                runButton.disabled = false;
                runButton.textContent = "Reintentar Python";
                stopButton.disabled = true;
                status.textContent = "No se pudo cargar Python. Puedes volver a intentarlo.";
            }
        }
    });

    runButton.addEventListener("click", function () {
        if (!pythonReady) {
            resetOutput();
            runButton.disabled = true;
            runButton.textContent = "Cargando Python...";
            status.textContent = "Volviendo a preparar Python...";
            sendToFrame({ type: "reset" });
            loadTimer = window.setTimeout(() => {
                runButton.disabled = false;
                runButton.textContent = "Reintentar Python";
                status.textContent = "La carga tardó demasiado. Puedes volver a intentarlo.";
            }, loadTimeoutMs);
            return;
        }

        resetOutput();
        currentRun += 1;
        runButton.disabled = true;
        stopButton.disabled = false;
        status.textContent = "Cargando los paquetes necesarios...";
        packageTimer = window.setTimeout(() => {
            sendToFrame({ type: "reset" });
            pythonReady = false;
            restartMessage = "La carga del paquete excedió su límite. Python está listo para intentar de nuevo.";
            runButton.disabled = true;
            runButton.textContent = "Cargando Python...";
            stopButton.disabled = true;
            status.textContent =
                "La carga del paquete tardó demasiado. Reiniciando Python...";
        }, packageTimeoutMs);
        sendToFrame({ type: "run", runId: currentRun, code });
    });

    stopButton.addEventListener("click", function () {
        window.clearTimeout(packageTimer);
        window.clearTimeout(runTimer);
        sendToFrame({ type: "reset" });
        pythonReady = false;
        restartMessage = "Ejecución detenida. Python está listo para otra ejecución.";
        runButton.disabled = true;
        runButton.textContent = "Cargando Python...";
        stopButton.disabled = true;
        status.textContent = "Ejecución detenida; reiniciando Python...";
    });

    createFrame();
});
