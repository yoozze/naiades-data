/* eslint-disable import/prefer-default-export */

/**
 * Check if given string value is numeric.
 * @param value String value.
 * @returns `true` if `value` is numeric string, `false` otherwise.
 */
export function isNumeric(value: string): boolean {
    const number = parseFloat(value);
    return !Number.isNaN(number) && Number.isFinite(number);
}

/**
 * Generate random number on given interval.
 * If `min` > `max`, bounds are switched.
 * @param min Lower bound.
 * @param max Upper bound.
 * @returns Random integer between `min` and `max`.
 */
export function getRandomInt(min: number, max: number): number {
    return Math.floor(Math.random() * (Math.abs(max - min) + 1)) + Math.min(min, max);
}

/**
 * Generate random string of given length.
 * Characters are randpmly chosen from [A-Za-z0-9].
 * @param len Length of random string (absolute value).
 * @returns Random string of length `len`.
 */
export function getRandomString(len: number): string {
    const buf = [];
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for (let i = 0; i < Math.abs(len); i++) {
        buf.push(chars[getRandomInt(0, chars.length - 1)]);
    }

    return buf.join('');
}
