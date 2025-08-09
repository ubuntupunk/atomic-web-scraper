"""
Main application for the Atomic Scraper Tool.

Next-generation intelligent web scraping with AI-powered strategy generation
and natural language interface for effortless data extraction.
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

from .agents.scraper_planning_agent import AtomicScraperPlanningAgent, AtomicScraperAgentInputSchema
from .tools.atomic_scraper_tool import AtomicScraperTool, AtomicScraperInputSchema
from .config.scraper_config import AtomicScraperConfig


class AtomicScraperApp:
    """
    Main application class for the Atomic Scraper Tool.
    
    Next-generation intelligent web scraping application with AI-powered strategy
    generation and natural language interface for effortless data extraction.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the atomic scraper application.
        
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
        
        # Add sample session history for demonstration
        self._add_sample_history()
    
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
                "user_agent": "AtomicScraperTool/1.0",
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
            scraper_config = AtomicScraperConfig(**self.config["scraper"])
            self.scraper_tool = AtomicScraperTool(scraper_config)
            
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
# � Atomic Scraper Tool

Welcome to the next-generation intelligent web scraper! This AI-powered tool uses advanced 
natural language processing to understand your scraping requests and automatically generates 
optimal scraping strategies with dynamic schema recipes.

## Features:
- **Natural Language Interface**: Describe what you want to scrape in plain English
- **AI-Powered Strategy Generation**: Intelligent analysis of websites and content patterns
- **Dynamic Schema Recipes**: Automatically generated data structures for any website
- **Advanced Quality Scoring**: Multi-dimensional data quality assessment and filtering
- **Ethical Scraping**: Built-in compliance with robots.txt and respectful crawling
- **Rich Interactive Interface**: Beautiful formatted results with export options

