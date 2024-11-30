export function formatCPFAndCNPJ(v: string) {
    if (v.length == 11) {
        return `${v.slice(0, 3)}.${v.slice(3, 6)}.${v.slice(6, 9)}-${v.slice(9, 11)}`; // XXX.XXX.XXX-XX
    } else if (v.length == 14) {
        return `${v.slice(0, 2)}.${v.slice(2, 5)}.${v.slice(5, 8)}/${v.slice(8, 12)}-${v.slice(12, 14)}`; // XX.XXX.XXX/XXXX-XX
    }

    return "";
}

export function roundNumber(number: number, digits: number = 2): string {
    var multiple = Math.pow(10, digits);
    var roundedNum = Math.round(number * multiple) / multiple;
    return roundedNum.toFixed(digits);
}

export function getCityKey(stateCode: number, cityName: string): string {
    return `${stateCode}-${cityName}`;
}
