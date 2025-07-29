# US Government RSS Data Aggregator

## Overview

This project aggregates data from various US Government RSS feeds, including the Department of Defense (DOD), DOD Contract Awards, Department of State, Congress, and Presidential Documents. The collected data is processed using the Grok API (via the OpenAI Python SDK) with structured outputs to generate summaries. The results are stored in a database for reference, analysis, and fine-tuning datasets for further machine learning applications.

The project is built with Python, managed using the UV package manager, and leverages the OpenAI Python SDK for interacting with the Grok API.

## Features

- **RSS Feed Parsing**: Collects links and data from specified US Government RSS feeds.
- **Grok API Integration**: Uses the OpenAI Python SDK to send data to the Grok API and receive structured outputs for summarization.
- **Data Storage**: Stores processed data and summaries in a database for easy querying and dataset creation.
- **Modular Design**: Easily extendable to include additional RSS feeds or processing logic.
- **Dependency Management**: Uses UV for efficient and reproducible Python package management.
