"""
Main application for the Website Scraper Tool.

Provides an interactive Rich console interface for natural language scraping requests.
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich import box

from atomic_agents.agents.base_agent import BaseAgentConfig
from atomic_agents.lib.components.agent_memory import AgentMemory

from .agents.scraper_planning_agent import ScraperPlanningAgent, ScraperAgentInputSchema
from .tools.website_scraper_tool import WebsiteScraperTool, WebsiteScraperInputSchema
from .config.scraper_config import WebsiteScraperConfig


class WebsiteScraperApp:
    """
    Main application class for the Website Scraper Tool.
    
    Provides an interactive Rich console interface that allows users to make
    natural language scraping requests and see formatted results.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the website scraper application.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.console = Console()
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        self.planning_agent = None
        self.scraper_tool = None
        self.session_history = []
        
        # Application state
        self.running = True
        self.debug_mode = False
        
        # Initialize components
        self._initialize_components()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load application configuration."""
        default_config = {
            "scraper": {
                "base_url": "https://example.com",
                "request_delay": 1.0,
                "timeout": 30,
                "max_pages": 5,
                "max_results": 50,
                "min_quality_score": 60.0,
                "user_agent": "WebsiteScraperTool/1.0",
                "respect_robots_txt": True,
                "enable_rate_limiting": True,
                "max_retries": 3,
                "retry_delay": 2.0
            },
            "agent": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "interface": {
                "show_reasoning": True,
                "show_confidence": True,
                "auto_execute": False,
                "save_results": True,
                "results_format": "json"
            }
        }
        
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    for section, settings in user_config.items():
                        if section in default_config:
                            default_config[section].update(settings)
                        else:
                            default_config[section] = settings
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load config from {self.config_path}: {e}[/yellow]")
        
        return default_config
    
    def _initialize_components(self):
        """Initialize the planning agent and scraper tool."""
        try:
            # Initialize scraper tool
            scraper_config = WebsiteScraperConfig(**self.config["scraper"])
            self.scraper_tool = WebsiteScraperTool(scraper_config)
            
            # Initialize planning agent (mock for demo - would need actual LLM client)
            # For demo purposes, we'll skip the planning agent initialization
            # In a real implementation, this would use a proper LLM client
            self.planning_agent = None
            
            self.console.print("[yellow]Note: Planning agent disabled for demo. Using mock responses.[/yellow]")
            
        except Exception as e:
            self.console.print(f"[red]Error initializing components: {e}[/red]")
            sys.exit(1)
    
    def run(self):
        """Run the main application loop."""
        self._show_welcome()
        
        while self.running:
            try:
                self._show_main_menu()
                choice = self._get_user_choice()
                self._handle_menu_choice(choice)
            except KeyboardInterrupt:
                self._handle_exit()
            except Exception as e:
                self.console.print(f"[red]Unexpected error: {e}[/red]")
                if self.debug_mode:
                    self.console.print_exception()
    
    def _show_welcome(self):
        """Display welcome message and application info."""
        welcome_text = """
# 🕷️ Website Scraper Tool

Welcome to the intelligent website scraper! This tool uses natural language processing 
to understand your scraping requests and automatically generates optimal scraping strategies.

## Features:
- **Natural Language Requests**: Describe what you want to scrape in plain English
- **Intelligent Strategy Generation**: AI-powered analysis of websites and content
- **Quality Scoring**: Automatic data quality assessment and filtering
- **Respectful Crawling**: Built-in rate limiting and robots.txt compliance
- **Rich Output**: Beautiful formatted results with export options

