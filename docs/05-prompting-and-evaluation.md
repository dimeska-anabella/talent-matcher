# Prompting and Evaluation

## Prompting Guidance

For explanation generation, keep prompts constrained:

- Ask for 1-2 sentences.
- Ask for concrete reasons (skills, experience, role fit).
- Avoid speculative or biased claims.

## Simple Evaluation Checklist

Use 5-10 job descriptions and check:

- Do top 3 candidates make sense to a human reviewer?
- Is at least one strong candidate in top 3?
- Are explanations specific and understandable?
- Are scores stable across repeated calls?

## Error/Fallback Behavior

- If LLM call fails, return template explanation.
- If vector index is empty, prompt user to run ingestion.
- If job text is too short, reject with validation error.
