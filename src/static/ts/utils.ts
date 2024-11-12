export function formatCPFAndCNPJ(v: string) {
    if (v.length == 11) {
        // Formata o CPF no padrão XXX.XXX.XXX-XX
        return `${v.slice(0, 3)}.${v.slice(3, 6)}.${v.slice(6, 9)}-${v.slice(9, 11)}`;
    } else if (v.length == 14) {
        // Formata o CNPJ no padrão XX.XXX.XXX/0001-XX
        return `${v.slice(0, 2)}.${v.slice(2, 5)}.${v.slice(5, 8)}/${v.slice(8, 12)}-${v.slice(12, 14)}`;
    }

    return "CNPJ/CPF INVÁLIDO";
}
