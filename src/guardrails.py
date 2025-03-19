from agents import (
    Runner,
    Agent,
    RunContextWrapper,
    GuardrailFunctionOutput,
    input_guardrail,
    output_guardrail,
    TResponseInputItem,
)
from schemas import MinLengthInputGuardrailOutput, ModerationInputGuardrailOutput, MessageOutput, RelevanceInputGuardrailOutput, OutputGuardrailOutput
from openai import AsyncOpenAI

### add this to env file later, or another file that holds constants
GPT_MODEL = "gpt-4o-mini-2024-07-18"
MOD_MODEL = "omni-moderation-2024-09-26"

###  change this later 
client = AsyncOpenAI()

# ------------------------------------------------------------------------------------------------
# Guardrail agents
# ------------------------------------------------------------------------------------------------

input_guardrail_agent = Agent( 
    name="Guardrail check",
    model=GPT_MODEL,
    instructions="Check if the user is asking you something that is not related to travelling.",
    output_type=RelevanceInputGuardrailOutput,
)


output_guardrail_agent = Agent( 
    name="Guardrail check",
    model=GPT_MODEL,
    instructions="Check if the output contains any non-English content.",
    output_type=OutputGuardrailOutput,
)


# ------------------------------------------------------------------------------------------------
# Guardrails
# ------------------------------------------------------------------------------------------------

@input_guardrail
async def relevance_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=result.final_output.is_irrelevant,
    )


@input_guardrail
async def min_length_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    user_messages = [message['content'] for message in input if message['role'] == 'user']
    latest_user_message = user_messages[-1]
    input_length = len(latest_user_message)
    if input_length < 10:
        return GuardrailFunctionOutput(
            output_info=MinLengthInputGuardrailOutput(is_too_short=True, error_message="Input is too short"),
            tripwire_triggered=True,
        )
    return GuardrailFunctionOutput(output_info=MinLengthInputGuardrailOutput(is_too_short=False, error_message="Input is long enough"), tripwire_triggered=False)


@input_guardrail
async def moderation_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    user_messages = [message['content'] for message in input if message['role'] == 'user']
    latest_user_message = user_messages[-1]

    response = await client.moderations.create(
        model=MOD_MODEL,
        input=latest_user_message,
    )

    flagged = response.results[0].flagged

    if flagged:
        return GuardrailFunctionOutput(
            output_info=ModerationInputGuardrailOutput(is_flagged=flagged, error_message="Input is flagged"),
            tripwire_triggered=flagged,
        )
    return GuardrailFunctionOutput(output_info=ModerationInputGuardrailOutput(is_flagged=flagged, error_message="Input is not flagged"), tripwire_triggered=flagged)


@output_guardrail
async def non_english_guardrail(  
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(output_guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_non_english,
    )

