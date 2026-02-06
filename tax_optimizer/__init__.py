"""Core package for deterministic retirement tax optimization."""

from .model import HouseholdConfig, ProjectionConfig, optimize_plan, project_plan

__all__ = ["HouseholdConfig", "ProjectionConfig", "optimize_plan", "project_plan"]
