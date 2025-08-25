from setuptools import setup

setup(
    name="incident-analysis-dashboard",
    version="0.2.0",
    description="Consolidate security alerts and scan outputs into an incident dashboard with charts and reporting",
    py_modules=["incident_dashboard_v2"],
    install_requires=["pandas", "matplotlib"],
    entry_points={
        "console_scripts": [
            "incident-dashboard=incident_dashboard_v2:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
