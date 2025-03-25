# ------------------------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------------------------
# Custom exceptions for the Agent class
class AgentError(Exception):
    """Base exception class for Agent-related errors."""
    pass

class AgentInputGuardrailError(AgentError):
    """Raised when an input guardrail is triggered."""
    def __init__(self, message, guardrail_output):
        super().__init__(message)
        self.guardrail_output = guardrail_output

class AgentOutputGuardrailError(AgentError):
    """Raised when an output guardrail is triggered."""
    def __init__(self, message, guardrail_output):
        super().__init__(message)
        self.guardrail_output = guardrail_output

class AgentProcessingError(AgentError):
    """Raised when an unexpected error occurs during agent processing."""
    pass