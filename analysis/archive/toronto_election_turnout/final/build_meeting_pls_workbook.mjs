import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const repoRoot = new URL("../../../", import.meta.url).pathname.replace(/\/$/, "");
const inputPath = `${repoRoot}/data/toronto_election_turnout/final/meeting_pls/toronto_ct_meeting_pls.csv`;
const outputPath = `${repoRoot}/data/toronto_election_turnout/final/meeting_pls/toronto_ct_meeting_pls.xlsx`;
const previewPath = "/private/tmp/toronto_ct_meeting_pls_preview.png";

const csvText = await fs.readFile(inputPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Meeting PLS" });
const sheet = workbook.worksheets.getItem("Meeting PLS");
const used = sheet.getUsedRange();

sheet.freezePanes.freezeRows(1);
sheet.freezePanes.freezeColumns(4);
sheet.showGridLines = false;
used.format.font = { name: "Arial", size: 9 };
sheet.getRangeByIndexes(0, 0, 1, used.columnCount).format = {
  fill: "#1F4E78",
  font: { name: "Arial", size: 9, bold: true, color: "#FFFFFF" },
  wrapText: true,
  verticalAlignment: "center",
};
sheet.getRangeByIndexes(0, 0, 1, used.columnCount).format.rowHeight = 42;
sheet.getRangeByIndexes(0, 0, used.rowCount, 4).format.columnWidth = 16;
sheet.getRangeByIndexes(0, 4, used.rowCount, used.columnCount - 4).format.columnWidth = 14;

const info = workbook.worksheets.add("Read Me");
info.getRange("A1:B9").values = [
  ["Toronto CT Meeting PLS", ""],
  ["Purpose", "Self-contained census-tract handoff table"],
  ["Unit", "One row per 2021 Toronto analytical census tract (585 CTs)"],
  ["Join key", "ct_id (text)"],
  ["Inputs", "14 meeting-selected variables plus four turnout outcomes"],
  ["Latents", "PLS X-scores and within-model percentiles"],
  ["Model results", "Fitted values, residuals, and shuffled-CV predictions for the mean and three election levels"],
  ["Geometry", "Use the matching GeoJSON in the same folder"],
  ["Caution", "CT election outcomes are spatially allocated estimates; associations are ecological, not individual-level or causal"],
];
info.mergeCells("A1:B1");
info.getRange("A1:B1").format = {
  fill: "#1F4E78",
  font: { name: "Arial", size: 12, bold: true, color: "#FFFFFF" },
};
info.getRange("A2:A9").format.font = { name: "Arial", size: 10, bold: true, color: "#1F4E78" };
info.getRange("B2:B9").format.wrapText = true;
info.getRange("A:A").format.columnWidth = 20;
info.getRange("B:B").format.columnWidth = 85;
info.showGridLines = false;

const preview = await workbook.render({ sheetName: "Read Me", range: "A1:B9", scale: 1.5, format: "png" });
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
if (errors.ndjson.includes("#REF!") || errors.ndjson.includes("#DIV/0!") || errors.ndjson.includes("#VALUE!")) {
  throw new Error(errors.ndjson);
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
console.log(previewPath);
