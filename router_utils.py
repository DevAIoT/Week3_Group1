"""
Router Utilities for Smart Three-Tier Routing
Provides image complexity calculation and routing decision logic
"""

import numpy as np


class ImageComplexityRouter:
    """
    Router that makes routing decisions based on image complexity (pixel variance)
    """

    def __init__(self, threshold):
        """
        Initialize router with complexity threshold

        Args:
            threshold: Pixel variance threshold for routing decision
                      Images with variance < threshold will be processed locally
                      Images with variance >= threshold will be forwarded
        """
        self.threshold = threshold

    def calculate_complexity(self, image_array):
        """
        Calculate image complexity using pixel variance

        Args:
            image_array: NumPy array of shape (1, 224, 224, 3)

        Returns:
            float: Pixel variance (complexity metric)
        """
        return float(np.var(image_array))

    def should_process_locally(self, complexity):
        """
        Determine if image should be processed locally based on complexity

        Args:
            complexity: Calculated image complexity (variance)

        Returns:
            bool: True if should process locally, False if should forward
        """
        return complexity < self.threshold

    def get_routing_decision(self, image_array):
        """
        Make complete routing decision for an image

        Args:
            image_array: NumPy array of shape (1, 224, 224, 3)

        Returns:
            dict: {
                'complexity': float,
                'process_locally': bool,
                'threshold': float
            }
        """
        complexity = self.calculate_complexity(image_array)
        process_locally = self.should_process_locally(complexity)

        return {
            'complexity': complexity,
            'process_locally': process_locally,
            'threshold': self.threshold
        }
