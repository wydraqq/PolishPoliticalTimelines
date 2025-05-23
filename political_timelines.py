import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
from matplotlib.lines import Line2D
from typing import List, Tuple, Dict, Any


def year_month_to_date(year_month: float) -> datetime:
    """Convert a year.month float representation to a datetime object."""
    year = int(year_month)
    month = int(round((year_month - year) * 100))
    return datetime(year, month, 1)


COLOR_SCHEME = {
    "Lewica": "#fffacd",  # pastel yellow
    "Centroprawica": "#aed9e0",  # pastel blue
    "Prawica": "#f4cccc",  # light red
    "Brak": "#BBBBBB",  # gray
}

CONSISTENT_COLOR = "#A8E6CF"
INCONSISTENT_COLOR = "#FF0000"


class PoliticalTimelinePlotter:
    """Class to handle the plotting of political timelines with consistency analysis."""
    
    def __init__(self):
        self.figure, self.axes = plt.subplots(
            nrows=4,
            figsize=(16, 14),
            sharex=True,
            gridspec_kw={"hspace": 0.5},
        )
        self.figure.patch.set_facecolor("#FAFAFA")
        self.position_mapping = {"Prezydent": 0, "Premier": 1}
        self.bar_height = 0.5
        self.reference_date = datetime(2000, 1, 1)
        
    @staticmethod
    def _calculate_days_since_reference(date: datetime, reference: datetime) -> int:
        """Calculate days since reference date."""
        return (date - reference).days
    
    def _complement_periods(
        self, 
        periods: List[Tuple[float, float]], 
        start_date: datetime = None, 
        end_date: datetime = None
    ) -> List[Tuple[datetime, datetime]]:
        """Find the inverse of given periods (periods where there was no overlap)."""
        start_date = start_date or year_month_to_date(2000.01)
        end_date = end_date or year_month_to_date(2030.08)
        
        periods_dt = sorted(
            [(year_month_to_date(start), year_month_to_date(end)) for start, end in periods],
            key=lambda x: x[0]
        )
        
        complement = []
        current_start = start_date
        
        for period_start, period_end in periods_dt:
            if period_start > current_start:
                complement.append((current_start, period_start))
            if period_end > current_start:
                current_start = period_end
                
        if current_start < end_date:
            complement.append((current_start, end_date))
            
        return complement
    
    def _draw_periods(
        self, 
        ax: plt.Axes,
        periods: List[Tuple[datetime, datetime]], 
        color: str,
        label_duration: bool = True
    ) -> None:
        """Draw shaded periods on the timeline."""
        for start, end in periods:
            start_days = self._calculate_days_since_reference(start, self.reference_date)
            end_days = self._calculate_days_since_reference(end, self.reference_date)
            
            ax.axvspan(start_days, end_days, color=color, alpha=0.3)
            
            if label_duration:
                duration_years = (end.year - start.year) + (end.month - start.month)/12
                if duration_years > 1:
                    midpoint = start + (end - start)/2
                    ax.text(
                        self._calculate_days_since_reference(midpoint, self.reference_date), 
                        0.6, f"{duration_years:.1f} lat",
                        ha="center", 
                        va="bottom", 
                        fontsize=8, 
                        color="black", 
                        weight='bold', 
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="white"),
                        zorder=2,
                    )
    
    def _plot_timeline(
        self,
        ax: plt.Axes,
        timeline_data: List[Tuple[str, float, float, str, str]],
        consistent_periods: List[Tuple[float, float]],
        title: str,
        subtitle: str
    ) -> None:
        """Plot a single timeline with given data."""
        # Convert data to datetime objects
        converted_data = [
            (name, year_month_to_date(start), year_month_to_date(end), party, position)
            for name, start, end, party, position in timeline_data
        ]
        
        # Convert consistent periods to datetime
        consistent_periods_dt = [
            (year_month_to_date(start), year_month_to_date(end)) 
            for start, end in consistent_periods
        ]
        
        # Find inconsistent periods
        inconsistent_periods_dt = self._complement_periods(consistent_periods)
        
        # Draw the consistency background
        self._draw_periods(ax, inconsistent_periods_dt, INCONSISTENT_COLOR)
        self._draw_periods(ax, consistent_periods_dt, CONSISTENT_COLOR)
        
        # Plot each political term
        for name, start, end, party, position in converted_data:
            start_days = self._calculate_days_since_reference(start, self.reference_date)
            end_days = self._calculate_days_since_reference(end, self.reference_date)
            
            ax.barh(
                self.position_mapping[position],
                width=end_days - start_days,
                left=start_days,
                height=self.bar_height,
                color=COLOR_SCHEME[party],
                edgecolor="#666666",
            )
            
            # Use full name for President, initials for Prime Minister
            display_name = name if position == "Prezydent" else "".join([s[0] for s in name.split()])
            
            ax.text(
                start_days + (end_days - start_days) / 2,
                self.position_mapping[position],
                display_name,
                ha="center",
                va="center",
                fontsize=12,
                color="black",
                bbox=dict(
                    boxstyle="round,pad=0", 
                    facecolor=COLOR_SCHEME[party], 
                    edgecolor=COLOR_SCHEME[party]
                ),
                zorder=2,
            )
        
        # Configure axes
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["Prezydent", "Premier"], fontsize=12)
        ax.invert_yaxis()
        
        # Set x-axis limits and ticks
        ax.set_xlim(
            self._calculate_days_since_reference(datetime(2000, 1, 1), self.reference_date),
            self._calculate_days_since_reference(datetime(2032, 1, 1), self.reference_date)
        )
        
        ticks = [
            self._calculate_days_since_reference(datetime(year, 1, 1), self.reference_date)
            for year in range(2000, 2032, 2)
        ]
        ax.set_xticks(ticks)
        ax.set_xticklabels([str(year) for year in range(2000, 2032, 2)], fontsize=12)
        
        # Add election markers
        ax.axvline(
            self._calculate_days_since_reference(datetime(2025, 6, 1), self.reference_date),
            color="red", linestyle="--", linewidth=1.2, zorder=1
        )
        ax.axvline(
            self._calculate_days_since_reference(datetime(2027, 11, 1), self.reference_date),
            color="blue", linestyle="--", linewidth=1.2, zorder=1
        )
        
        # Styling
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.tick_params(axis="x", length=1)
        ax.tick_params(axis="y", length=5)
        ax.set_facecolor("#FAFAFA")
        ax.set_title(title, fontsize=12, weight="bold", pad=20)
        ax.text(
            0.5, 1.05, subtitle, 
            transform=ax.transAxes, 
            fontsize=10, 
            style='italic', 
            ha='center'
        )
    
    def _create_legend(self) -> None:
        """Create and position the figure legend."""
        legend_elements = [
            mpatches.Patch(facecolor="green", alpha=0.3, label="Okres zgodności"),
            mpatches.Patch(facecolor="red", alpha=0.3, label="Okres rozbieżności"),
            Line2D(
                [0], [0], color='red', linestyle='--', linewidth=1.5, 
                label='Wybory prezydenckie 2025'
            ),
            Line2D(
                [0], [0], color='blue', linestyle='--', linewidth=1.5, 
                label='Wybory parlamentarne 2027'
            )
        ]
        
        self.figure.legend(
            handles=legend_elements,
            loc='lower center',
            bbox_to_anchor=(0.5, 0.03),
            ncol=len(legend_elements),
            fontsize=12
        )
        
        # Add footer
        self.figure.text(
            0.99, 0.015, "@ks", 
            ha="right", 
            fontsize=9, 
            style="italic", 
            color="gray"
        )
    
    def plot_all_scenarios(self) -> None:
        """Plot all four political scenarios."""
        # Define scenario data (keeping original Polish names and terms)
        scenarios = [
            {
                "data": (
                    [
                        ("Aleksander Kwaśniewski", 2000.01, 2005.12, "Lewica", "Prezydent"),
                        ("Lech Kaczyński", 2005.12, 2010.08, "Prawica", "Prezydent"),
                        ("Bronisław Komorowski", 2010.08, 2015.08, "Centroprawica", "Prezydent"),
                        ("Andrzej Duda", 2015.08, 2025.08, "Prawica", "Prezydent"),
                        ("Rafał Trzaskowski", 2025.08, 2030.08, "Centroprawica", "Prezydent"),
                        ("?", 2030.08, 2031.11, "Brak", "Prezydent"),
                        
                        ("Jerzy Buzek", 2000.01, 2001.10, "Centroprawica", "Premier"),
                        ("Leszek Miller", 2001.10, 2004.05, "Lewica", "Premier"),
                        ("Marek Belka", 2004.05, 2005.10, "Lewica", "Premier"),
                        ("Kazimierz Marcinkiewicz", 2005.10, 2006.07, "Prawica", "Premier"),
                        ("Jarosław Kaczyński", 2006.07, 2007.11, "Prawica", "Premier"),
                        ("Donald Tusk", 2007.11, 2014.09, "Centroprawica", "Premier"),
                        ("Ewa Kopacz", 2014.09, 2015.11, "Centroprawica", "Premier"),
                        ("Beata Szydło", 2015.11, 2017.12, "Prawica", "Premier"),
                        ("Mateusz Morawiecki", 2017.12, 2023.12, "Prawica", "Premier"),
                        ("Donald Tusk", 2023.12, 2027.11, "Centroprawica", "Premier"),
                        ("?", 2027.11, 2031.11, "Centroprawica", "Premier"),
                    ],
                    [   
                        (2001.10, 2005.10), 
                        (2005.12, 2007.11), 
                        (2010.08, 2015.08), 
                        (2015.11, 2023.12),
                        (2025.08, 2030.08)
                    ],
                ),
                "title": "Prezydenci i Premierzy Polski (2000–2025) – Analiza Zgodności Politycznej i Przyszłe Scenariusze\n\nOpcja A:    R. Trzaskowski jako prezydent, rząd PO w kolejnych wyborach.",
                "subtitle": "(około 5 lat współpracy)"
            },
            {
                "data": (
                    [
                        ("Aleksander Kwaśniewski", 2000.01, 2005.12, "Lewica", "Prezydent"),
                        ("Lech Kaczyński", 2005.12, 2010.08, "Prawica", "Prezydent"),
                        ("Bronisław Komorowski", 2010.08, 2015.08, "Centroprawica", "Prezydent"),
                        ("Andrzej Duda", 2015.08, 2025.08, "Prawica", "Prezydent"),
                        ("Rafał Trzaskowski", 2025.08, 2030.08, "Centroprawica", "Prezydent"),
                        ("?", 2030.08, 2031.11, "Brak", "Prezydent"),
                        
                        ("Jerzy Buzek", 2000.01, 2001.10, "Centroprawica", "Premier"),
                        ("Leszek Miller", 2001.10, 2004.05, "Lewica", "Premier"),
                        ("Marek Belka", 2004.05, 2005.10, "Lewica", "Premier"),
                        ("Kazimierz Marcinkiewicz", 2005.10, 2006.07, "Prawica", "Premier"),
                        ("Jarosław Kaczyński", 2006.07, 2007.11, "Prawica", "Premier"),
                        ("Donald Tusk", 2007.11, 2014.09, "Centroprawica", "Premier"),
                        ("Ewa Kopacz", 2014.09, 2015.11, "Centroprawica", "Premier"),
                        ("Beata Szydło", 2015.11, 2017.12, "Prawica", "Premier"),
                        ("Mateusz Morawiecki", 2017.12, 2023.12, "Prawica", "Premier"),
                        ("Donald Tusk", 2023.12, 2027.11, "Centroprawica", "Premier"),
                        ("?", 2027.11, 2031.11, "Prawica", "Premier"),
                    ],
                    [   
                        (2001.10, 2005.10), 
                        (2005.12, 2007.11), 
                        (2010.08, 2015.08), 
                        (2015.11, 2023.12),
                        (2025.08, 2027.11)
                    ],
                ),
                "title": "Opcja B:   R. Trzaskowski jako prezydent, rząd PiS po kolejnych wyborach",
                "subtitle": "(około 2,2 lat współpracy)"
            },
            {
                "data": (
                    [
                        ("Aleksander Kwaśniewski", 2000.01, 2005.12, "Lewica", "Prezydent"),
                        ("Lech Kaczyński", 2005.12, 2010.08, "Prawica", "Prezydent"),
                        ("Bronisław Komorowski", 2010.08, 2015.08, "Centroprawica", "Prezydent"),
                        ("Andrzej Duda", 2015.08, 2025.08, "Prawica", "Prezydent"),
                        ("Karol Nawrocki", 2025.08, 2030.08, "Prawica", "Prezydent"),
                        ("?", 2030.08, 2031.11, "Brak", "Prezydent"),
                        
                        ("Jerzy Buzek", 2000.01, 2001.10, "Centroprawica", "Premier"),
                        ("Leszek Miller", 2001.10, 2004.05, "Lewica", "Premier"),
                        ("Marek Belka", 2004.05, 2005.10, "Lewica", "Premier"),
                        ("Kazimierz Marcinkiewicz", 2005.10, 2006.07, "Prawica", "Premier"),
                        ("Jarosław Kaczyński", 2006.07, 2007.11, "Prawica", "Premier"),
                        ("Donald Tusk", 2007.11, 2014.09, "Centroprawica", "Premier"),
                        ("Ewa Kopacz", 2014.09, 2015.11, "Centroprawica", "Premier"),
                        ("Beata Szydło", 2015.11, 2017.12, "Prawica", "Premier"),
                        ("Mateusz Morawiecki", 2017.12, 2023.12, "Prawica", "Premier"),
                        ("Donald Tusk", 2023.12, 2027.11, "Centroprawica", "Premier"),
                        ("?", 2027.11, 2031.11, "Centroprawica", "Premier"),
                    ],
                    [   
                        (2001.10, 2005.10), 
                        (2005.12, 2007.11), 
                        (2010.08, 2015.08), 
                        (2015.11, 2023.12)
                    ],
                ),
                "title": "Opcja C:   K. Nawrocki jako prezydent, rząd PO w kolejnych wyborach",
                "subtitle": "(około 6,7 lat rozbieżności)"
            },
            {
                "data": (
                    [
                        ("Aleksander Kwaśniewski", 2000.01, 2005.12, "Lewica", "Prezydent"),
                        ("Lech Kaczyński", 2005.12, 2010.08, "Prawica", "Prezydent"),
                        ("Bronisław Komorowski", 2010.08, 2015.08, "Centroprawica", "Prezydent"),
                        ("Andrzej Duda", 2015.08, 2025.08, "Prawica", "Prezydent"),
                        ("Karol Nawrocki", 2025.08, 2030.08, "Prawica", "Prezydent"),
                        ("?", 2030.08, 2031.11, "Brak", "Prezydent"),
                        
                        ("Jerzy Buzek", 2000.01, 2001.10, "Centroprawica", "Premier"),
                        ("Leszek Miller", 2001.10, 2004.05, "Lewica", "Premier"),
                        ("Marek Belka", 2004.05, 2005.10, "Lewica", "Premier"),
                        ("Kazimierz Marcinkiewicz", 2005.10, 2006.07, "Prawica", "Premier"),
                        ("Jarosław Kaczyński", 2006.07, 2007.11, "Prawica", "Premier"),
                        ("Donald Tusk", 2007.11, 2014.09, "Centroprawica", "Premier"),
                        ("Ewa Kopacz", 2014.09, 2015.11, "Centroprawica", "Premier"),
                        ("Beata Szydło", 2015.11, 2017.12, "Prawica", "Premier"),
                        ("Mateusz Morawiecki", 2017.12, 2023.12, "Prawica", "Premier"),
                        ("Donald Tusk", 2023.12, 2027.11, "Centroprawica", "Premier"),
                        ("?", 2027.11, 2031.11, "Prawica", "Premier"),
                    ],
                    [   
                        (2001.10, 2005.10), 
                        (2005.12, 2007.11), 
                        (2010.08, 2015.08), 
                        (2015.11, 2023.12),
                        (2027.11, 2030.08)
                    ],
                ),
                "title": "Opcja D:   K. Nawrocki jako prezydent, rząd PiS w kolejnych wyborach",
                "subtitle": "(około 2,2 lat rozbieżności, następnie 2,8 lat współpracy)"
            }
        ]
        
        # Plot each scenario
        for idx, scenario in enumerate(scenarios):
            self._plot_timeline(
                self.axes[idx],
                *scenario["data"],
                scenario["title"],
                scenario["subtitle"]
            )
        
        # Add legend and adjust layout
        self._create_legend()
        plt.subplots_adjust(bottom=0.1)
    
    def save_and_show(self, filename: str = "political_timelines.png", dpi: int = 300) -> None:
        """Save the figure and display it."""
        plt.savefig(filename, dpi=dpi, bbox_inches="tight")
        plt.show()


if __name__ == "__main__":
    plotter = PoliticalTimelinePlotter()
    plotter.plot_all_scenarios()
    plotter.save_and_show()