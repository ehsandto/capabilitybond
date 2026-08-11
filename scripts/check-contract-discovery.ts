import fs from "node:fs";
import path from "node:path";

const contractFiles = fs.readdirSync("contracts").filter((name) => name.endsWith(".py")).sort();
if (JSON.stringify(contractFiles) !== JSON.stringify(["CapabilityBond.py"])) {
  throw new Error(`Expected exactly one deployable Python contract, found: ${contractFiles.join(", ")}`);
}

const directTests = fs.readdirSync(path.join("tests", "direct")).filter((name) => name.endsWith(".py"));
for (const name of directTests) {
  const source = fs.readFileSync(path.join("tests", "direct", name), "utf8");
  if (source.includes("exec(") || source.includes("CapabilityBond.py\").read_text")) {
    throw new Error(`Test must not dynamically execute contract source: ${name}`);
  }
}

console.log("contract discovery check passed: contracts/CapabilityBond.py is the sole deployable source");
