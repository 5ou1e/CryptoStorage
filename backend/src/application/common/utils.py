def classify_block_relation(event_block: int, reference_block: int) -> str:
    if event_block < reference_block:
        return "before"
    elif event_block > reference_block:
        return "after"
    return "same"


def classify_token_trade_status(buy_status: str, sell_status: str):
    if (buy_status, sell_status) in [
        ("after", "after"),
        ("same", "after"),
        ("after", "same"),
    ]:
        status = "after"
    elif (buy_status, sell_status) in [
        ("same", "before"),
        ("before", "before"),
        ("before", "same"),
    ]:
        status = "before"
    elif (buy_status, sell_status) == (
        "same",
        "same",
    ):
        status = "same"
    else:
        # ("before", "after"),
        # ("after", "before"),
        status = "mixed"
    return status


def classify_related_wallet_status(
    statuses: set,
    intersected_tokens_count: int,
    total_token_count: int,
    before_count: int,
    after_count: int,
):
    color = None
    if statuses == {"same"}:
        status = "undetermined"
    elif statuses <= {"after", "same"}:
        status = "copied_by"
    elif statuses <= {"before", "same"}:
        status = "copying"
    else:
        status = "undetermined"  # если есть mixed

    if status == "undetermined":
        if total_token_count and intersected_tokens_count / total_token_count >= 0.4:
            return "similar", color
        if intersected_tokens_count >= 10:
            if before_count / intersected_tokens_count >= 0.75:
                return "copying", color
            if after_count / intersected_tokens_count >= 0.75:
                return "copied_by", color
    if status in ["copied_by", "copying"]:
        if total_token_count and intersected_tokens_count / total_token_count >= 0.4:
            status = "similar"
            color = "rgba(248, 113, 113, 0.1)"
    return status, color
