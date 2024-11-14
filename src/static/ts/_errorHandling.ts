window.onerror = function (message, source, lineno, colno, _) {
    const errorElement = document.createElement("div");
    errorElement.style.position = "fixed";
    errorElement.style.bottom = "20px";
    errorElement.style.right = "20px";
    errorElement.style.padding = "15px 20px";
    errorElement.style.backgroundColor = "#c93a3a";
    errorElement.style.color = "#fff";
    errorElement.style.fontSize = "16px";
    errorElement.style.borderRadius = "8px";
    errorElement.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
    errorElement.style.maxWidth = "600px";
    errorElement.style.zIndex = "1000";
    errorElement.style.transition = "opacity 0.5s";

    errorElement.innerHTML = `
        <strong>Ocorreu um erro!</strong><br>
        ${message} <br>
        <small>(${source} - linha ${lineno}, coluna ${colno})</small>
    `;

    document.body.appendChild(errorElement);

    setTimeout(() => {
        errorElement.style.opacity = "0";
        setTimeout(() => {
            errorElement.remove();
        }, 500);
    }, 5000);

    return true;
};
