"""
Historical figure analysis and author generation module.

This package provides AI-powered tools for discovering, analyzing, and creating
author profiles based on historical and public figures' writing styles.
"""

from .figure_research import (
    FigureAnalysis,
    HistoricalFigure,
    HistoricalFigureResearcher,
    FigureVerification,
    display_analysis,
    display_figures,
    display_verification,
)

from .profile_generator import HistoricalProfileGenerator

from .dataset_generator import HistoricalDatasetGenerator

__all__ = [
    "HistoricalFigure",
    "FigureAnalysis", 
    "FigureVerification",
    "HistoricalFigureResearcher",
    "HistoricalProfileGenerator",
    "HistoricalDatasetGenerator",
    "display_figures",
    "display_analysis",
    "display_verification",
]