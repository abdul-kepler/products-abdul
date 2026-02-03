"""
Base Agent - Abstract base class for all multi-agent evaluation agents.

Provides:
- Unified OpenAI LLM client
- JSON response format enforcement
- Prompt building and response parsing
- Error handling and logging
"""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

import yaml
from openai import OpenAI
from dotenv import load_dotenv


class BaseAgent(ABC):
    """
    Abstract base class for all evaluation agents.

    Subclasses must implement:
    - build_prompt(): Construct the prompt for this agent
    - parse_response(): Parse and validate the LLM response
    """

    # Class-level config cache
    _config_cache: Optional[dict] = None
    _likert_cache: Optional[dict] = None

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        verbose: bool = False
    ):
        """
        Initialize the agent.

        Args:
            model: Override model (uses config default if None)
            temperature: Override temperature (uses config default if None)
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self._load_env()

        # Load configuration
        config = self._get_config()

        # Set model (priority: param > override > default)
        agent_name = self._get_agent_name()
        if model:
            self.model = model
        elif agent_name in config.get('models', {}).get('overrides', {}):
            self.model = config['models']['overrides'][agent_name]
        else:
            self.model = config.get('models', {}).get('default', 'gpt-4o-mini')

        # Set temperature
        if temperature is not None:
            self.temperature = temperature
        else:
            self.temperature = config.get('temperatures', {}).get(agent_name, 0.3)

        # Initialize OpenAI client
        self.client = OpenAI()

        if self.verbose:
            print(f"[{self.__class__.__name__}] Initialized with model={self.model}, temp={self.temperature}")

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        # Try multiple locations for .env
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / ".env",  # Project root
            Path.cwd() / ".env",
        ]

        for env_path in possible_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break

    @classmethod
    def _get_config(cls) -> dict:
        """Load and cache agent configuration."""
        if cls._config_cache is None:
            config_path = Path(__file__).parent.parent / "config" / "agent_config.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    cls._config_cache = yaml.safe_load(f)
            else:
                cls._config_cache = {}
        return cls._config_cache

    @classmethod
    def _get_likert_rubrics(cls) -> dict:
        """Load and cache Likert rubrics configuration."""
        if cls._likert_cache is None:
            rubrics_path = Path(__file__).parent.parent / "config" / "likert_rubrics.yaml"
            if rubrics_path.exists():
                with open(rubrics_path, 'r') as f:
                    cls._likert_cache = yaml.safe_load(f)
            else:
                cls._likert_cache = {}
        return cls._likert_cache

    def _get_agent_name(self) -> str:
        """Get the agent name for config lookup (e.g., 'critic', 'defender')."""
        class_name = self.__class__.__name__
        # Convert CamelCase to snake_case and remove 'Agent' suffix
        name = class_name.replace('Agent', '').replace('Judge', '_judge')
        # Handle special cases
        name_map = {
            'Critic': 'critic',
            'Defender': 'defender',
            'Input_Filter': 'input_filter',
            'InputFilter': 'input_filter',
            'Meta_judge': 'meta_judge',
            'MetaJudge': 'meta_judge',
            '_judge': 'judge',
        }
        return name_map.get(class_name.replace('Agent', ''), 'default')

    def _load_prompt_template(self, template_name: str) -> str:
        """Load a prompt template from the prompts directory."""
        prompt_path = Path(__file__).parent.parent / "prompts" / f"{template_name}.md"
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                return f.read()
        return ""

    @abstractmethod
    def build_prompt(self, **kwargs) -> str:
        """
        Build the prompt for this agent.

        Args:
            **kwargs: Agent-specific context data

        Returns:
            Complete prompt string
        """
        pass

    @abstractmethod
    def parse_response(self, response: dict) -> dict:
        """
        Parse and validate the LLM response.

        Args:
            response: Raw response from LLM

        Returns:
            Parsed and validated response dict
        """
        pass

    def execute(self, **kwargs) -> dict:
        """
        Execute the agent's task.

        Args:
            **kwargs: Context data passed to build_prompt()

        Returns:
            Parsed response from the agent
        """
        prompt = self.build_prompt(**kwargs)

        if self.verbose:
            print(f"[{self.__class__.__name__}] Executing with prompt length: {len(prompt)}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=self.temperature,
            )

            raw_content = response.choices[0].message.content

            if self.verbose:
                print(f"[{self.__class__.__name__}] Raw response: {raw_content[:200]}...")

            # Parse JSON response
            try:
                result = json.loads(raw_content)
            except json.JSONDecodeError as e:
                return {
                    "error": True,
                    "error_message": f"JSON parse error: {str(e)}",
                    "raw_response": raw_content,
                }

            # Validate and parse through subclass method
            parsed = self.parse_response(result)
            parsed["_meta"] = {
                "model": self.model,
                "temperature": self.temperature,
                "tokens": response.usage.total_tokens if response.usage else 0,
            }

            return parsed

        except Exception as e:
            return {
                "error": True,
                "error_message": str(e),
            }

    def _format_json(self, data: Any) -> str:
        """Format data as JSON string for prompt inclusion."""
        return json.dumps(data, indent=2, default=str)

    def _validate_required_fields(self, data: dict, required: list[str]) -> tuple[bool, list[str]]:
        """
        Validate that required fields are present in data.

        Returns:
            (is_valid, missing_fields)
        """
        missing = [f for f in required if f not in data or data[f] is None]
        return len(missing) == 0, missing


class AgentResponse:
    """Wrapper for agent responses with convenient access methods."""

    def __init__(self, data: dict):
        self.data = data
        self.error = data.get("error", False)
        self.error_message = data.get("error_message", "")

    def __getitem__(self, key: str) -> Any:
        return self.data.get(key)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def is_valid(self) -> bool:
        return not self.error

    def to_dict(self) -> dict:
        return self.data
