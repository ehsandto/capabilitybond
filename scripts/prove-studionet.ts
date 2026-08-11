import { createAccount, createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";

const address = (process.env.CONTRACT_ADDRESS ??
  "0x892DB175b67ab8497E6969596ed3bfb4DEA708AB") as `0x${string}`;
const account = createAccount();
const client = createClient({ chain: studionet, account });

const profiles = [
  {
    id: `research-citations-${Date.now()}`,
    name: "Evidence-backed research",
    rubric: "The agent must answer the selected research question and cite retrievable public evidence supporting material claims.",
    vectors: [
      { id: "compare", prompt: "Compare two documented technical approaches and cite primary evidence.", criteria: "Accurate comparison with traceable primary sources.", minimum_citations: 2 },
      { id: "verify", prompt: "Verify a factual technical claim and explain limitations.", criteria: "The conclusion follows from retrieved evidence and states limitations.", minimum_citations: 2 },
    ],
  },
  {
    id: `incident-analysis-${Date.now()}`,
    name: "Incident evidence analysis",
    rubric: "The agent must distinguish observed evidence from inference and produce actionable conclusions.",
    vectors: [
      { id: "timeline", prompt: "Construct an evidence-backed incident timeline.", criteria: "Chronology is internally consistent and each material event is evidenced.", minimum_citations: 2 },
      { id: "root-cause", prompt: "Assess the most likely root cause and alternatives.", criteria: "Separates evidence from inference and evaluates alternatives.", minimum_citations: 2 },
    ],
  },
  {
    id: `policy-audit-${Date.now()}`,
    name: "Public policy audit",
    rubric: "The agent must evaluate a public policy requirement against authoritative sources without inventing obligations.",
    vectors: [
      { id: "applicability", prompt: "Determine whether a stated public rule applies to a scenario.", criteria: "Uses authoritative sources and identifies jurisdiction and effective date.", minimum_citations: 2 },
      { id: "requirements", prompt: "Extract the operative requirements and exceptions.", criteria: "Requirements and exceptions are accurately grounded in sources.", minimum_citations: 2 },
    ],
  },
];

const proofs: unknown[] = [];
for (const profile of profiles) {
  const hash = await client.writeContract({
    address,
    functionName: "register_profile",
    args: [profile.id, profile.name, profile.rubric, JSON.stringify(profile.vectors)],
    account,
    value: 0n,
  });
  console.log(`profile=${profile.id} transaction=${hash}`);
  const receipt = await client.waitForTransactionReceipt({
    hash: hash as never,
    status: TransactionStatus.FINALIZED,
    interval: 5000,
    retries: 180,
  }) as any;
  const votes = Object.values(receipt.consensus_data?.votes ?? {});
  const executions = (receipt.consensus_data?.leader_receipt ?? []).map((item: any) => ({
    result: item.execution_result,
    code: item.genvm_result?.error_code ?? null,
  }));
  const fatal = executions.filter((item: any) => item.result !== "SUCCESS" &&
    item.code !== "CONSENSUS_VALIDATOR_QUORUM_REACHED");
  if (receipt.result_name !== "MAJORITY_AGREE" || fatal.length > 0) {
    throw new Error(`Proof transaction failed: ${JSON.stringify({ hash, consensus: receipt.result_name, fatal })}`);
  }
  const stored = await client.readContract({
    address,
    functionName: "get_profile",
    args: [profile.id],
  });
  proofs.push({
    profileId: profile.id,
    transactionHash: hash,
    transactionExplorer: `https://explorer-studio.genlayer.com/tx/${hash}`,
    status: receipt.status_name,
    consensus: receipt.result_name,
    agree: votes.filter((vote) => vote === "agree").length,
    disagree: votes.filter((vote) => vote === "disagree").length,
    executions,
    stored,
  });
}

console.log(JSON.stringify({
  contractAddress: address,
  contractExplorer: `https://explorer-studio.genlayer.com/address/${address}`,
  proofCount: proofs.length,
  proofs,
}, null, 2));
