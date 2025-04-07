# SQL-Scorer

SQL-Scorer is a tool for analyzing, comparing, and optimizing SQL queries. It evaluates queries based on performance metrics, best practices, and readability, providing both a command-line interface and a web-based GUI for interactive use.

## Features

- **Query Analysis**
  - Performance metrics (execution time, CPU usage)
  - Best practices compliance
  - Readability scoring
  - Query plan analysis

- **Comparison Tools**
  - Side-by-side query comparison
  - Detailed score breakdown
  - Performance metrics visualization
  - Optimization suggestions

- **Optimization**
  - Automatic query formatting
  - Best practices recommendations
  - Index usage analysis
  - Query structure improvements

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/karamustafay21/SQL-Scorer
cd SQL-Scorer
```

2. Build and run using Docker Compose:
```bash
# For web interface
docker-compose up web

# For CLI
docker-compose run cli queries/query1.sql queries/query2.sql
```

### Local Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
# Web interface
streamlit run app.py

# CLI
python main.py queries/query1.sql queries/query2.sql
```

## Usage

### Web Interface

1. Access the web interface at `http://localhost:8501`
2. Enter your SQL queries in the text areas
3. Click "Compare Queries" to see the analysis

### Command Line Interface

Compare two SQL query files:
```bash
python main.py path/to/query1.sql path/to/query2.sql
```
