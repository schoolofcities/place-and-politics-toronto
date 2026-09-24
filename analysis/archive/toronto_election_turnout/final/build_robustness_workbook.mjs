import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const repoRoot = new URL("../../../", import.meta.url).pathname.replace(/\/$/, "");
const releaseRoot = `${repoRoot}/data/toronto_election_turnout/final/robustness_checks`;
const resultCsv = await fs.readFile(`${releaseRoot}/toronto_ct_meeting_robustness_spatial_cv.csv`, "utf8");
const validationCsv = await fs.readFile(`${releaseRoot}/robustness_validation_summary.csv`, "utf8");
const pcaSummaryCsv = await fs.readFile(`${releaseRoot}/supervised_pca_model_summary.csv`, "utf8");
const pcaLoadingsCsv = await fs.readFile(`${releaseRoot}/supervised_pca_loadings.csv`, "utf8");
const elasticSummaryCsv = await fs.readFile(`${releaseRoot}/elastic_net_model_summary.csv`, "utf8");
const elasticCoefficientsCsv = await fs.readFile(`${releaseRoot}/elastic_net_coefficients.csv`, "utf8");

const workbook = await Workbook.fromCSV(resultCsv, { sheetName: "CT Spatial CV" });
await workbook.fromCSV(validationCsv, { sheetName: "Validation Summary" });
await workbook.fromCSV(pcaSummaryCsv, { sheetName: "PCA Summary" });
await workbook.fromCSV(pcaLoadingsCsv, { sheetName: "PCA Loadings" });
await workbook.fromCSV(elasticSummaryCsv, { sheetName: "Elastic Net Summary" });
await workbook.fromCSV(elasticCoefficientsCsv, { sheetName: "Elastic Coefficients" });

const readme = workbook.worksheets.add("Read Me");
readme.getRange("A1:B8").values = [
  ["Meeting-Variable Robustness Checks", ""],
  ["Purpose", "Compare supervised PCA and elastic net against the primary meeting PLS"],
  ["Unit", "CT Spatial CV is one row per 2021 Toronto analytical census tract (585 CTs)"],
  ["Join key", "ct_id (text)"],
  ["Outcomes", "Mean, municipal, provincial, and federal citizen-18+ participation"],
  ["Validation", "Saved shuffled-CV summaries and saved spatially blocked nested-CV results"],
  ["Geometry", "Map-ready GeoJSON is provided beside this workbook"],
  ["Caution", "Ecological predictive checks; not individual-level or causal estimates"],
];
readme.mergeCells("A1:B1");
readme.getRange("A1:B1").format = {
  fill: "#1F4E78",
  font: { name: "Arial", size: 12, bold: true, color: "#FFFFFF" },
};
readme.getRange("A2:A8").format.font = { name: "Arial", size: 10, bold: true, color: "#1F4E78" };
readme.getRange("B2:B8").format.wrapText = true;
readme.getRange("A1:A8").format.columnWidth = 22;
readme.getRange("B1:B8").format.columnWidth = 84;
readme.showGridLines = false;

for (const sheetName of [
  "CT Spatial CV",
  "Validation Summary",
  "PCA Summary",
  "PCA Loadings",
  "Elastic Net Summary",
  "Elastic Coefficients",
]) {
  const sheet = workbook.worksheets.getItem(sheetName);
  const used = sheet.getUsedRange();
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(sheetName === "CT Spatial CV" ? 4 : 1);
  sheet.showGridLines = false;
  used.format.font = { name: "Arial", size: 9 };
  sheet.getRangeByIndexes(0, 0, 1, used.columnCount).format = {
    fill: "#1F4E78",
    font: { name: "Arial", size: 9, bold: true, color: "#FFFFFF" },
    wrapText: true,
    verticalAlignment: "center",
  };
  sheet.getRangeByIndexes(0, 0, 1, used.columnCount).format.rowHeight = 60;
  sheet.getRangeByIndexes(0, 0, used.rowCount, used.columnCount).format.columnWidth = 15;
  const headers = sheet.getRangeByIndexes(0, 0, 1, used.columnCount).values[0];
  headers.forEach((headerValue, columnIndex) => {
    const header = String(headerValue ?? "");
    let width = 15;
    if (header === "model_id") width = 25;
    else if (header === "outcome") width = 38;
    else if (header === "method") width = 18;
    else if (header === "term" || header === "variable") width = 36;
    else if (header === "source_file" || header.endsWith("_source_file")) width = 110;
    else if (header === "sign_convention") width = 52;
    else if (header === "dguid") width = 27;
    else if (header.includes("prediction") || header.includes("residual")) width = 20;
    sheet.getRangeByIndexes(0, columnIndex, used.rowCount, 1).format.columnWidth = width;
  });
}

const tableCheck = await workbook.inspect({
  kind: "table",
  sheetId: "Validation Summary",
  range: "A1:I9",
  include: "values,formulas",
  tableMaxRows: 9,
  tableMaxCols: 9,
  maxChars: 5000,
});
console.log(tableCheck.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
if (errors.ndjson.includes("#REF!") || errors.ndjson.includes("#DIV/0!") || errors.ndjson.includes("#VALUE!")) {
  throw new Error(errors.ndjson);
}

const preview = await workbook.render({ sheetName: "Read Me", range: "A1:B8", scale: 1.5, format: "png" });
await fs.writeFile("/private/tmp/toronto_ct_robustness_preview.png", new Uint8Array(await preview.arrayBuffer()));
for (const [sheetName, range, slug] of [
  ["CT Spatial CV", "A1:AA10", "ct"],
  ["Validation Summary", "A1:L9", "validation"],
  ["PCA Summary", "A1:J5", "pca_summary"],
  ["PCA Loadings", "A1:H18", "pca_loadings"],
  ["Elastic Net Summary", "A1:I5", "elastic_summary"],
  ["Elastic Coefficients", "A1:G18", "elastic_coefficients"],
]) {
  const sheetPreview = await workbook.render({ sheetName, range, scale: 0.8, format: "png" });
  await fs.writeFile(
    `/private/tmp/toronto_ct_robustness_${slug}.png`,
    new Uint8Array(await sheetPreview.arrayBuffer()),
  );
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${releaseRoot}/toronto_ct_meeting_robustness_spatial_cv.xlsx`);
console.log(`${releaseRoot}/toronto_ct_meeting_robustness_spatial_cv.xlsx`);
