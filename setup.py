from setuptools import setup

setup(
    name="incident-analysis-dashboard",
    version="0.3.0",
    description=(
        "Consolidate security alerts and scan outputs into an incident dashboard with charts, "
        "correlation analysis and interactive exploration"
    ),
    py_modules=["incident_dashboard_v2", "incident_dashboard_v3"],
    install_requires=["pandas", "matplotlib", "numpy"],
    entry_points={
        "console_scripts": [
            # Bind the CLI entry point to v3 by default for advanced features
            "incident-dashboard=incident_dashboard_v3:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
