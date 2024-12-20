export function formatCPFAndCNPJ(v: string) {
    if (v.length == 11) {
        return `${v.slice(0, 3)}.${v.slice(3, 6)}.${v.slice(6, 9)}-${v.slice(9, 11)}`; // XXX.XXX.XXX-XX
    } else if (v.length == 14) {
        return `${v.slice(0, 2)}.${v.slice(2, 5)}.${v.slice(5, 8)}/${v.slice(8, 12)}-${v.slice(12, 14)}`; // XX.XXX.XXX/XXXX-XX
    }

    return "";
}

export function roundNumber(number: number, digits: number = 2) {
    var multiple = Math.pow(10, digits);
    var roundedNum = Math.round(number * multiple) / multiple;
    return roundedNum.toFixed(digits);
}

export function getCityKey(stateCode: number, cityName: string) {
    return `${stateCode}-${cityName}`;
}

export function getRandomPastelColor() {
    const pastelColors = [
        "#FFB3BA",
        "#FFDFBA",
        "#FFFFBA",
        "#BAFFC9",
        "#BAE1FF",
        "#E0BBE4",
        "#FFCCE6",
        "#D4A5A5",
        "#C9C9FF",
        "#B5EAD7",
    ];
    const randomIndex = Math.floor(Math.random() * pastelColors.length);
    return pastelColors[randomIndex];
}
