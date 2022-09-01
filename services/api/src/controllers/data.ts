import fs from 'fs';
import path from 'path';
import { once } from 'events';
import readline from 'readline';
import { spawn } from 'child_process';

import { NextFunction, Request, Response } from 'express';

import { getRandomString, isNumeric } from '../utils/misc';

interface DataPoint {
    [attribute: string]: number | string | null;
}

function getDataFilePath(sensor: string): string {
    const fileName = `${sensor.replace(/-/g, '_')}.csv`;
    const filePath = path.resolve('dump', fileName);

    if (!fs.existsSync(filePath)) {
        return '';
    }

    return filePath;
}

function getTempDataFilePath(filePath: string): string {
    const tempFilePath = filePath
        .replace('/dump/', '/cache/')
        .replace(/\.([^.]+)$/, `.${getRandomString(32)}.$1`);
    return tempFilePath;
}

function getTimeStamp(line: string) {
    const i = line.indexOf(',');
    return Number(line.substring(0, i).trim());
}

function csvToJson(headerLine: string, dataLines: string[]) {
    const headerRow = headerLine.split(',');
    const series: DataPoint[] = [];

    dataLines.forEach((dataLine) => {
        const dataRow = dataLine.split(',');

        if (dataRow.length !== headerRow.length) {
            return;
        }

        const dataPoint: DataPoint = {};
        headerRow.forEach((h, i) => {
            dataPoint[h] = isNumeric(dataRow[i]) ? parseFloat(dataRow[i]) : dataRow[i];
        });
        series.push(dataPoint);
    });

    return series;
}

async function processData(
    inputFilePath: string,
    outputFilePath: string,
    interval: number
): Promise<boolean> {
    return new Promise((resolve, reject): void => {
        try {
            const cmd = 'python3';
            const args = [
                'scripts/run.py',
                `-i${inputFilePath}`,
                `-o${outputFilePath}`,
                `-d${interval}`,
            ];
            const python = spawn(cmd, args);
            python.on('exit', () => {
                resolve(true);
            });
        } catch (error) {
            reject(error);
        }
    });
}

async function readSeries(filePath: string, from?: number, to?: number) {
    const series: string[] = [];

    try {
        const fileStream = fs.createReadStream(filePath);
        const rl = readline.createInterface({
            input: fileStream,
            crlfDelay: Infinity,
        });

        let count = 0;
        let currentLine = '';
        const readLines = (line: string) => {
            if (count === 0) {
                series.push(line);
                count += 1;
                return;
            }

            const timeStamp = getTimeStamp(line);

            if (Number.isNaN(timeStamp)) {
                return;
            }

            if (!((from && timeStamp < from) || (to && timeStamp > to))) {
                series.push(line);
                count += 1;
            } else if (count > 1) {
                rl.off('line', readLines).close();
            }

            currentLine = line;
        };

        rl.on('line', readLines);
        await once(rl, 'close');

        if (from === -1 && to === -1) {
            series.push(currentLine);
        }
    } catch (error) {
        // Failed to read series.
    }

    if (series.length > 0) {
        // Fix time column header name.
        const headers = series[0].split(/\s*,\s*/);
        series[0] = ['time', ...headers.slice(1)].join(',');
    }

    return series;
}

function deleteTempFiles(filePath: string) {
    try {
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
        }

        const tempFilePath = `${filePath}.temp`;
        if (fs.existsSync(tempFilePath)) {
            fs.unlinkSync(tempFilePath);
        }
    } catch (error) {
        console.log(error);
    }
}

export async function getSeries(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
        const inputFilePath = getDataFilePath(req.params.sensor);
        if (!inputFilePath) {
            res.status(500).json({
                error: `Invalid sensor: ${req.params.sensor}`,
            });
            return;
        }

        // const interval = Math.abs(Number(req.query.interval) || 3600);
        const interval = Number(req.query.interval);
        let outputFilePath = '';

        if (interval && interval > 0) {
            console.log(
                `Processing data from sensor ${req.params.sensor} with interval ${interval}`
            );

            outputFilePath = getTempDataFilePath(inputFilePath);
            const success = await processData(inputFilePath, outputFilePath, interval);

            if (!success) {
                deleteTempFiles(outputFilePath);
                res.status(500).json({
                    error: 'Data preprocessing failed',
                });
                return;
            }
        }

        const lines = await readSeries(
            outputFilePath || inputFilePath,
            req.query.from ? new Date(`${req.query.from}`).getTime() / 1000 : undefined,
            req.query.to ? new Date(`${req.query.to}`).getTime() / 1000 : undefined
        );

        if (outputFilePath) {
            deleteTempFiles(outputFilePath);
        }

        if (req.query.format === 'csv') {
            res.header('Content-Type', 'text/csv');
            res.attachment('data.csv');
            res.status(200).send(lines.join('\r\n'));
            return;
        }

        const [header, ...data] = lines;
        const series = csvToJson(header, data);
        res.status(200).json({
            series,
        });
    } catch (error) {
        next(error);
    }
}

export async function getLastDataPoint(
    req: Request,
    res: Response,
    next: NextFunction
): Promise<void> {
    console.log(req.params);

    try {
        const filePath = getDataFilePath(req.params.sensor);
        if (!filePath) {
            res.status(500).json({
                error: `Invalid sensor: ${req.params.sensor}`,
            });
            return;
        }

        const lines = await readSeries(filePath, -1, -1);

        if (req.query.format === 'csv') {
            res.header('Content-Type', 'text/csv');
            res.attachment('data.csv');
            res.status(200).send(lines.join('\r\n'));
        }

        const [header, ...data] = lines;
        const series = csvToJson(header, data);
        res.status(200).json({
            series,
        });
    } catch (error) {
        next(error);
    }
}
