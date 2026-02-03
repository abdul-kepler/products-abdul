"""
Retry Handler - Manages retry logic for sycophantic evaluations.

Responsibilities:
- Track retry attempts
- Apply exponential backoff
- Determine if retry should be attempted
"""

import time
from typing import Optional


class RetryHandler:
    """
    Handles retry logic for failed or sycophantic evaluations.
    """

    def __init__(
        self,
        max_retries: int = 2,
        backoff_factor: float = 1.5,
        initial_delay_ms: int = 500,
    ):
        """
        Initialize retry handler.

        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Multiplier for exponential backoff
            initial_delay_ms: Initial delay in milliseconds
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.initial_delay_ms = initial_delay_ms
        self.attempts = 0
        self.history = []

    def should_retry(self, meta_result: dict) -> bool:
        """
        Determine if a retry should be attempted.

        Args:
            meta_result: Result from MetaJudge

        Returns:
            True if retry should be attempted
        """
        # Check if we've exceeded max retries
        if self.attempts >= self.max_retries:
            return False

        # Check recommendation from meta-judge
        recommendation = meta_result.get("recommendation", "accept")
        is_sycophantic = meta_result.get("is_sycophantic", False)

        return recommendation == "retry" or is_sycophantic

    def record_attempt(
        self,
        result: dict,
        meta_result: dict,
        was_successful: bool
    ) -> None:
        """
        Record an evaluation attempt.

        Args:
            result: The judge result
            meta_result: The meta-judge result
            was_successful: Whether the attempt was accepted
        """
        self.attempts += 1
        self.history.append({
            "attempt": self.attempts,
            "result": result,
            "meta_result": meta_result,
            "was_successful": was_successful,
            "timestamp": time.time(),
        })

    def get_delay(self) -> float:
        """
        Get the delay before next retry in seconds.

        Returns:
            Delay in seconds
        """
        if self.attempts == 0:
            return 0

        delay_ms = self.initial_delay_ms * (self.backoff_factor ** (self.attempts - 1))
        return delay_ms / 1000.0

    def wait(self) -> None:
        """Wait for the appropriate delay before retry."""
        delay = self.get_delay()
        if delay > 0:
            time.sleep(delay)

    def reset(self) -> None:
        """Reset the retry handler for a new evaluation."""
        self.attempts = 0
        self.history = []

    def get_summary(self) -> dict:
        """
        Get a summary of retry attempts.

        Returns:
            Summary dict with attempts and history
        """
        return {
            "total_attempts": self.attempts,
            "max_retries": self.max_retries,
            "retries_remaining": max(0, self.max_retries - self.attempts),
            "history": self.history,
        }

    @property
    def retries_exhausted(self) -> bool:
        """Check if all retries have been used."""
        return self.attempts >= self.max_retries

    def get_best_result(self) -> Optional[dict]:
        """
        Get the best result from all attempts.

        The "best" result is the one with the highest overall score
        that wasn't flagged as sycophantic.

        Returns:
            Best result dict or None
        """
        valid_attempts = [
            h for h in self.history
            if h.get("was_successful") or not h.get("meta_result", {}).get("is_sycophantic")
        ]

        if not valid_attempts:
            # If all were sycophantic, return the last one
            if self.history:
                return self.history[-1].get("result")
            return None

        # Find the one with highest overall score
        best = max(
            valid_attempts,
            key=lambda h: h.get("result", {}).get("overall", 0)
        )
        return best.get("result")
