import Alpine from "alpinejs";

import "@phosphor-icons/web/bold/style.css";
import "@phosphor-icons/web/fill/style.css";
import "@phosphor-icons/web/regular/style.css";
import "htmx.org";

Alpine.start();

let timeoutId: any = null;

/*
    Função usada por `components/copyable_text.html`
    para copiar o texto de um elemento que contem
    o atributo `data-value`
*/
function copyText(element: any) {
    const value = element.getAttribute("data-value");

    const allCopyableTexts = document.querySelectorAll(".copyable-text");
    allCopyableTexts.forEach((el) => el.classList.remove("copied"));

    navigator.clipboard.writeText(value).then(() => {
        element.classList.add("copied");

        if (timeoutId) {
            clearTimeout(timeoutId);
        }

        timeoutId = setTimeout(() => {
            element.classList.remove("copied");
        }, 1000);
    });
}

(window as any).copyText = copyText;
