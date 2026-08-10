# src/monitoring/pricing.py


MODEL_PRICING = {
    # Update these values according to the current provider pricing.
    "openai/gpt-oss-120b": {
        "input_per_million": 0.0,
        "output_per_million": 0.0,
    },

    "llama-3.1-8b-instant": {
        "input_per_million": 0.0,
        "output_per_million": 0.0,
    },
}


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:

    pricing = MODEL_PRICING.get(model)

    if not pricing:
        return 0.0

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input_per_million"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output_per_million"]

    return input_cost + output_cost