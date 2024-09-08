# section_writer.py

from ..inference import GenerationStatistics

def generate_section(prompt: str, additional_instructions: str, model: str, groq_provider):
    stream = groq_provider.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert writer. Generate a long, comprehensive, structured chapter following the 5E Instructional Model (Engage, Explore, Explain, Elaborate, Evaluate). Only output the content.",
            },
            {
                "role": "user",
                "content": f"Generate a chapter using the following details and instructions:\n\n{prompt}\n\nAdditional Instructions: {additional_instructions}",
            },
        ],
        temperature=0.3,
        max_tokens=8000,
        top_p=1,
        stream=True,
        stop=None,
    )

    for chunk in stream:
        tokens = chunk.choices[0].delta.content
        if tokens:
            yield tokens
        if x_groq := chunk.x_groq:
            if not x_groq.usage:
                continue
            usage = x_groq.usage
            statistics_to_return = GenerationStatistics(
                input_time=usage.prompt_time,
                output_time=usage.completion_time,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                total_time=usage.total_time,
                model_name=model,
            )
            yield statistics_to_return