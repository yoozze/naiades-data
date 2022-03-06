import fs from 'fs';
import path from 'path';
import { once } from 'events';
import readline from 'readline';

import { NextFunction, Request, Response } from 'express';
import { Parser } from 'json2csv';
import csvParse from 'csv-parse/lib/sync';

import { isNumeric } from '../utils/misc';

interface DataPoint {
    [attribute: string]: number | string | null;
}

function getDataFilePath(sensor: string): string {
    console.log('sensor', sensor);
    const fileName = `${sensor.replace(/-/g, '_')}.csv`;
    const filePath = path.resolve('dump', fileName);
    console.log('fileName', fileName);
    console.log('filePath', filePath);

    if (!fs.existsSync(filePath)) {
        return '';
    }

    return filePath;
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

    return series;
}

export async function getSeries(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
        const filePath = getDataFilePath(req.params.sensor);
        if (!filePath) {
            res.status(500).json({
                error: `Invalid sensor: ${req.params.sensor}`,
            });
            return;
        }

        const lines = await readSeries(
            filePath,
            req.query.from ? new Date(`${req.query.from}`).getTime() / 1000 : undefined,
            req.query.to ? new Date(`${req.query.to}`).getTime() / 1000 : undefined
        );

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
