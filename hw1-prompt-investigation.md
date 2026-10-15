# HW1 Part C: refund policy citation investigation

## Requirement and test

SPEC.md RESP-1 requires a policy identifier for every claim derived from a policy document. The refund timing comes from `data/policies/cw-refunds.md`, policy ID `cw-refunds`: approved refunds return to the original payment method in 5 to 10 business days.

The student ran the CLI as support user 9501 with debug output enabled. The tested sequence was:

1. `Show me order 4127.`
2. `start a refund`
3. `$84.00 broken in delivery`

The original conversation also included later support requests. Each reported rerun began in a fresh CLI session after regenerating the database, restoring order 4127 to its original delivered, refund-eligible state. These are user-provided live transcripts, not simulated runs.

## Original prompt and observed response

Prompt version: `d108f6949e5e`.

```text
- Cite the policy id (for example cw-returns) for every policy claim.
```

The refund tool returned:

```json
{"ok":true,"status":"auto_approved","refund_id":575,"order_id":4127,"amount_usd":84.0,"note":"refund goes back to the original payment method in 5 to 10 business days"}
```

The agent's final response was:

> The refund of $84.00 for order 4127 has been successfully processed and is auto-approved. Here are the details:
>
> - **Refund ID:** 575
> - **Amount:** $84.00
> - **Reason:** Broken in delivery
>
> The refund will be credited back to your original payment method within 5 to 10 business days. If you have any more questions or need further assistance, feel free to ask!

No policy retrieval or policy citation appeared in the supplied refund turn.

## First revision

Prompt version: `3dc11427e8fc`.

The citation bullet was changed to:

```text
- Cite the policy id (for example cw-returns) for every policy claim,
  including refund timing stated in tool results. If the result provides
  no policy id, retrieve the relevant policy before making the claim.
```

The observed refund tool call was:

```json
{"name":"issue_refund","arguments":{"order_id":4127,"amount_usd":84.0,"reason":"broken in delivery"},"result":{"ok":true,"status":"auto_approved","refund_id":575,"order_id":4127,"amount_usd":84.0,"note":"refund goes back to the original payment method in 5 to 10 business days"}}
```

The agent's final response was:

> The refund of $84.00 for order 4127 has been successfully issued and auto-approved.
>
> - **Refund ID:** 575
> - **Refund Status:** The amount will be credited back to the original payment method within 5 to 10 business days.
>
> If you have any other questions or need further assistance, feel free to ask!

The agent again omitted both policy retrieval and the citation.

## Second revision

Prompt version: `003c48572a7d`.

The first revision was retained and this bullet was added:

```text
- Before stating refund processing times, retrieve cw-refunds using
  get_policy and cite [cw-refunds] alongside the timing claim.
  Do this even when issue_refund includes timing in its result.
```

The debug output again showed `issue_refund` with the same arguments and result as above, with no `get_policy` call. The final response was:

> The refund for order 4127 has been successfully initiated for the amount of $84.00 due to the item being broken in delivery.
>
> - **Refund ID:** 575
> - **Status:** Auto-approved
> - **Note:** The refund will be processed back to the original payment method within 5 to 10 business days.
>
> If you have any other questions or need further assistance, feel free to ask!

## Assessment and takeaway

The student explicitly assessed the first revised response as failing RESP-1 because it did not cite the policy. The second revised response visibly repeats the same omission; a separate student label for that run has not been recorded.

The refund operation succeeded. The observed problem concerns the model's response and tool choice, rather than an incorrect refund result. Both revisions were tested but unsuccessful in the supplied runs; neither is a verified fix.

Takeaway: the agent used the refund timing supplied by `issue_refund` without retrieving or citing its policy source. Clarifying the general citation instruction and adding an explicit retrieval instruction did not correct this behavior in these runs. Instructions alone did not reliably enforce the requirement in this case. Enforcing retrieval and validating citations in code could be a future investigation; it was not implemented or tested here. These observations do not establish a failure rate or prove that a prompt change can never work.

## Scope and remaining homework

This file closes the documented prompt experiment; it is not a complete HW1 submission or a ten-conversation `hw1-session.jsonl`. The original pasted transcript is preserved separately in `work/hw1/transcript-2026-10-15.txt` in the chat workspace. The two reruns above were transcribed from the user's messages. Additional-tool work, completion of required conversation coverage and records, and the student's video remain separate deliverables.
