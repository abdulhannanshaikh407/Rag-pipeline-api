"""
LLM client for text generation supporting OpenAI and Anthropic.
"""
from typing import List, Dict, Any
import openai
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.logging import setup_logging
import structlog

logger = structlog.get_logger()


class LLMClient:
    """
    Unified LLM interface for text generation.
    Supports OpenAI and Anthropic providers.
    """

    def __init__(self):
        self.settings = get_settings()
        self._setup_clients()

    def _setup_clients(self):
        """Initialize the LLM client based on provider."""
        if self.settings.llm_provider == "openai":
            self.openai_client = openai.AsyncOpenAI(
                api_key=self.settings.openai_api_key,
                base_url=getattr(self.settings, 'openai_base_url', None)
            )
        elif self.settings.llm_provider == "anthropic":
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=self.settings.anthropic_api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.settings.llm_provider}")

    async def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate text from the LLM given a list of messages.
        Each message is a dict with 'role' and 'content'.
        Returns the generated text string.
        """
        if self.settings.llm_provider == "openai":
            return await self._generate_openai(messages)
        elif self.settings.llm_provider == "anthropic":
            return await self._generate_anthropic(messages)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.settings.llm_provider}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _generate_openai(self, messages: List[Dict[str, str]]) -> str:
        """Generate text using OpenAI API."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.settings.llm_model,
                messages=messages,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e))
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _generate_anthropic(self, messages: List[Dict[str, str]]) -> str:
        """Generate text using Anthropic API."""
        try:
            # Convert messages to Anthropic format
            system_messages = [m for m in messages if m["role"] == "system"]
            chat_messages = [m for m in messages if m["role"] in ["user", "assistant"]]

            system = system_messages[0]["content"] if system_messages else ""
            response = await self.anthropic_client.messages.create(
                model=self.settings.llm_model,
                system=system,
                messages=chat_messages,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error("Anthropic generation failed", error=str(e))
            raise

    async def generate_stream(self, messages: List[Dict[str, str]]):
        """Stream generated text from the LLM."""
        if self.settings.llm_provider == "openai":
            response = await self.openai_client.chat.completions.create(
                model=self.settings.llm_model,
                messages=messages,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                stream=True
            )
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        elif self.settings.llm_provider == "anthropic":
            system_messages = [m for m in messages if m["role"] == "system"]
            chat_messages = [m for m in messages if m["role"] in ["user", "assistant"]]
            system = system_messages[0]["content"] if system_messages else ""
            
            async with self.anthropic_client.messages.stream(
                model=self.settings.llm_model,
                system=system,
                messages=chat_messages,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            raise ValueError(f"Unsupported LLM provider: {self.settings.llm_provider}")