"""
Solution: Exercise 3 - Design an approval flow for a risky tool
"""

APPROVAL_THRESHOLD = 50.00


def classify_refund_request(order_id: str, amount: float) -> str:
    if amount <= APPROVAL_THRESHOLD:
        return "auto_approve"
    return "requires_approval"


class ApprovalQueue:
    def __init__(self) -> None:
        self._pending: list[dict] = []

    def submit(self, request: dict) -> None:
        self._pending.append(request)

    def list_pending(self) -> list[dict]:
        return list(self._pending)


def issue_refund(order_id: str, amount: float) -> str:
    """Pretend to actually issue a refund (executes immediately for
    auto-approved requests)."""
    return f"Refund of ${amount:.2f} issued for order {order_id}."


def handle_refund_tool_call(tool_input: dict, queue: ApprovalQueue) -> str:
    order_id = tool_input["order_id"]
    amount = tool_input["amount"]

    decision = classify_refund_request(order_id, amount)

    if decision == "auto_approve":
        return issue_refund(order_id, amount)

    queue.submit({"order_id": order_id, "amount": amount})
    return (
        f"Refund of ${amount:.2f} for order {order_id} exceeds the "
        f"${APPROVAL_THRESHOLD:.2f} auto-approval threshold and has been "
        f"queued for human approval. It has NOT been issued."
    )


def main() -> None:
    queue = ApprovalQueue()

    test_requests = [
        {"order_id": "ORD-1001", "amount": 19.99},
        {"order_id": "ORD-1002", "amount": 124.50},
    ]

    for req in test_requests:
        result = handle_refund_tool_call(req, queue)
        print(result)

    print("\nPending approvals:")
    for pending in queue.list_pending():
        print(f"  - {pending}")

    # Discussion:
    # - The $50 threshold encodes a business risk decision, not a technical
    #   one — it should be configurable and owned by whoever owns refund
    #   policy, not buried in agent code.
    # - The agent (and the model behind it) never gets the ability to
    #   directly call issue_refund() for high-value amounts — the *only*
    #   path for those amounts is the approval queue. This is the
    #   "privilege separation" principle from the module README applied
    #   concretely: the model can request, but cannot itself authorize,
    #   high-impact actions.


if __name__ == "__main__":
    main()