Type your scraping requests naturally, like:
- "Scrape all farmers markets in Cape Town with their locations and hours"
- "Get product listings from this e-commerce site with prices and descriptions"
- "Extract article titles and dates from this news website"
        """
        
        panel = Panel(
            Markdown(welcome_text),
            title="�  Atomic Scraper Tool v1.0",
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
        agent_input = AtomicScraperAgentInputSchema(
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
                
                scraper_input = AtomicScraperInputSchema(
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
    
    def _mock_planning_agent_response(self, agent_input: AtomicScraperAgentInputSchema) -> Dict[str, Any]:
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
    
    def _add_sample_history(self):
        """Add sample session history for demonstration purposes."""
        from datetime import datetime, timedelta
        
        # Add some sample history entries
        sample_entries = [
            {
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "request": "Scrape product listings with prices and ratings",
                "url": "https://example-store.com/products",
                "planning_result": {"strategy": "list_scraping"},
                "scraping_summary": "Successfully scraped 25 product listings",
                "items_scraped": 25
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "request": "Extract news articles from homepage",
                "url": "https://news-site.com",
                "planning_result": {"strategy": "article_extraction"},
                "scraping_summary": "Extracted 12 news articles with metadata",
                "items_scraped": 12
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "request": "Get restaurant information with ratings",
                "url": "https://restaurant-directory.com/search",
                "planning_result": {"strategy": "directory_scraping"},
                "scraping_summary": "Found 8 restaurants with complete data",
                "items_scraped": 8
            }
        ]
        
        self.session_history.extend(sample_entries)
    
    def _show_session_history(self):
        """Display session history."""
        self.console.print("\n[bold green]📋 Session History[/bold green]")
        
        if not self.session_history:
            self.console.print("[yellow]No scraping requests in this session.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        history_table = Table(box=box.ROUNDED)
        history_table.add_column("#", style="dim", width=3)
        history_table.add_column("Time", style="cyan", width=20)
        history_table.add_column("Request", style="white", width=40)
        history_table.add_column("URL", style="blue", width=30)
        history_table.add_column("Items", style="green", width=8)
        
        for i, entry in enumerate(self.session_history, 1):
            timestamp = entry["timestamp"][:19].replace("T", " ")
            request = entry["request"][:37] + "..." if len(entry["request"]) > 40 else entry["request"]
            url = entry["url"][:27] + "..." if len(entry["url"]) > 30 else entry["url"]
            items = str(entry["items_scraped"])
            
            history_table.add_row(str(i), timestamp, request, url, items)
        
        self.console.print(history_table)
        
        # Show summary
        total_items = sum(entry["items_scraped"] for entry in self.session_history)
        self.console.print(f"\n[bold]Summary:[/bold] {len(self.session_history)} scraping operations, {total_items} total items scraped")
        
        # Ask if user wants to see details or export
        self.console.print("\n[bold cyan]Options:[/bold cyan]")
        self.console.print("1. View detailed entry")
        self.console.print("2. Export session history")
        self.console.print("3. Clear session history")
        self.console.print("4. Back to main menu")
        
        choice = Prompt.ask(
            "\n[cyan]Choose an option[/cyan]",
            choices=["1", "2", "3", "4"],
            default="4"
        )
        
        if choice == "1":
            self._view_history_details()
        elif choice == "2":
            self._export_session_history()
        elif choice == "3":
            self._clear_session_history()
        # choice == "4" returns to main menu
    
    def _view_history_details(self):
        """View detailed information about a specific history entry."""
        if not self.session_history:
            return
        
        entry_choices = [str(i) for i in range(1, len(self.session_history) + 1)] + ["cancel"]
        entry_num = Prompt.ask(
            f"[cyan]Which entry would you like to view? (1-{len(self.session_history)})[/cyan]",
            choices=entry_choices,
            default="cancel"
        )
        
        if entry_num == "cancel":
            return
        
        entry = self.session_history[int(entry_num) - 1]
        
        # Display detailed entry information
        detail_table = Table(title=f"Entry {entry_num} Details", box=box.ROUNDED)
        detail_table.add_column("Field", style="cyan", width=20)
        detail_table.add_column("Value", style="white")
        
        detail_table.add_row("Timestamp", entry["timestamp"])
        detail_table.add_row("Request", entry["request"])
        detail_table.add_row("URL", entry["url"])
        detail_table.add_row("Items Scraped", str(entry["items_scraped"]))
        detail_table.add_row("Summary", entry["scraping_summary"])
        
        self.console.print(detail_table)
        input("\nPress Enter to continue...")
    
    def _export_session_history(self):
        """Export session history to a file."""
        if not self.session_history:
            self.console.print("[yellow]No session history to export.[/yellow]")
            return
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_history_{timestamp}.json"
        
        try:
            import json
            with open(filename, 'w') as f:
                json.dump(self.session_history, f, indent=2, default=str)
            
            self.console.print(f"[green]✅ Session history exported to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Export failed: {e}[/red]")
        
        input("\nPress Enter to continue...")
    
    def _clear_session_history(self):
        """Clear the current session history."""
        if not self.session_history:
            self.console.print("[yellow]Session history is already empty.[/yellow]")
            return
        
        confirm = Confirm.ask(
            f"[red]Are you sure you want to clear {len(self.session_history)} history entries?[/red]",
            default=False
        )
        
        if confirm:
            self.session_history.clear()
            self.console.print("[green]✅ Session history cleared.[/green]")
        else:
            self.console.print("[yellow]Operation cancelled.[/yellow]")
        
        input("\nPress Enter to continue...")
    
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
        
        # Configuration management options
        self.console.print("\n[bold cyan]Configuration Management Options:[/bold cyan]")
        config_menu = Table(show_header=False, box=box.SIMPLE)
        config_menu.add_column("Option", style="cyan", width=3)
        config_menu.add_column("Description", style="white")
        
        config_menu.add_row("1", "🔧 Modify Scraper Settings")
        config_menu.add_row("2", "🧠 Manage Schema Recipes")
        config_menu.add_row("3", "📏 Set Quality Thresholds")
        config_menu.add_row("4", "💾 Save Configuration")
        config_menu.add_row("5", "🔄 Reset to Defaults")
        config_menu.add_row("6", "🔙 Back to Main Menu")
        
        self.console.print(config_menu)
        
        choice = Prompt.ask(
            "\n[bold cyan]Choose an option[/bold cyan]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="6"
        )
        
        if choice == "1":
            self._modify_scraper_settings()
        elif choice == "2":
            self._manage_schema_recipes()
        elif choice == "3":
            self._set_quality_thresholds()
        elif choice == "4":
            self._save_configuration()
        elif choice == "5":
            self._reset_to_defaults()
        # choice == "6" returns to main menu
    
    def _show_tool_information(self):
        """Display tool information and statistics."""
        self.console.print("\n[bold green]📊 Tool Information[/bold green]")
        
        try:
            # Get tool info
            if self.scraper_tool is None:
                self.console.print("[red]❌ Scraper tool not initialized[/red]")
                input("\nPress Enter to continue...")
                return
            
            tool_info = self.scraper_tool.get_tool_info()
            
            info_table = Table(title="Tool Information", box=box.ROUNDED)
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="white")
            
            info_table.add_row("Name", tool_info.get("name", "Atomic Scraper Tool"))
            info_table.add_row("Version", tool_info.get("version", "1.0.0"))
            info_table.add_row("Description", tool_info.get("description", "AI-powered web scraping tool"))
            
            self.console.print(info_table)
            
            # Configuration details
            config_table = Table(title="Current Configuration", box=box.SIMPLE)
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="white")
            
            config_data = tool_info.get("config", self.config.get("scraper", {}))
            for key, value in config_data.items():
                config_table.add_row(key.replace("_", " ").title(), str(value))
            
            self.console.print(config_table)
            
            # Supported features
            features_table = Table(title="Supported Features", box=box.SIMPLE)
            features_table.add_column("Feature", style="cyan")
            features_table.add_column("Options", style="white")
            
            strategies = tool_info.get("supported_strategies", ["list", "detail", "search", "sitemap"])
            extraction_types = tool_info.get("supported_extraction_types", ["text", "links", "images", "tables"])
            
            features_table.add_row("Strategies", ", ".join(strategies))
            features_table.add_row("Extraction Types", ", ".join(extraction_types))
            
            self.console.print(features_table)
            
            # Session statistics
            stats_table = Table(title="Session Statistics", box=box.SIMPLE)
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="white")
            
            total_requests = len(self.session_history)
            total_items = sum(entry["items_scraped"] for entry in self.session_history)
            
            stats_table.add_row("Total Requests", str(total_requests))
            stats_table.add_row("Total Items Scraped", str(total_items))
            stats_table.add_row("Debug Mode", "Enabled" if self.debug_mode else "Disabled")
            
            self.console.print(stats_table)
            
        except Exception as e:
            self.console.print(f"[red]❌ Error retrieving tool information: {e}[/red]")
            if self.debug_mode:
                self.console.print_exception()
        
        input("\nPress Enter to continue...")
    
    def _toggle_debug_mode(self):
        """Toggle debug mode on/off."""
        self.debug_mode = not self.debug_mode
        status = "enabled" if self.debug_mode else "disabled"
        color = "green" if self.debug_mode else "red"
        
        self.console.print(f"\n[{color}]🐛 Debug mode {status}[/{color}]")
        
        if self.debug_mode:
            self.console.print("\n[dim]Debug mode features:[/dim]")
            self.console.print("• Detailed error tracebacks")
            self.console.print("• Verbose logging output")
            self.console.print("• Additional diagnostic information")
            self.console.print("• Request/response details")
        else:
            self.console.print("\n[dim]Debug mode disabled - errors will show simplified messages[/dim]")
        
        input("\nPress Enter to continue...")
    
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
        self.console.print("\n[bold blue]👋 Thank you for using Atomic Scraper Tool![/bold blue]")
        
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
    
    def _modify_scraper_settings(self):
        """Modify scraper configuration settings."""
        self.console.print("\n[bold green]🔧 Modify Scraper Settings[/bold green]")
        
        settings_table = Table(show_header=False, box=box.SIMPLE)
        settings_table.add_column("Option", style="cyan", width=3)
        settings_table.add_column("Setting", style="white", width=25)
        settings_table.add_column("Current Value", style="yellow")
        
        scraper_config = self.config["scraper"]
        modifiable_settings = [
            ("1", "request_delay", "Request delay between pages (seconds)"),
            ("2", "timeout", "Request timeout (seconds)"),
            ("3", "max_pages", "Maximum pages to scrape"),
            ("4", "max_results", "Maximum results to return"),
            ("5", "min_quality_score", "Minimum quality score (0-100)"),
            ("6", "user_agent", "User agent string"),
            ("7", "respect_robots_txt", "Respect robots.txt (true/false)"),
            ("8", "enable_rate_limiting", "Enable rate limiting (true/false)")
        ]
        
        for option, key, description in modifiable_settings:
            current_value = str(scraper_config.get(key, "Not set"))
            settings_table.add_row(option, description, current_value)
        
        settings_table.add_row("9", "Back to Configuration Menu", "")
        
        self.console.print(settings_table)
        
        choice = Prompt.ask(
            "\n[cyan]Which setting would you like to modify?[/cyan]",
            choices=[str(i) for i in range(1, 10)],
            default="9"
        )
        
        if choice == "9":
            return
        
        # Get the setting to modify
        setting_key = modifiable_settings[int(choice) - 1][1]
        setting_desc = modifiable_settings[int(choice) - 1][2]
        current_value = scraper_config.get(setting_key)
        
        self.console.print(f"\n[bold]Modifying:[/bold] {setting_desc}")
        self.console.print(f"[dim]Current value: {current_value}[/dim]")
        
        # Get new value based on setting type
        if setting_key in ["respect_robots_txt", "enable_rate_limiting"]:
            new_value = Confirm.ask(f"[cyan]New value for {setting_key}[/cyan]", default=current_value)
        elif setting_key in ["request_delay", "timeout", "min_quality_score"]:
            new_value_str = Prompt.ask(f"[cyan]New value for {setting_key}[/cyan]", default=str(current_value))
            try:
                new_value = float(new_value_str)
            except ValueError:
                self.console.print("[red]Invalid numeric value.[/red]")
                return
        elif setting_key in ["max_pages", "max_results"]:
            new_value_str = Prompt.ask(f"[cyan]New value for {setting_key}[/cyan]", default=str(current_value))
            try:
                new_value = int(new_value_str)
            except ValueError:
                self.console.print("[red]Invalid integer value.[/red]")
                return
        else:  # String values like user_agent
            new_value = Prompt.ask(f"[cyan]New value for {setting_key}[/cyan]", default=str(current_value))
        
        # Update the configuration
        self.config["scraper"][setting_key] = new_value
        
        # Update the scraper tool configuration
        try:
            self.scraper_tool.update_config(**{setting_key: new_value})
            self.console.print(f"[green]✅ Updated {setting_key} to {new_value}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to update setting: {e}[/red]")
    
    def _manage_schema_recipes(self):
        """Manage schema recipes for different scraping scenarios."""
        self.console.print("\n[bold green]🧠 Manage Schema Recipes[/bold green]")
        
        # Initialize schema recipes storage if not exists
        if "schema_recipes" not in self.config:
            self.config["schema_recipes"] = {}
        
        recipes = self.config["schema_recipes"]
        
        if not recipes:
            self.console.print("[yellow]No schema recipes found.[/yellow]")
        else:
            # Display existing recipes
            recipes_table = Table(title="Saved Schema Recipes", box=box.ROUNDED)
            recipes_table.add_column("Name", style="cyan")
            recipes_table.add_column("Description", style="white")
            recipes_table.add_column("Fields", style="green")
            
            for name, recipe in recipes.items():
                field_count = len(recipe.get("fields", {}))
                description = recipe.get("description", "No description")
                recipes_table.add_row(name, description, str(field_count))
            
            self.console.print(recipes_table)
        
        # Schema management options
        schema_menu = Table(show_header=False, box=box.SIMPLE)
        schema_menu.add_column("Option", style="cyan", width=3)
        schema_menu.add_column("Description", style="white")
        
        schema_menu.add_row("1", "📝 Create New Schema Recipe")
        schema_menu.add_row("2", "👁️  View Schema Recipe Details")
        schema_menu.add_row("3", "🗑️  Delete Schema Recipe")
        schema_menu.add_row("4", "📋 Export Schema Recipe")
        schema_menu.add_row("5", "📥 Import Schema Recipe")
        schema_menu.add_row("6", "🔙 Back to Configuration Menu")
        
        self.console.print(schema_menu)
        
        choice = Prompt.ask(
            "\n[cyan]Choose an option[/cyan]",
            choices=["1", "2", "3", "4", "5", "6"],
            default="6"
        )
        
        if choice == "1":
            self._create_schema_recipe()
        elif choice == "2":
            self._view_schema_recipe()
        elif choice == "3":
            self._delete_schema_recipe()
        elif choice == "4":
            self._export_schema_recipe()
        elif choice == "5":
            self._import_schema_recipe()
        # choice == "6" returns to config menu
    
    def _set_quality_thresholds(self):
        """Set quality thresholds for different aspects of scraping."""
        self.console.print("\n[bold green]📏 Set Quality Thresholds[/bold green]")
        
        # Initialize quality thresholds if not exists
        if "quality_thresholds" not in self.config:
            self.config["quality_thresholds"] = {
                "minimum_completeness": 0.6,
                "minimum_accuracy": 0.8,
                "minimum_consistency": 0.5,
                "minimum_overall": 60.0
            }
        
        thresholds = self.config["quality_thresholds"]
        
        # Display current thresholds
        thresholds_table = Table(title="Current Quality Thresholds", box=box.ROUNDED)
        thresholds_table.add_column("Metric", style="cyan")
        thresholds_table.add_column("Current Value", style="white")
        thresholds_table.add_column("Description", style="dim")
        
        threshold_descriptions = {
            "minimum_completeness": "Minimum data completeness ratio (0.0-1.0)",
            "minimum_accuracy": "Minimum data accuracy ratio (0.0-1.0)",
            "minimum_consistency": "Minimum data consistency ratio (0.0-1.0)",
            "minimum_overall": "Minimum overall quality score (0-100)"
        }
        
        for key, value in thresholds.items():
            description = threshold_descriptions.get(key, "Quality threshold")
            thresholds_table.add_row(key.replace("_", " ").title(), str(value), description)
        
        self.console.print(thresholds_table)
        
        # Allow modification
        modify = Confirm.ask("\n[cyan]Modify quality thresholds?[/cyan]", default=False)
        if not modify:
            return
        
        for key, current_value in thresholds.items():
            description = threshold_descriptions.get(key, key)
            new_value_str = Prompt.ask(
                f"[cyan]{key.replace('_', ' ').title()}[/cyan] ({description})",
                default=str(current_value)
            )
            
            try:
                new_value = float(new_value_str)
                
                # Validate ranges
                if key == "minimum_overall":
                    if not 0 <= new_value <= 100:
                        self.console.print(f"[red]Overall quality score must be between 0 and 100[/red]")
                        continue
                else:
                    if not 0.0 <= new_value <= 1.0:
                        self.console.print(f"[red]Ratio values must be between 0.0 and 1.0[/red]")
                        continue
                
                thresholds[key] = new_value
                self.console.print(f"[green]✅ Updated {key} to {new_value}[/green]")
                
            except ValueError:
                self.console.print(f"[red]Invalid numeric value for {key}[/red]")
        
        # Update scraper tool quality thresholds
        try:
            self.scraper_tool.update_config(min_quality_score=thresholds["minimum_overall"])
            self.console.print("[green]✅ Quality thresholds updated successfully[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to update quality thresholds: {e}[/red]")
    
    def _save_configuration(self):
        """Save current configuration to file."""
        self.console.print("\n[bold green]💾 Save Configuration[/bold green]")
        
        if self.config_path:
            filename = self.config_path
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraper_config_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
            
            self.console.print(f"[green]✅ Configuration saved to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to save configuration: {e}[/red]")
    
    def _reset_to_defaults(self):
        """Reset configuration to default values."""
        self.console.print("\n[bold red]🔄 Reset to Defaults[/bold red]")
        
        confirm = Confirm.ask(
            "[yellow]This will reset ALL settings to defaults. Are you sure?[/yellow]",
            default=False
        )
        
        if not confirm:
            self.console.print("[cyan]Reset cancelled.[/cyan]")
            return
        
        # Reset to default configuration
        self.config = self._load_default_config()
        
        # Reinitialize components with new config
        try:
            scraper_config = WebsiteScraperConfig(**self.config["scraper"])
            self.scraper_tool = WebsiteScraperTool(scraper_config)
            self.console.print("[green]✅ Configuration reset to defaults[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to reset configuration: {e}[/red]")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration without user overrides."""
        return {
            "scraper": {
                "base_url": "https://example.com",
                "request_delay": 1.0,
                "timeout": 30,
                "max_pages": 5,
                "max_results": 50,
                "min_quality_score": 60.0,
                "user_agent": "AtomicScraperTool/1.0",
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
    
    def _create_schema_recipe(self):
        """Create a new schema recipe."""
        self.console.print("\n[bold green]📝 Create New Schema Recipe[/bold green]")
        
        name = Prompt.ask("[cyan]Recipe name[/cyan]")
        if not name.strip():
            self.console.print("[red]Recipe name cannot be empty.[/red]")
            return
        
        description = Prompt.ask("[cyan]Recipe description[/cyan]", default="Custom schema recipe")
        
        # Create basic recipe structure
        recipe = {
            "name": name,
            "description": description,
            "fields": {},
            "validation_rules": [],
            "quality_weights": {
                "completeness": 0.4,
                "accuracy": 0.4,
                "consistency": 0.2
            }
        }
        
        # Add fields
        self.console.print("\n[bold]Add fields to the schema:[/bold]")
        while True:
            field_name = Prompt.ask("[cyan]Field name (or 'done' to finish)[/cyan]")
            if field_name.lower() == 'done':
                break
            
            if not field_name.strip():
                continue
            
            field_type = Prompt.ask(
                "[cyan]Field type[/cyan]",
                choices=["string", "number", "array", "object", "boolean"],
                default="string"
            )
            
            field_desc = Prompt.ask(f"[cyan]Description for {field_name}[/cyan]", default=f"{field_name} field")
            selector = Prompt.ask(f"[cyan]CSS selector for {field_name}[/cyan]", default=f".{field_name}")
            required = Confirm.ask(f"[cyan]Is {field_name} required?[/cyan]", default=False)
            
            recipe["fields"][field_name] = {
                "field_type": field_type,
                "description": field_desc,
                "extraction_selector": selector,
                "required": required,
                "quality_weight": 1.0
            }
        
        if not recipe["fields"]:
            self.console.print("[yellow]No fields added. Recipe not saved.[/yellow]")
            return
        
        # Save recipe
        if "schema_recipes" not in self.config:
            self.config["schema_recipes"] = {}
        
        self.config["schema_recipes"][name] = recipe
        self.console.print(f"[green]✅ Schema recipe '{name}' created successfully[/green]")
    
    def _view_schema_recipe(self):
        """View details of a schema recipe."""
        if "schema_recipes" not in self.config or not self.config["schema_recipes"]:
            self.console.print("[yellow]No schema recipes found.[/yellow]")
            return
        
        recipes = list(self.config["schema_recipes"].keys())
        recipe_name = Prompt.ask(
            "[cyan]Which recipe would you like to view?[/cyan]",
            choices=recipes + ["cancel"],
            default="cancel"
        )
        
        if recipe_name == "cancel":
            return
        
        recipe = self.config["schema_recipes"][recipe_name]
        
        # Display recipe details
        self.console.print(f"\n[bold green]Schema Recipe: {recipe_name}[/bold green]")
        self.console.print(f"[dim]Description: {recipe.get('description', 'No description')}[/dim]\n")
        
        # Display fields
        fields_table = Table(title="Fields", box=box.ROUNDED)
        fields_table.add_column("Field Name", style="cyan")
        fields_table.add_column("Type", style="white")
        fields_table.add_column("Selector", style="yellow")
        fields_table.add_column("Required", style="green")
        
        for field_name, field_def in recipe.get("fields", {}).items():
            required = "Yes" if field_def.get("required", False) else "No"
            fields_table.add_row(
                field_name,
                field_def.get("field_type", "string"),
                field_def.get("extraction_selector", ""),
                required
            )
        
        self.console.print(fields_table)
    
    def _delete_schema_recipe(self):
        """Delete a schema recipe."""
        if "schema_recipes" not in self.config or not self.config["schema_recipes"]:
            self.console.print("[yellow]No schema recipes found.[/yellow]")
            return
        
        recipes = list(self.config["schema_recipes"].keys())
        recipe_name = Prompt.ask(
            "[cyan]Which recipe would you like to delete?[/cyan]",
            choices=recipes + ["cancel"],
            default="cancel"
        )
        
        if recipe_name == "cancel":
            return
        
        confirm = Confirm.ask(f"[red]Delete recipe '{recipe_name}'?[/red]", default=False)
        if confirm:
            del self.config["schema_recipes"][recipe_name]
            self.console.print(f"[green]✅ Recipe '{recipe_name}' deleted[/green]")
    
    def _export_schema_recipe(self):
        """Export a schema recipe to file."""
        if "schema_recipes" not in self.config or not self.config["schema_recipes"]:
            self.console.print("[yellow]No schema recipes found.[/yellow]")
            return
        
        recipes = list(self.config["schema_recipes"].keys())
        recipe_name = Prompt.ask(
            "[cyan]Which recipe would you like to export?[/cyan]",
            choices=recipes + ["cancel"],
            default="cancel"
        )
        
        if recipe_name == "cancel":
            return
        
        recipe = self.config["schema_recipes"][recipe_name]
        filename = f"schema_recipe_{recipe_name.replace(' ', '_')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(recipe, f, indent=2)
            self.console.print(f"[green]✅ Recipe exported to {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Export failed: {e}[/red]")
    
    def _import_schema_recipe(self):
        """Import a schema recipe from file."""
        filename = Prompt.ask("[cyan]Enter filename to import[/cyan]")
        
        try:
            with open(filename, 'r') as f:
                recipe = json.load(f)
            
            # Validate recipe structure
            if not isinstance(recipe, dict) or "name" not in recipe or "fields" not in recipe:
                self.console.print("[red]Invalid recipe format.[/red]")
                return
            
            if "schema_recipes" not in self.config:
                self.config["schema_recipes"] = {}
            
            recipe_name = recipe["name"]
            if recipe_name in self.config["schema_recipes"]:
                overwrite = Confirm.ask(f"[yellow]Recipe '{recipe_name}' already exists. Overwrite?[/yellow]", default=False)
                if not overwrite:
                    return
            
            self.config["schema_recipes"][recipe_name] = recipe
            self.console.print(f"[green]✅ Recipe '{recipe_name}' imported successfully[/green]")
            
        except FileNotFoundError:
            self.console.print(f"[red]File '{filename}' not found.[/red]")
        except json.JSONDecodeError:
            self.console.print(f"[red]Invalid JSON format in '{filename}'.[/red]")
        except Exception as e:
            self.console.print(f"[red]Import failed: {e}[/red]")


def main():
    """Main entry point for the application."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Atomic Scraper Tool - Intelligent web scraping with natural language")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    try:
        app = AtomicScraperApp(config_path=args.config)
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
    main()