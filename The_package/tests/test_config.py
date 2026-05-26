"""
    This file contains the pytests for config
"""

from package_name.config.settings import get_settings
import package_name.config.functions as functions
import matplotlib.pyplot as plt

settings = get_settings()

class TestSettings:
    """
        This class contains the tests for config/settings.py
    """
    def test_repr(self):
        print(settings)

    def test_describe(self):
        print(settings.describe())

    def test_to_df(self):
        settings.to_df().to_csv("config.csv")


class TestConfigFuncs:
    """
        This class contains the tests for the config/functions.py
    """
    def test_Show_Poisson_distribution(self):
        """
            This test uses below variables to plot a Poisson distribution.
        """
        return
        show_radiusses = False
        lower_x = 0
        higher_x = 10000
        lower_y = 0
        higher_y = 10000
        radius = 250
        ncanidates = 30
        pts = functions.Poisson_distribution(lower_x, higher_x, lower_y, higher_y, radius=radius, ncanidates=ncanidates)

        # Written by Chat-gpt:

        # Basic validation
        if pts.ndim != 2 or pts.shape[1] != 2:
            raise ValueError("Expected output shape (n, 2)")

        fig, ax = plt.subplots()

        # --- Plot bounding box ---
        width = higher_x - lower_x
        height = higher_y - lower_y

        rect = plt.Rectangle( # type: ignore
            (lower_x, lower_y),
            width,
            height,
            fill=False
        )
        ax.add_patch(rect)

        # --- Plot pts ---
        ax.scatter(pts[:, 0], pts[:, 1])

        if show_radiusses:
            # --- Draw radius circles ---
            for x, y in pts:
                circle = plt.Circle( # type: ignore
                    (x, y),
                    radius,
                    fill=False,
                    alpha=0.3
                )
                ax.add_patch(circle)

        # --- Formatting ---
        ax.set_aspect("equal")
        ax.set_xlim(lower_x - radius, higher_x + radius)
        ax.set_ylim(lower_y - radius, higher_y + radius)

        ax.set_title("Poisson Disk Sampling Test")

        print(pts)

        plt.show()
