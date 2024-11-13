import { html } from "../constants";
import { Supplier } from "../types";
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

export function SupplierCard(supplier: Supplier, borderColor: string, ratingColor: string): string {
    const distanciaFmt =
        supplier.distancia_em_metros !== null
            ? `${Math.round((supplier.distancia_em_metros / 1000) * 10) / 10} km`
            : "N/A";

    const avaliacaoFmt = supplier.avaliacao || "N/A";
    const licencaFmt = supplier.licenca_ambiental?.documento || "N/A";
    const cadastroTecnicoFederalFmt = supplier.cadastro_tecnico_federal?.documento || "N/A";
    const registroIefFmt = supplier.registro_ief?.documento || "N/A";

    let ctfStatusColor = statusColor(supplier.cadastro_tecnico_federal?.status);
    let licencaStatusColor = statusColor(supplier.licenca_ambiental?.status);
    let registroIefStatusColor = statusColor(supplier.registro_ief?.status);

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
                            ${supplier.razao_social}
                        </p>
                        <div class="flex items-center w-full gap-4">
                            <i class="ph-map-pin ph-fill"></i>
                            <span class="font-medium"
                                >${supplier.cidade.nome} - ${supplier.estado.sigla}</span
                            >
                        </div>
                        <div class="flex items-center gap-4">
                            <i class="ph-fill ph-identification-card"></i>
                            <span class="font-medium">${formatCPFAndCNPJ(supplier.cpf_cnpj)}</span>
                        </div>

                        <div class="flex items-center gap-4">
                            <i class="ph-fill ph-package"></i>
                            <span class="font-medium">${supplier.tipo_material}</span>
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
                                <!-- Licença -->
                                <tr class="border-slate-800 border-b">
                                    <td class="px-4 py-3">
                                        <div class="flex items-center text-slate-400 gap-2">
                                            <i class="ph-fill ph-file-text"></i>
                                            <span class="font-medium text-sm">LICENÇA</span>
                                        </div>
                                    </td>
                                    <td class="text-right px-4 py-3">
                                        <span class="font-medium text-sm">${licencaFmt}</span>
                                    </td>
                                    <td class="text-right px-4 py-3 w-fit">
                                        <span class="font-medium ${licencaStatusColor} text-sm"
                                            >${(
                                                supplier.licenca_ambiental?.status || "AUSENTE"
                                            ).toUpperCase()}</span
                                        >
                                    </td>
                                </tr>

                                <!-- CTF -->
                                <tr class="border-slate-800 border-b">
                                    <td class="px-4 py-3">
                                        <div class="flex items-center text-slate-400 gap-2">
                                            <i class="ph-fill ph-file-text"></i>
                                            <span class="font-medium text-sm">CADASTRO TÉCNICO FEDERAL</span>
                                        </div>
                                    </td>
                                    <td class="text-right px-4 py-3">
                                        <span class="font-medium text-sm">${cadastroTecnicoFederalFmt}</span>
                                    </td>
                                    <td class="text-right px-4 py-3 w-fit">
                                        <span class="font-medium ${ctfStatusColor} text-sm"
                                            >${(
                                                supplier.cadastro_tecnico_federal?.status || "AUSENTE"
                                            ).toUpperCase()}</span
                                        >
                                    </td>
                                </tr>

                                <!-- IEF -->
                                <tr class="">
                                    <td class="px-4 py-3">
                                        <div class="flex items-center text-slate-400 gap-2">
                                            <i class="ph-fill ph-file-text"></i>
                                            <span class="font-medium text-sm">REGISTRO IEF</span>
                                        </div>
                                    </td>
                                    <td class="text-right px-4 py-3">
                                        <span class="font-medium text-sm">${registroIefFmt}</span>
                                    </td>
                                    <td class="text-right px-4 py-3 w-fit">
                                        <span class="font-medium ${registroIefStatusColor} text-sm"
                                            >${(
                                                supplier.registro_ief?.status || "AUSENTE"
                                            ).toUpperCase()}</span
                                        >
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}
