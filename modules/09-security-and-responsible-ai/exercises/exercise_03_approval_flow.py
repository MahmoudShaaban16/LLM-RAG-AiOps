"""
Exercise 3: Design an approval flow for a risky tool

TODO:
  1. Implement classify_refund_request(order_id, amount) -> str
       returns "auto_approve" if amount <= APPROVAL_THRESHOLD
       returns "requires_approval" otherwise
  2. Implement ApprovalQueue with submit(request) and list_pending()
  3. Implement handle_refund_tool_call(tool_input) that ties these together
  4. Test with at least 2 amounts: one under $50, one over.
"""

APPROVAL_THRESHOLD = 50.00


def classify_refund_request(order_id: str, amount: float) -> str:
    # TODO
    pass


class ApprovalQueue:
    def __init__(self) -> None:
        self._pending: list[dict] = []

    def submit(self, request: dict) -> None:
        # TODO: store the request
        pass

    def list_pending(self) -> list[dict]:
        # TODO: return pending requests
        pass


def issue_refund(order_id: str, amount: float) -> str:
    """Pretend to actually issue a refund (executes immediately for
    auto-approved requests)."""
    return f"Refund of ${amount:.2f} issued for order {order_id}."


def handle_refund_tool_call(tool_input: dict, queue: ApprovalQueue) -> str:
    """tool_input looks like {"order_id": "...", "amount": 12.50}"""
    # TODO:
    #   - classify the request
    #   - if auto_approve: call issue_refund() and return its result
    #   - if requires_approval: queue.submit(...) and return a message
    #     explaining the refund is pending approval
    pass


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


if __name__ == "__main__":
    main()
