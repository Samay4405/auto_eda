# AutoEDA - Automated Exploratory Data Analysis System

A comprehensive web application for automated exploratory data analysis featuring a **streamlined step-by-step workflow** that guides users through intelligent data processing and visualization.

## ✨ New Step-by-Step Workflow

### 🎯 **Simplified User Experience**

The platform now features an intuitive step-by-step process:

1. **Upload your CSV file** (up to 100MB)
2. **Choose Analysis Mode** (AI or Manual) - applies to all subsequent steps
3. **Select Processing Steps** - choose which operations to perform:
   - Data Cleaning (optional)
   - Data Transformation (optional)
   - Data Classification (optional)
4. **Visualize Results** with two options:
   - **Smart Dashboard**: AI-generated consolidated view with key insights
   - **Individual Charts**: Detailed exploration of separate visualizations

### 🧠 **Intelligent Processing**

- **AI Mode**: Automatic parameter selection and optimal processing pipeline
- **Manual Mode**: Full control over configurations and options
- **Smart Recommendations**: Context-aware suggestions throughout the process

## Features

### 🚀 Core Functionality

- **File Upload**: Easy drag-and-drop CSV file upload (up to 100MB)
- **Guided Workflow**: Step-by-step process for data analysis
- **Multiple Operations**:
  - Data Cleaning (remove duplicates, handle missing values, outliers)
  - Data Transformation (scaling, encoding, feature engineering)
  - Data Classification (analyze data types, quality metrics)
  - Data Visualization (comprehensive charts and dashboards)

### 🤖 AI-Powered Analysis

- **Manual Mode**: Configure specific operations and parameters
- **AI Mode**: Automated analysis using Groq and LangGraph
- **Smart Insights**: AI-generated recommendations and insights
- **MCP Integration**: Model Context Protocol for intelligent automation

### 📊 Visualizations

- **Smart Dashboard**: AI-curated consolidated view with most relevant charts
- **Individual Charts**: Detailed exploration interface
- Interactive charts using Plotly.js
- Distribution plots, correlation heatmaps, scatter plots
- Box plots, bar charts, pie charts
- Missing values analysis
- Downloadable charts and dashboards

## Tech Stack

### Backend

- **Python 3.8+**
- **FastAPI** - Modern, fast web framework
- **LangGraph** - AI workflow orchestration
- **Groq** - AI language model integration
- **Pandas, NumPy** - Data manipulation
- **Scikit-learn** - Machine learning utilities
- **Plotly** - Chart generation
- **Matplotlib, Seaborn** - Additional plotting

### Frontend

- **React 19** - Modern React with hooks
- **Vite** - Fast build tool
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Plotly.js** - Interactive chart rendering
- **React-Plotly.js** - React wrapper for Plotly
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Notifications

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. **Navigate to the server directory:**

   ```bash
   cd server
   ```

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   - Copy `.env.example` to `.env` (if available) or create `.env` file
   - Add your Groq API key:

   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the backend server:**

   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the client directory:**

   ```bash
   cd client
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### Getting a Groq API Key

1. Visit [Groq Console](https://console.groq.com)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

## Usage

### Quick Start

1. **Start both servers** (backend and frontend)
2. **Open your browser** to `http://localhost:5173`
3. **Upload a CSV file** using the upload interface
4. **Choose an operation:**
   - **Clean**: Remove duplicates, handle missing values
   - **Transform**: Scale features, encode categories
   - **Classify**: Analyze data types and quality
   - **Visualize**: Generate comprehensive charts
5. **Select mode:**
   - **Manual**: Configure specific parameters
   - **AI**: Let AI automatically analyze and process
6. **View results** with interactive charts and insights

### Detailed Workflow

#### Data Cleaning

- **Missing Values**: Choose between dropping or imputing
- **Duplicates**: Automatic duplicate detection and removal
- **Outliers**: IQR-based outlier detection and removal
- **Data Types**: Automatic type conversion

#### Data Transformation

- **Scaling**: Standard scaling or Min-Max scaling
- **Encoding**: Label encoding or One-hot encoding
- **Feature Engineering**: Create interaction features

#### Data Classification

- **Type Analysis**: Automatic column type detection
- **Quality Score**: Data quality assessment
- **Recommendations**: Suggestions for data improvements

#### Data Visualization

- **Distribution Charts**: Histograms, box plots
- **Relationships**: Scatter plots, correlation heatmaps
- **Categorical Analysis**: Bar charts, pie charts
- **Missing Values**: Visualization of missing data patterns

## API Endpoints

### File Management

- `POST /api/upload` - Upload CSV file
- `GET /api/file/{file_id}/info` - Get file information
- `DELETE /api/file/{file_id}` - Delete uploaded file

### Data Processing

- `POST /api/process` - Process data with specified operation
- `GET /api/charts/{file_id}` - Generate charts
- `GET /api/insights/{file_id}` - Get AI insights

### Health Check

- `GET /health` - API health check

## Project Structure

```
├── client/                 # Frontend React application
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   ├── pages/         # Page components
│   │   ├── api/           # API service functions
│   │   └── styles/        # CSS and styling
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
│
├── server/                # Backend Python application
│   ├── services/         # Business logic services
│   │   ├── data_processor.py    # Data cleaning & transformation
│   │   ├── ai_agent.py          # AI-powered analysis
│   │   └── chart_generator.py   # Chart generation
│   ├── api.py            # API route definitions
│   ├── main.py           # FastAPI application entry point
│   └── requirements.txt  # Python dependencies
│
└── README.md             # This file
```

## Development

### Backend Development

- The backend uses FastAPI with automatic API documentation at `http://localhost:8000/docs`
- Hot reload is enabled during development
- Add new routes in `api.py`
- Business logic should be in `services/` directory

### Frontend Development

- Vite provides fast hot module replacement
- Components are in `src/components/`
- Pages are in `src/pages/`
- Tailwind CSS for styling
- React Router for navigation

### Adding New Features

1. **Backend**: Add new endpoints in `api.py` and logic in `services/`
2. **Frontend**: Create components in `src/components/` and update routing
3. **API Integration**: Update `src/api/apiService.js` for new endpoints

## Deployment

### Production Build

**Frontend:**

```bash
cd client
npm run build
```

**Backend:**

```bash
cd server
# Use a production WSGI server like uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Environment Variables

**Production Environment:**

- Set `GROQ_API_KEY` in your production environment
- Configure proper CORS origins in `main.py`
- Set up proper file storage (not local filesystem)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

1. Check the API documentation at `http://localhost:8000/docs`
2. Review the browser console for frontend errors
3. Check server logs for backend issues
4. Ensure all dependencies are properly installed

## Roadmap

- [ ] Support for additional file formats (Excel, JSON)
- [ ] User authentication and file management
- [ ] Advanced ML model integration
- [ ] Real-time collaboration features
- [ ] Cloud deployment templates
- [ ] Advanced statistical analysis
- [ ] Custom chart configuration
- [ ] Data export in multiple formats
