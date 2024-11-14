import { CONFIG, html } from "../constants";
import type { Supplier, Document } from "../types";
import { formatCPFAndCNPJ } from "../utils";

function statusColor(status?: string): string {
    if (!status) {
        return "text-white";
    }

    switch (status.toLowerCase()) {
        case "válida":
            return "text-[var(--green-highlight)]";
        case "renovação/válida":
            return "text-[var(--green-highlight)]";
        case "vencida":
            return "text-[var(--highlight)]";
        default:
            return "text-white";
    }
}

function linkfy(value: string, link?: string) {
    if (!link) {
        return value;
    }

    return html`
        <a
            href="${CONFIG.fileServerBaseUrl}/${link}"
            class="hover:text-slate-300"
            target="_blank"
            rel="noopener noreferrer"
            >${value}</a
        >
    `;
}

function documentTableRow(label: string, document: Document) {
    return html`
        <tr class="border-slate-800 border-b">
            <td class="px-4 py-3">
                <div class="flex items-center text-slate-400 gap-2">
                    <i class="ph-fill ph-file-text"></i>
                    <span class="font-medium text-sm">${label}</span>
                </div>
            </td>
            <td class="text-right px-4 py-3">
                <span class="font-medium text-sm">${linkfy(document.name, document?.filepath)}</span>
            </td>
            <td class="text-right px-4 py-3 w-fit">
                <span class="font-medium ${statusColor(document?.status)} text-sm"
                    >${(document?.status || "AUSENTE").toUpperCase()}</span
                >
            </td>
        </tr>
    `;
}

export function SupplierCard(supplier: Supplier, borderColor: string, ratingColor: string): string {
    const distanciaFmt =
        supplier.distance_in_meters !== null
            ? `${Math.round((supplier.distance_in_meters / 1000) * 10) / 10} km`
            : "N/A";

    const avaliacaoFmt = supplier.rating || "N/A";

    const documents = supplier.documents
        .map((document) => {
            console.log(document);
            return documentTableRow(document.type.toUpperCase(), document);
        })
        .join("");

    return html`
        <div class="p-3 w-full text-slate-200" id="supplier-card-template">
            <div
                id="card"
                style="border-color: ${borderColor};"
                class="bg-dark-200 bg-opacity-60 shadow-lg hover:shadow-xl px-4 py-4 border-t-[3px] rounded-lg w-full max-w-full fixtransition transition-transform hover:translate-x-1 duration-300"
            >
                <div class="flex justify-between w-full text-md">
                    <div class="flex flex-col w-full gap-1">
                        <p
                            class="mb-3 font-medium w-fullbg-violet-600 verflow-hidden text-ellipsis text-white"
                        >
                            ${supplier.corporate_name}
                        </p>
                        <div class="flex items-center w-full gap-4">
                            <i class="ph-map-pin ph-fill"></i>
                            <span class="font-medium">${supplier.city.name} - ${supplier.state.abbr}</span>
                        </div>
                        <div class="flex items-center gap-4">
                            <i class="ph-fill ph-identification-card"></i>
                            <span class="font-medium">${formatCPFAndCNPJ(supplier.cpf_cnpj)}</span>
                        </div>

                        <div class="flex items-center gap-4">
                            <i class="ph-fill ph-package"></i>
                            <span class="font-medium">${supplier.material_type}</span>
                        </div>
                    </div>
                    <div class="flex justify-end gap-2 ml-5 w-fit max-w-fit">
                        <div
                            class="flex items-center gap-2 bg-black bg-opacity-20 px-3 py-1 rounded-md w-fit h-fit"
                        >
                            <i class="ph-fill ph-path text-xl"></i>
                            <span class="font-medium text-nowrap">${distanciaFmt}</span>
                        </div>
                        <div
                            class="flex items-center gap-2 bg-black bg-opacity-20 px-3 py-1 rounded-md w-fit h-fit text-green-300"
                            id="supplier-rating"
                        >
                            <i class="ph-fill ph-star text-xl"></i>
                            <span class="font-medium">${avaliacaoFmt}</span>
                        </div>
                    </div>
                </div>
                <div class="mt-5 w-full">
                    <div class="bg-black bg-opacity-20 shadow-sm rounded-lg overflow-hidden">
                        <table class="w-full">
                            <tbody>
                                <tr class="border-slate-800 border-b">
                                    ${documents}
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}
