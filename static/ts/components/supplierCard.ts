import { APP_CONFIG, html } from "../constants";
import type { Supplier, Document } from "../types";
import { formatCPFAndCNPJ, roundNumber } from "../utils";

function getValidityStatusAndColor(document: Document): [string, string] {
    if (!document.validity) {
        return ["AUSENTE", "text-white"];
    }

    const now = new Date();
    const validityDate = new Date(document.validity);

    const nowUTC = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
    const validityUTC = new Date(
        Date.UTC(validityDate.getFullYear(), validityDate.getMonth(), validityDate.getDate())
    );

    const diffInDays = Math.floor((validityUTC.getTime() - nowUTC.getTime()) / (1000 * 60 * 60 * 24));

    if (diffInDays < 0) {
        return ["VENCIDO", "text-primary"];
    } else if (diffInDays <= 30) {
        return [`VENCE EM ${diffInDays} DIAS`, "text-primary"];
    } else {
        return ["VÁLIDO", "text-secondary"];
    }
}

function linkfy(value: string, link?: string) {
    if (!link) {
        return value;
    }
    return html` <a href="${link}" class="hover:text-slate-300" target="_blank">${value}</a> `;
}

function documentTableRow(label: string, document: Document) {
    const [validityStatus, validityColor] = getValidityStatusAndColor(document);

    return html`
        <tr class="border-dark-200 border-b">
            <td class="px-4 py-3">
                <div class="flex items-center text-slate-400 gap-2">
                    <i class="ph-fill ph-file-text"></i>
                    <span class="font-medium text-sm">${label}</span>
                </div>
            </td>
            <td class="text-center px-4 py-3">
                <span class="font-medium text-sm">${linkfy(document.name, document?.filepath)}</span>
            </td>
            <td class="text-right px-4 py-3 w-fit">
                <span class="font-medium ${validityColor} text-sm">${validityStatus}</span>
            </td>
        </tr>
    `;
}

function charcoalStats(supplier: Supplier) {
    if (!supplier.charcoal_recent_stats || supplier.material_type !== "Carvão Vegetal") {
        return "";
    }

    return html`
        <div class="mt-5 w-full bg-black bg-opacity-20 shadow-sm rounded-md overflow-hidden">
            <div
                class="px-4 w-full font-semibold text-[0.6rem] text-slate-500 flex justify-between items-center py-2"
            >
                <p>
                    QUALIDADE RECENTE DO CARVÃO - MÉDIA DAS ULTIMAS ${supplier.charcoal_recent_stats.count}
                    ENTREGAS
                </p>
                <p>${supplier.charcoal_recent_stats.period}</p>
            </div>
            <div class=" w-full grid grid-cols-3 grid-rows-1 text-sm">
                <div
                    class="px-4 border-slate-800 font-medium border-r flex justify-between  items-center py-3"
                >
                    <span class="text-slate-400">DENSIDADE</span>
                    <span>${roundNumber(supplier.charcoal_recent_stats.average_density)}</span>
                </div>
                <div
                    class="px-4 border-slate-800 font-medium border-r flex justify-between  items-center py-3"
                >
                    <span class="text-slate-400">UMIDADE</span>
                    <span>${roundNumber(supplier.charcoal_recent_stats.average_moisture)}</span>
                </div>
                <div class="px-4 flex justify-between font-medium items-center py-3">
                    <span class="text-slate-400">FINOS</span>
                    <span>${roundNumber(supplier.charcoal_recent_stats.average_fines)}</span>
                </div>
            </div>
        </div>
    `;
}

export function SupplierCard(supplier: Supplier, borderColor: string, ratingColor: string) {
    const ratingFmt = supplier.rating || " - ";

    const distanceFmt =
        supplier.distance_in_meters !== null
            ? `${Math.round((supplier.distance_in_meters / 1000) * 10) / 10} km`
            : " - ";

    const documentRows = supplier.documents.reduce(
        (rows, document) => rows + documentTableRow(document.type.toUpperCase(), document),
        ""
    );

    const hasDocuments = supplier.documents.length > 0;

    return html`
        <div class="p-3 w-full text-slate-200" id="supplier-card-template">
            <div
                id="card"
                style="border-color: ${borderColor};"
                class="bg-dark-200 bg-opacity-60 shadow-lg hover:shadow-xl px-4 py-4 border-t-[3px] rounded-md w-full max-w-full fixtransition transition-transform hover:translate-x-1 duration-300"
            >
                <div class="flex justify-between w-full text-md overflow-hidden">
                    <div class="flex flex-col gap-1 text-nowrap overflow-hidden">
                        <div
                            class="mb-3 w-full font-medium text-ellipsis text-white hover:text-wrap overflow-hidden"
                        >
                            ${supplier.corporate_name}
                        </div>
                        <div class="flex items-center pt-4 text-sm gap-4 w-full">
                            <i class="ph-map-pin ph-fill"></i>
                            <span class="font-medium">${supplier.city.name} - ${supplier.state.abbr}</span>
                        </div>
                        <div class="flex items-center text-sm gap-4">
                            <i class="ph-fill ph-identification-card"></i>
                            <span class="font-medium">${formatCPFAndCNPJ(supplier.cpf_cnpj)}</span>
                        </div>
                        <div class="flex items-center text-sm gap-4">
                            <i class="ph-fill ph-package"></i>
                            <span class="font-medium">${supplier.material_type}</span>
                        </div>
                        <div class="flex items-center text-slate-400 group mb-4 text-sm gap-4">
                            <i
                                class="ph-bold ph-arrow-square-out transition-colors duration-150 group-hover:text-primary"
                            ></i>
                            <a
                                href="supplier/${supplier.id}"
                                class="font-medium cursor-pointer transition-colors duration-150 group-hover:text-primary"
                                >Detalhes</a
                            >
                        </div>
                    </div>
                    <div class="flex justify-end gap-2 ml-5 w-fit max-w-fit">
                        <div
                            class="flex items-center gap-2 bg-black bg-opacity-20 px-3 py-1 rounded-md w-fit h-fit"
                        >
                            <i class="ph-fill ph-path text-xl"></i>
                            <span class="font-medium translate-y-[1px] text-nowrap">${distanceFmt}</span>
                        </div>
                        <div
                            title="Média dos ultimos 3 IQFs existentes para esse fornecedor."
                            class="flex cursor-help items-center gap-2 bg-black bg-opacity-20 px-3 py-1 rounded-md w-fit h-fit text-green-300"
                            id="supplier-rating"
                        >
                            <i class="ph-fill ph-star text-xl"></i>
                            <span class="font-medium translate-y-[1px]">${ratingFmt}</span>
                        </div>
                    </div>
                </div>
                ${charcoalStats(supplier)}
                ${hasDocuments
            ? html`
                          <div class="mt-5 w-full">
                              <div class="bg-black bg-opacity-20 shadow-sm rounded-md overflow-hidden">
                                  <table class="w-full">
                                      <tbody>
                                          ${documentRows}
                                      </tbody>
                                  </table>
                              </div>
                          </div>
                      `
            : ""}
            </div>
        </div>
    `;
}
