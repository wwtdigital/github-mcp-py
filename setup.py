from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="github_mcp_server",
    version="0.1.0",
    author="Windsurf Team",
    author_email="your.email@example.com",
    description="GitHub Message Control Protocol (MCP) server for Windsurf integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/github-mcp-py",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "github-mcp-server=github_mcp_server.__main__:main",
        ],
    },
)
