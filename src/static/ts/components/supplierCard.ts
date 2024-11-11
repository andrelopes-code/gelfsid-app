import { html } from "../constants";
import { Supplier } from "../types";

export function SupplierCard(supplier: Supplier, borderColor: string, ratingColor: string): string {
    const distanciaFmt =
        supplier.distancia_em_metros !== null ? `${supplier.distancia_em_metros / 1000} km` : "N/A";
    const licencaFmt = supplier.licenca || "Sem Licença";
    const cadastroTecnicoFederalFmt = supplier.cadastro_tecnico_federal || "Sem Cadastro Técnico Federal";
    const registroIefFmt = supplier.registro_ief || "Sem Registro IEF";

    return html`
        <div class="p-3 w-full text-slate-200" id="supplier-card-template">
            <div
                id="card"
                style="border-color: ${borderColor};"
                class="bg-dark-200 bg-opacity-60 shadow-lg hover:shadow-xl px-4 py-4 border-t-[3px] rounded-lg w-full fixtransition transition-transform hover:translate-x-1 duration-300"
            >
                <div class="flex justify-between text-md">
                    <div class="flex flex-col gap-1">
                        <p class="mb-3 font-medium text-2xl text-white text-wrap break-words tracking-wide">
                            <span class="field">${supplier.razao_social}</span>
                        </p>

                        <div class="flex items-center gap-4">
                            <i class="ph-map-pin ph-fill"></i>
                            <span class="font-medium"
                                >${supplier.cidade.nome} - ${supplier.estado.sigla}</span
                            >
                        </div>

                        <div class="flex items-center gap-4">
                            <i class="ph-fill ph-identification-card"></i>
                            <span class="font-medium">${supplier.cnpj}</span>
                        </div>

                        <div class="flex items-center gap-4">
                            <i class="ph-fill ph-package"></i>
                            <span class="font-medium">${supplier.tipo_material}</span>
                        </div>
                    </div>
                    <div class="flex justify-end gap-2 w-fit wf">
                        <div
                            class="flex items-center gap-2 bg-black bg-opacity-20 px-3 py-1 rounded-md w-fit h-full max-h-fit"
                        >
                            <i class="ph-fill ph-path text-xl"></i>
                            <span class="font-medium text-nowrap">${distanciaFmt}</span>
                        </div>
                        <div
                            class="flex items-center gap-2 bg-black bg-opacity-20 px-3 py-1 rounded-md w-fit h-full max-h-fit text-green-300"
                            id="supplier-rating"
                        >
                            <i class="ph-fill ph-star text-xl"></i>
                            <span class="font-medium">${supplier.avaliacao}</span>
                        </div>
                    </div>
                </div>
                <div class="mt-5 w-full">
                    <!-- Card Content -->
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
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}
