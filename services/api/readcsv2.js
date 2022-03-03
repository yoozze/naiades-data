const fs = require('fs');
const readline = require('readline');
const csvParse = require('csv-parse/lib/sync');

(async () => {
	console.time(__filename);
        const lines = [];
	const filePath = './dump/braila_flow211306H360.csv';
        const fileStream = fs.createReadStream(filePath);
        const rl = readline.createInterface({
            input: fileStream,
            crlfDelay: Infinity,
        });
        const readLines = (line) => {
            lines.push(...csvParse(line));

            // if (lines.length > 1) {
            //     rl.off('line', readFirstLines).close();
            // }
        };

        rl.on('line', readLines);
        await once(rl, 'close');

        const [header, ...rows] = lines;

        if (rows.length > 0) {
            const row = rows[rows.length - 1];
            const dp = {};
            header.forEach((h, i) => {
                dp[h] = isNumeric(row[i]) ? parseFloat(row[i]) : row[i];
            });
            dataPoint = dp;
        }
	console.timeEnd(__filename);
})();
