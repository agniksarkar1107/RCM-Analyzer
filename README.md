# Risk Control Matrix Analyzer

An interactive Streamlit dashboard for analyzing Risk Control Matrix (RCM) documents, extracting key insights, and providing actionable recommendations.

## Features

- Upload different document types (PDF, XLSX, CSV, DOCX)
- Automatic extraction of structured data from RCM documents 
- Risk analysis using Google's Gemini AI
- Interactive visualization of risk metrics
- Detailed gap analysis with recommendations
- Vector database powered by ChromaDB for data persistence and search
- Multi-department risk heatmap visualization

## Screenshot

![RCM Analyzer Dashboard](https://img.icons8.com/color/96/000000/risk-management.png)

## Setup

### Prerequisites

- Python 3.9+
- Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rcm-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
   - Create a `.env` file in the project root
   - Add your Gemini API key: `GEMINI_API_KEY=your-api-key-here`

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to http://localhost:8501

3. Upload a Risk Control Matrix document (XLSX, CSV, PDF, or DOCX format)

4. View the analysis and interactive dashboard

## Project Structure

```
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this file)
├── README.md                 # Project documentation
├── utils/                    # Utility modules
│   ├── __init__.py           # Package initialization
│   ├── document_processor.py # Document processing utilities
│   ├── db.py                 # ChromaDB vector database integration
│   └── gemini.py             # Gemini API integration for AI analysis
└── chroma_db/                # ChromaDB persistent storage (created at runtime)
```

## Development

To contribute or modify the project:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

3. Make your changes and test them with Streamlit:
```bash
streamlit run app.py
```

## License

MIT License

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the web framework
- [Google Gemini AI](https://ai.google.dev/) for the AI analysis
- [ChromaDB](https://www.trychroma.com/) for vector database functionality
- [Plotly](https://plotly.com/) for interactive visualizations 