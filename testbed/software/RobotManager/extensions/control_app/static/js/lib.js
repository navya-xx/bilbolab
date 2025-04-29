function formatNumber(num, totalLength, decimalPlaces) {
    const sign = num < 0 ? '-' : ' ';
    const absFixed = Math.abs(num).toFixed(decimalPlaces);
    const [intPart, fracPart] = absFixed.split('.');

    // totalLength includes everything: sign + intPart + '.' + fracPart
    // figure out how wide the intPart should be
    const intWidth = totalLength - 1 - 1 - decimalPlaces; // minus sign, dot, and fraction

    const paddedInt = intPart.padStart(intWidth, ' ');
    return sign + paddedInt + '.' + fracPart;
}


