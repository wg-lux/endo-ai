"""Utility functions for the predictor module"""

from torchvision import transforms


def get_unorm(ds_config: dict):
    """Get the unnormalization transform"""
    unorm = transforms.Normalize(
        mean=[-m / s for m, s in zip(ds_config["mean"], ds_config["std"])],
        std=[1 / s for s in ds_config["std"]],
    )
    return unorm
