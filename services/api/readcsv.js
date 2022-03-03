const fs = require('fs');

const rs = fs.createReadStream('./dump/braila_flow211306H360.csv');
rs.setEncoding('utf-8'); /* return String and not Buffer */

let counter = 0;
function parseline(line, start) {
	const f0 = line.indexOf('\t', start || 0);
	const f1 = line.indexOf('\t', f0 + 1);
	const data1 = line.substring(f0 + 1, f1);
	if (data1 && data1.match(/^Paris$/g))
		counter++;
}

(async () => {
	console.time(__filename);
	let remainder = '';
	for await (const buf of rs) {
		let start = 0;
		let end;
		while ((end = buf.indexOf('\n', start)) !== -1) {
			if (start == 0 && remainder.length > 0) {
				parseline(remainder + buf);
				remainder = '';
			} else
				parseline(buf, start);
			start = end + 1;
		}
		remainder = buf.substring(start);
	}
	console.timeEnd(__filename);
})();

