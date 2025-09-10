"""
Unit tests for historical author CLI commands.
"""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from cli.commands.historical_author import (
    historical_app,
    create_historical_author_interactive,
)
from core.historical import (
    HistoricalFigure,
    FigureAnalysis,
    FigureVerification
)
from core.models import AuthorProfile, AuthorSource, StyleGuide


class TestHistoricalAuthorCLI:
    """Test historical author CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
        # Create test fixtures
        self.test_figure = HistoricalFigure(
            name="Mark Twain",
            time_period="1835-1910",
            writing_style="Satirical American vernacular",
            notable_works="Tom Sawyer, Huckleberry Finn",
            match_criteria="Famous American humorist"
        )
        
        self.test_verification = FigureVerification(
            figure_name="Mark Twain",
            status="VERIFIED",
            reason="Extensive documented works",
            available_sources="Books, letters, speeches",
            concerns="None",
            time_period="1835-1910",
            primary_medium="Books",
            writing_volume="Extensive"
        )
        
        self.test_analysis = FigureAnalysis(
            figure_name="Mark Twain",
            tone_analysis="Satirical and humorous",
            voice_perspective="First person narrative",
            formality_level="Casual to moderate",
            length_structure="Variable episodic",
            unique_characteristics="Vernacular speech patterns",
            topics_themes="American life, social critique",
            historical_context="19th century American frontier"
        )
    
    def test_create_command_help(self):
        """Test create command help output."""
        result = self.runner.invoke(historical_app, ["create", "--help"])
        
        assert result.exit_code == 0
        assert "Create a new author profile based on a historical figure" in result.output
        assert "--id" in result.output
        assert "--criteria" in result.output
        assert "--figure" in result.output
    
    def test_search_command_help(self):
        """Test search command help output."""
        result = self.runner.invoke(historical_app, ["search", "--help"])
        
        assert result.exit_code == 0
        assert "Search for historical figures based on criteria" in result.output
        assert "--refine" in result.output
    
    def test_analyze_command_help(self):
        """Test analyze command help output."""
        result = self.runner.invoke(historical_app, ["analyze", "--help"])
        
        assert result.exit_code == 0
        assert "Analyze a historical figure's writing style" in result.output
    
    @patch('cli.commands.historical_author.HistoricalFigureResearcher')
    def test_search_command_success(self, mock_researcher_class):
        """Test successful search command."""
        mock_researcher = Mock()
        mock_researcher.discover_figures.return_value = [self.test_figure]
        mock_researcher_class.return_value = mock_researcher
        
        result = self.runner.invoke(historical_app, ["search", "Famous American authors"])
        
        assert result.exit_code == 0
        mock_researcher.discover_figures.assert_called_once_with("Famous American authors")
    
    @patch('cli.commands.historical_author.HistoricalFigureResearcher')
    def test_search_command_with_refine(self, mock_researcher_class):
        """Test search command with refine option."""
        mock_researcher = Mock()
        mock_researcher.refine_search.return_value = [self.test_figure]
        mock_researcher_class.return_value = mock_researcher
        
        with patch('cli.commands.historical_author.Prompt') as mock_prompt:
            mock_prompt.ask.return_value = "Focus on 19th century"
            
            result = self.runner.invoke(historical_app, ["search", "--refine", "American authors"])
            
            assert result.exit_code == 0
            mock_researcher.refine_search.assert_called_once_with("American authors", "Focus on 19th century")
    
    @patch('cli.commands.historical_author.HistoricalFigureResearcher')
    def test_search_command_error(self, mock_researcher_class):
        """Test search command when researcher fails."""
        mock_researcher_class.side_effect = Exception("API Error")
        
        result = self.runner.invoke(historical_app, ["search", "test criteria"])
        
        assert result.exit_code == 1
    
    @patch('cli.commands.historical_author.HistoricalFigureResearcher')
    def test_analyze_command_success(self, mock_researcher_class):
        """Test successful analyze command."""
        mock_researcher = Mock()
        mock_researcher.verify_figure.return_value = self.test_verification
        mock_researcher.analyze_figure.return_value = self.test_analysis
        mock_researcher_class.return_value = mock_researcher
        
        with patch('cli.commands.historical_author.Confirm') as mock_confirm:
            mock_confirm.ask.return_value = True
            
            result = self.runner.invoke(historical_app, ["analyze", "Mark Twain"])
            
            assert result.exit_code == 0
            mock_researcher.verify_figure.assert_called_once_with("Mark Twain")
            mock_researcher.analyze_figure.assert_called_once_with("Mark Twain")
    
    @patch('cli.commands.historical_author.HistoricalFigureResearcher')
    def test_analyze_command_unverified_figure(self, mock_researcher_class):
        """Test analyze command with unverified figure."""
        mock_researcher = Mock()
        unverified = FigureVerification(
            figure_name="Fake Person",
            status="UNVERIFIED",
            reason="Fictional character",
            available_sources="None",
            concerns="Not a real person"
        )
        mock_researcher.verify_figure.return_value = unverified
        mock_researcher_class.return_value = mock_researcher
        
        result = self.runner.invoke(historical_app, ["analyze", "Fake Person"])
        
        assert result.exit_code == 1
        # Should not call analyze_figure for unverified figures
        mock_researcher.analyze_figure.assert_not_called()
    
    @patch('cli.commands.historical_author.HistoricalFigureResearcher')
    def test_analyze_command_verification_fails(self, mock_researcher_class):
        """Test analyze command when verification fails."""
        mock_researcher = Mock()
        mock_researcher.verify_figure.return_value = None
        mock_researcher_class.return_value = mock_researcher
        
        result = self.runner.invoke(historical_app, ["analyze", "Test Figure"])
        
        assert result.exit_code == 1
    
    def test_create_command_batch_mode_missing_params(self):
        """Test create command in batch mode with missing parameters."""
        result = self.runner.invoke(historical_app, ["create", "--batch"])
        
        assert result.exit_code == 1
        assert "Either --figure or --criteria must be provided" in result.output
    
    def test_create_command_batch_mode_missing_id(self):
        """Test create command in batch mode with missing ID."""
        result = self.runner.invoke(historical_app, ["create", "--batch", "--figure", "Mark Twain"])
        
        assert result.exit_code == 1
        assert "--id must be provided in batch mode" in result.output


class TestBasicCLIFunctionality:
    """Test basic CLI functionality without complex mocking."""
    
    def test_historical_module_imports(self):
        """Test that historical modules can be imported."""
        from core.historical import HistoricalFigure, FigureAnalysis, FigureVerification
        from cli.commands.historical_author import historical_app, create_historical_author_interactive
        
        # Basic smoke test - objects can be created
        figure = HistoricalFigure(
            name="Test Figure",
            time_period="Test Period", 
            writing_style="Test Style",
            notable_works="Test Works",
            match_criteria="Test Criteria"
        )
        
        assert figure.name == "Test Figure"
        assert historical_app is not None
        assert create_historical_author_interactive is not None