Type your scraping requests naturally, like:
- "Scrape all farmers markets in Cape Town with their locations and hours"
- "Get product listings from this e-commerce site with prices and descriptions"
- "Extract article titles and dates from this news website"
        """
        
        panel = Panel(
            Markdown(welcome_text),
            title="🕷️ Website Scraper Tool v1.0",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def _show_main_menu(self):
        """Display the main menu options."""
        menu_table = Table(show_header=False, box=box.SIMPLE)
        menu_table.add_column("Option", style="cyan", width=3)
        menu_table.add_column("Description", style="white")
        
        menu_table.add_row("1", "🔍 New Scraping Request")
        menu_table.add_row("2", "📋 View Session History")
        menu_table.add_row("3", "⚙️  Configuration Settings")
        menu_table.add_row("4", "📊 Tool Information")
        menu_table.add_row("5", "🐛 Toggle Debug Mode")
        menu_table.add_row("6", "❓ Help & Examples")
        menu_table.add_row("7", "🚪 Exit")
        
        panel = Panel(
            menu_table,
            title="Main Menu",
            border_style="green",
            padding=(0, 1)
        )
        
        self.console.print(panel)
    
    def _get_user_choice(self) -> str:
        """Get user menu choice."""
        return Prompt.ask(
            "\n[bold cyan]Choose an option[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "6", "7"],
            default="1"
        )
    
    def _handle_menu_choice(self, choice: str):
        """Handle user menu selection."""
        if choice == "1":
            self._handle_scraping_request()
        elif choice == "2":
            self._show_session_history()
        elif choice == "3":
            self._show_configuration_settings()
        elif choice == "4":
            self._show_tool_information()
        elif choice == "5":
            self._toggle_debug_mode()
        elif choice == "6":
            self._show_help_and_examples()
        elif choice == "7":
            self._handle_exit()
    
    def _handle_scraping_request(self):
        """Handle a new scraping request from the user."""
        self.console.print("\n[bold green]🔍 New Scraping Request[/bold green]")
        self.console.print("Describe what you want to scrape in natural language:")
        self.console.print("[dim]Example: 'Scrape farmers markets in Cape Town with locations and operating hours'[/dim]\n")
        
        # Get user request
        request = Prompt.ask("[cyan]Your request[/cyan]")
        if not request.strip():
            self.console.print("[yellow]Request cannot be empty.[/yellow]")
            return
        
        # Get target URL
        target_url = Prompt.ask("[cyan]Target website URL[/cyan]")
        if not target_url.strip():
            self.console.print("[yellow]URL cannot be empty.[/yellow]")
            return
        
        # Get optional parameters
        max_results = Prompt.ask(
            "[cyan]Maximum results[/cyan]", 
            default=str(self.config["scraper"]["max_results"])
        )
        
        quality_threshold = Prompt.ask(
            "[cyan]Quality threshold (0-100)[/cyan]", 
            default=str(self.config["scraper"]["min_quality_score"])
        )
        
        try:
            max_results = int(max_results)
            quality_threshold = float(quality_threshold)
        except ValueError:
            self.console.print("[red]Invalid numeric values provided.[/red]")
            return
        
        # Process the request
        self._process_scraping_request(request, target_url, max_results, quality_threshold)
    
    def _process_scraping_request(
        self, 
        request: str, 
        target_url: str, 
        max_results: int, 
        quality_threshold: float
    ):
        """Process a scraping request through the planning agent and scraper tool."""
        
        # Create input for planning agent
        agent_input = ScraperAgentInputSchema(
            request=request,
            target_url=target_url,
            max_results=max_results,
            quality_threshold=quality_threshold
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Step 1: Generate scraping plan
            task1 = progress.add_task("🧠 Analyzing request and generating strategy...", total=None)
            
            try:
                # Note: This would normally call the planning agent
                # For now, we'll create a mock response
                planning_result = self._mock_planning_agent_response(agent_input)
                progress.update(task1, completed=True)
                
                # Show planning results
                self._display_planning_results(planning_result)
                
                # Ask user if they want to proceed
                if not self.config["interface"]["auto_execute"]:
                    proceed = Confirm.ask("\n[cyan]Execute this scraping plan?[/cyan]", default=True)
                    if not proceed:
                        self.console.print("[yellow]Scraping cancelled.[/yellow]")
                        return
                
                # Step 2: Execute scraping
                task2 = progress.add_task("🕷️ Executing scraping operation...", total=None)
                
                scraper_input = WebsiteScraperInputSchema(
                    target_url=target_url,
                    strategy=planning_result["strategy"],
                    schema_recipe=planning_result["schema_recipe"],
                    max_results=max_results
                )
                
                scraping_result = self.scraper_tool.run(scraper_input)
                progress.update(task2, completed=True)
                
                # Display results
                self._display_scraping_results(scraping_result, request)
                
                # Save to session history
                self._save_to_history(request, target_url, planning_result, scraping_result)
                
            except Exception as e:
                progress.stop()
                self.console.print(f"[red]Error during scraping: {e}[/red]")
                if self.debug_mode:
                    self.console.print_exception()
    
    def _mock_planning_agent_response(self, agent_input: ScraperAgentInputSchema) -> Dict[str, Any]:
        """Mock planning agent response for demonstration."""
        # This would normally call self.planning_agent.run(agent_input)
        return {
            "scraping_plan": f"Plan to scrape {agent_input.request} from {agent_input.target_url}",
            "strategy": {
                "scrape_type": "list",
                "target_selectors": [".item", ".listing", "article"],
                "pagination_strategy": "next_link",
                "max_pages": 3,
                "request_delay": 1.0
            },
            "schema_recipe": {
                "name": "dynamic_schema",
                "description": f"Schema for: {agent_input.request}",
                "fields": {
                    "title": {
                        "field_type": "string",
                        "description": "Item title",
                        "extraction_selector": "h1, h2, .title",
                        "required": True
                    },
                    "description": {
                        "field_type": "string", 
                        "description": "Item description",
                        "extraction_selector": "p, .description",
                        "required": False
                    }
                }
            },
            "reasoning": "Selected list strategy based on request for multiple items...",
            "confidence": 0.85
        }
    
    def _display_planning_results(self, planning_result: Dict[str, Any]):
        """Display the planning agent results."""
        self.console.print("\n[bold green]📋 Generated Scraping Plan[/bold green]")
        
        # Show plan summary
        plan_panel = Panel(
            planning_result["scraping_plan"],
            title="Scraping Plan",
            border_style="blue"
        )
        self.console.print(plan_panel)
        
        # Show confidence if enabled
        if self.config["interface"]["show_confidence"]:
            confidence = planning_result["confidence"]
            confidence_color = "green" if confidence > 0.8 else "yellow" if confidence > 0.6 else "red"
            self.console.print(f"\n[bold]Confidence Score:[/bold] [{confidence_color}]{confidence:.1%}[/{confidence_color}]")
        
        # Show reasoning if enabled
        if self.config["interface"]["show_reasoning"]:
            reasoning_panel = Panel(
                Markdown(planning_result["reasoning"]),
                title="🧠 Agent Reasoning",
                border_style="cyan",
                expand=False
            )
            self.console.print(reasoning_panel)
        
        # Show strategy details
        strategy_table = Table(title="Strategy Configuration", box=box.ROUNDED)
        strategy_table.add_column("Parameter", style="cyan")
        strategy_table.add_column("Value", style="white")
        
        strategy = planning_result["strategy"]
        strategy_table.add_row("Scrape Type", strategy["scrape_type"])
        strategy_table.add_row("Target Selectors", ", ".join(strategy["target_selectors"]))
        strategy_table.add_row("Max Pages", str(strategy["max_pages"]))
        strategy_table.add_row("Request Delay", f"{strategy['request_delay']}s")
        
        self.console.print(strategy_table)
    
    def _display_scraping_results(self, scraping_result, original_request: str):
        """Display the scraping results."""
        self.console.print("\n[bold green]🎉 Scraping Results[/bold green]")
        
        # Summary panel
        summary_panel = Panel(
            scraping_result.summary,
            title="Summary",
            border_style="green"
        )
        self.console.print(summary_panel)
        
        # Quality metrics
        metrics = scraping_result.quality_metrics
        metrics_table = Table(title="Quality Metrics", box=box.SIMPLE)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="white")
        
        metrics_table.add_row("Average Quality Score", f"{metrics['average_quality_score']:.1f}%")
        metrics_table.add_row("Success Rate", f"{metrics['success_rate']:.1f}%")
        metrics_table.add_row("Items Found", str(int(metrics['total_items_found'])))
        metrics_table.add_row("Items Scraped", str(int(metrics['total_items_scraped'])))
        metrics_table.add_row("Execution Time", f"{metrics['execution_time']:.2f}s")
        
        self.console.print(metrics_table)
        
        # Show sample results
        results = scraping_result.results
        if results['items']:
            self._display_sample_items(results['items'][:3])  # Show first 3 items
            
            # Ask if user wants to see all results or export
            if len(results['items']) > 3:
                show_all = Confirm.ask(f"\n[cyan]Show all {len(results['items'])} results?[/cyan]", default=False)
                if show_all:
                    self._display_sample_items(results['items'])
            
            # Export options
            if self.config["interface"]["save_results"]:
                export = Confirm.ask("[cyan]Export results to file?[/cyan]", default=True)
                if export:
                    self._export_results(results, original_request)
    
    def _display_sample_items(self, items: list):
        """Display sample scraped items."""
        for i, item in enumerate(items, 1):
            item_table = Table(title=f"Item {i}", box=box.ROUNDED, show_header=False)
            item_table.add_column("Field", style="cyan", width=15)
            item_table.add_column("Value", style="white")
            
            for field, value in item['data'].items():
                # Truncate long values
                display_value = str(value)
                if len(display_value) > 100:
                    display_value = display_value[:97] + "..."
                item_table.add_row(field.title(), display_value)
            
            item_table.add_row("Quality Score", f"{item['quality_score']:.1f}%")
            self.console.print(item_table)
    
    def _export_results(self, results: Dict[str, Any], request: str):
        """Export results to file."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraping_results_{timestamp}.json"
        
        export_data = {
            "request": request,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.console.print(f"[green]✅ Results exported to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Export failed: {e}[/red]")
    
    def _save_to_history(self, request: str, url: str, planning_result: Dict, scraping_result):
        """Save request to session history."""
        from datetime import datetime
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "url": url,
            "planning_result": planning_result,
            "scraping_summary": scraping_result.summary,
            "items_scraped": scraping_result.results['total_scraped']
        }
        
        self.session_history.append(history_entry)
    
    def _show_session_history(self):
        """Display session history."""
        self.console.print("\n[bold green]📋 Session History[/bold green]")
        
        if not self.session_history:
            self.console.print("[yellow]No scraping requests in this session.[/yellow]")
            return
        
        history_table = Table(box=box.ROUNDED)
        history_table.add_column("Time", style="cyan", width=20)
        history_table.add_column("Request", style="white", width=40)
        history_table.add_column("URL", style="blue", width=30)
        history_table.add_column("Items", style="green", width=8)
        
        for entry in self.session_history:
            timestamp = entry["timestamp"][:19].replace("T", " ")
            request = entry["request"][:37] + "..." if len(entry["request"]) > 40 else entry["request"]
            url = entry["url"][:27] + "..." if len(entry["url"]) > 30 else entry["url"]
            items = str(entry["items_scraped"])
            
            history_table.add_row(timestamp, request, url, items)
        
        self.console.print(history_table)
    
    def _show_configuration_settings(self):
        """Display and allow modification of configuration settings."""
        self.console.print("\n[bold green]⚙️ Configuration Settings[/bold green]")
        
        # Display current settings
        for section, settings in self.config.items():
            section_table = Table(title=section.title(), box=box.SIMPLE)
            section_table.add_column("Setting", style="cyan")
            section_table.add_column("Value", style="white")
            
            for key, value in settings.items():
                section_table.add_row(key, str(value))
            
            self.console.print(section_table)
        
        # Option to modify settings
        modify = Confirm.ask("\n[cyan]Modify settings?[/cyan]", default=False)
        if modify:
            self.console.print("[yellow]Configuration modification not implemented in this demo.[/yellow]")
    
    def _show_tool_information(self):
        """Display tool information and statistics."""
        self.console.print("\n[bold green]📊 Tool Information[/bold green]")
        
        # Get tool info
        tool_info = self.scraper_tool.get_tool_info()
        
        info_table = Table(title="Tool Information", box=box.ROUNDED)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("Name", tool_info["name"])
        info_table.add_row("Version", tool_info["version"])
        info_table.add_row("Description", tool_info["description"])
        
        self.console.print(info_table)
        
        # Configuration details
        config_table = Table(title="Current Configuration", box=box.SIMPLE)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="white")
        
        for key, value in tool_info["config"].items():
            config_table.add_row(key.replace("_", " ").title(), str(value))
        
        self.console.print(config_table)
        
        # Supported features
        features_table = Table(title="Supported Features", box=box.SIMPLE)
        features_table.add_column("Feature", style="cyan")
        features_table.add_column("Options", style="white")
        
        features_table.add_row("Strategies", ", ".join(tool_info["supported_strategies"]))
        features_table.add_row("Extraction Types", ", ".join(tool_info["supported_extraction_types"]))
        
        self.console.print(features_table)
    
    def _toggle_debug_mode(self):
        """Toggle debug mode on/off."""
        self.debug_mode = not self.debug_mode
        status = "enabled" if self.debug_mode else "disabled"
        color = "green" if self.debug_mode else "red"
        self.console.print(f"\n[{color}]🐛 Debug mode {status}[/{color}]")
    
    def _show_help_and_examples(self):
        """Display help information and examples."""
        help_text = """
# 🆘 Help & Examples

## Natural Language Requests

The scraper understands natural language requests. Here are some examples:

### E-commerce Sites
- "Get all product listings with names, prices, and descriptions"
- "Scrape product reviews with ratings and review text"
- "Extract product categories and their item counts"

### News & Blogs
- "Scrape article titles, authors, and publication dates"
- "Get all blog posts from the last month with content"
- "Extract news headlines and summaries from the homepage"

### Business Directories
- "Get business listings with names, addresses, and phone numbers"
- "Scrape restaurant information including cuisine type and ratings"
- "Extract company profiles with contact details"

### Events & Markets
- "Find all farmers markets with locations and operating hours"
- "Get event listings with dates, venues, and descriptions"
- "Scrape conference schedules with session details"

## Tips for Better Results

1. **Be Specific**: Include the exact data fields you want
2. **Mention Structure**: Specify if you want lists, individual pages, or search results
3. **Set Limits**: Use phrases like "first 20 items" or "from this week"
4. **Quality Matters**: The tool automatically filters low-quality results

## URL Requirements

- Must be a valid HTTP/HTTPS URL
- Should be publicly accessible
- Respects robots.txt by default
- Rate limiting is automatically applied

## Quality Scoring

The tool automatically scores extracted data based on:
- **Completeness**: How many fields were successfully extracted
- **Accuracy**: Data format and validation checks
- **Consistency**: Uniformity across extracted items

Items below the quality threshold are filtered out automatically.
        """
        
        help_panel = Panel(
            Markdown(help_text),
            title="Help & Examples",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(help_panel)
    
    def _handle_exit(self):
        """Handle application exit."""
        self.console.print("\n[bold blue]👋 Thank you for using Website Scraper Tool![/bold blue]")
        
        if self.session_history:
            save_history = Confirm.ask("Save session history?", default=True)
            if save_history:
                self._save_session_history()
        
        self.running = False
    
    def _save_session_history(self):
        """Save session history to file."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_history_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.session_history, f, indent=2, default=str)
            
            self.console.print(f"[green]✅ Session history saved to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to save history: {e}[/red]")


def main():
    """Main entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Website Scraper Tool - Intelligent web scraping with natural language")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        app = WebsiteScraperApp(config_path=args.config)
        if args.debug:
            app.debug_mode = True
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()