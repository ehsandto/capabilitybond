import fs from "node:fs";
import path from "node:path";
import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";

const account = createAccount();
const client = createClient({ chain: studionet, account });
const code = fs.readFileSync(path.resolve("contracts/CapabilityBond.py"), "utf8");
console.log(`deployer=${account.address}`);
const hash = await client.deployContract({ account, code, args: [] });
console.log(`deploymentTransaction=${hash}`);
const receipt = await client.waitForTransactionReceipt({
  hash: hash as never, status: TransactionStatus.FINALIZED, interval: 5000, retries: 180,
}) as Record<string, any>;
const address = receipt.data?.contract_address ?? receipt.txDataDecoded?.contractAddress;
const executions = (receipt.consensus_data?.leader_receipt ?? []).map((item: any) => item.execution_result);
if (!address || executions.some((value: string) => value !== "SUCCESS")) {
  throw new Error(`Deployment failed: ${JSON.stringify({ address, executions })}`);
}
console.log(JSON.stringify({
  contractAddress: address,
  deploymentTransaction: hash,
  status: receipt.status_name,
  consensus: receipt.result_name,
  executions,
  contractExplorer: `https://explorer-studio.genlayer.com/address/${address}`,
  transactionExplorer: `https://explorer-studio.genlayer.com/tx/${hash}`,
}, null, 2));
