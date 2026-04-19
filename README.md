# Risk Analytics System

A distributed, real-time financial risk analytics platform that calculates Value-at-Risk (VaR), Expected Shortfall (ES), and volatility forecasts for financial instruments using Monte Carlo simulation and GARCH modeling.

## 📋 Project Overview

This system provides enterprise-grade risk measurement capabilities with:
- **Real-time Risk Calculation**: Streaming VaR/ES computations using Apache Spark
- **Market Data Production**: Spring Boot service publishing market data via Kafka
- **Volatility Forecasting**: GARCH models for predictive volatility analysis
- **Backtesting Framework**: Comprehensive VaR model validation against historical data
- **Interactive Dashboard**: Web-based visualization of risk metrics and trends
- **Containerized Architecture**: Docker-based deployment for easy scalability

## 🏗️ System Architecture

```
Market Data Producer (Java/Spring)
          ↓ (Kafka)
     Risk Engine Stream (PySpark)
          ↓ (PostgreSQL)
Dashboard Backend (Flask)
          ↓
     Web UI (HTML/JS)
```

### Module Breakdown

#### Producer Module (`producer-module/`)
Java/Spring Boot application responsible for generating and streaming market data.

**Key Components:**
- Market data producer service
- Kafka integration for event streaming
- Configurable data generation

**Technologies:** Java 17, Spring Boot, Maven, Kafka

#### Simulation Module (`simulation-module/`)
Python package containing core risk analytics and data processing logic.

**Key Components:**
- `risk_package/` - Core risk calculation package
  - `monte_carlo_spark.py` - Distributed Monte Carlo VaR/ES computation
  - `garch_forecast.py` - Volatility forecasting using GARCH models
  - `backtesting.py` - VaR model validation and breach analysis
  - `config.py` - Spark, Kafka, and database configuration
- `risk_engine_stream.py` - Real-time streaming risk calculation job
- `run_backtest.py` - Backtesting runner for historical validation
- `dashboard/` - Flask backend API

**Technologies:** Python 3.8+, PySpark 3.5.0, Kafka, NumPy, Pandas

#### Dashboard Module (`dashboard-module/`)
Flask-based REST API and web interface for risk metrics visualization.

**Key Components:**
- REST API endpoints for risk data retrieval
- Real-time risk metric aggregation
- VaR trend analysis
- Backtest result reporting

**Technologies:** Flask, PostgreSQL, JavaScript, HTML5

#### Scripts (`Scripts/`)
Infrastructure and deployment automation scripts.

**Key Scripts:**
- `setup-docker.sh` - Docker environment initialization
- `run-spark-job.sh` - Spark job submission
- `cleanup.sh` - Resource cleanup and teardown
- `verify-setup.sh` - System validation

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.8+ (for development)
- Java 11+ (for producer module)
- PostgreSQL 12+

### Setup & Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RiskAnalytics
   ```

2. **Initialize infrastructure**
   ```bash
   cd Scripts
   bash setup-docker.sh
   ```

3. **Build and start services**
   ```bash
   docker-compose -f producer-module/docker-compose.yml up -d
   ```

4. **Install Python dependencies**
   ```bash
   cd simulation-module
   python -m venv venv-spark
   source venv-spark/bin/activate  # On Windows: venv-spark\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Initialize database schema**
   ```bash
   psql -U postgres -d risk_analytics < simulation-module/sql/init_db.sql
   ```

6. **Start real-time risk engine**
   ```bash
   cd simulation-module
   python risk_engine_stream.py
   ```

7. **Launch dashboard**
   ```bash
   cd simulation-module/dashboard
   python app.py
   ```

Access the dashboard at `http://localhost:5000`

## 📊 Key Features

### Real-Time Risk Metrics
- **Value-at-Risk (VaR)**: 95% confidence level
- **Expected Shortfall (ES)**: Average loss beyond VaR
- **Volatility Forecast**: GARCH-based predictions
- **Live Price Tracking**: Per-symbol price updates

### Backtesting
- Historical VaR validation
- Breach rate analysis
- Model accuracy assessment
- Regulatory compliance testing

### Analytics
- Multi-symbol portfolio analysis
- Trend visualization (24-hour windows)
- Risk metric aggregation
- Performance comparison

## 🔧 Configuration

### Database Setup
Edit `simulation-module/risk_package/config.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'risk_analytics',
    'user': 'postgres',
    'password': 'your_password'
}
```

### Kafka Configuration
```python
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'market-data'
```

### Risk Parameters
```python
RISK_PARAMS = {
    'confidence_level': 0.95,
    'num_simulations': 10000,
    'lookback_window': 252
}
```

## 📡 API Endpoints

### Current Risk Metrics
```
GET /api/current_risk
```
Returns latest VaR and ES for all symbols sorted by risk level.

### VaR Trend
```
GET /api/var_trend/<symbol>
```
Returns 24-hour VaR trend for specified symbol.

### Backtest Results
```
GET /api/backtest_summary
```
Returns latest backtesting results for all symbols.

## 📈 Data Flow

1. **Market Data Generation**: Producer generates market data
2. **Kafka Streaming**: Data published to Kafka topic
3. **Spark Processing**: Real-time aggregation and window calculations
4. **Risk Calculation**: Monte Carlo VaR/ES computation
5. **PostgreSQL Storage**: Results persisted for queries
6. **Dashboard API**: REST endpoints serve data
7. **Web Visualization**: Interactive charts and tables

## 🧪 Testing

### Unit Tests
```bash
cd simulation-module
python -m pytest test_files/
```

### Kafka Integration Tests
```bash
python test_files/kafka_consumer_test.py
```

### Spark Job Tests
```bash
python test_files/test_spark.py
```

## 📚 Project Structure Details

### Database Schema
- `risk_metrics` - Real-time VaR/ES calculations per symbol
- `backtest_results` - Historical validation results
- `market_data` - Raw price data feed
- `forecast_data` - GARCH volatility forecasts

### Key Algorithms
- **Geometric Brownian Motion**: Asset price simulation
- **Monte Carlo VaR**: Multi-step simulation and quantile estimation
- **GARCH(1,1)**: Conditional heteroskedasticity modeling
- **Kupiec POF Test**: VaR model validation

## 🐳 Docker Compose Services

- **Zookeeper** (port 2181): Kafka coordination
- **Kafka** (port 9092): Message broker
- **PostgreSQL** (port 5432): Data persistence
- **Market Data Producer** (port 8080): Data generation API
- **Spark Master** (port 7077): Distributed processing

## 🔐 Security Considerations

- Use environment variables for sensitive credentials
- Enable SSL/TLS for Kafka and PostgreSQL in production
- Implement authentication on dashboard endpoints
- Validate and sanitize all API inputs
- Use secrets management system for credentials

## 🚨 Troubleshooting

**Spark Job Not Starting**
- Check Kafka connectivity: `docker exec kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092`
- Verify PostgreSQL is running: `psql -U postgres -d risk_analytics`

**Dashboard API Errors**
- Check database connection in `config.py`
- Verify risk_metrics table exists: `\dt risk_metrics`
- Review Flask logs: `tail -f dashboard.log`

**Memory Issues**
- Increase Spark driver memory: `--driver-memory 4g`
- Adjust executor memory: `--executor-memory 2g`

## 📖 Documentation

- [Producer Module README](producer-module/README.md)
- [Market Data Producer Help](producer-module/market-data-producer/HELP.md)
- Database schemas: `simulation-module/sql/`
- Configuration: `simulation-module/risk_package/config.py`

## 🤝 Development

### Adding New Risk Metrics
1. Implement calculation in `risk_package/monte_carlo_spark.py`
2. Update Spark streaming job in `risk_engine_stream.py`
3. Create database migration for schema changes
4. Add API endpoint in `dashboard/app.py`

### Extending Backtesting
1. Add test functions in `risk_package/backtesting.py`
2. Update `run_backtest.py` with new validation logic
3. Extend API with `/api/backtest_details/<symbol>` endpoint

## 📝 License

[Add your license here]

## ✉️ Contact & Support

[Add contact information]

## 🗺️ Roadmap

- [ ] Multi-factor risk models (market, credit, operational)
- [ ] Real-time stress testing scenarios
- [ ] Portfolio optimization engine
- [ ] Advanced charting with WebGL rendering
- [ ] Machine learning-based risk prediction
- [ ] Regulatory reporting automation (Basel III)

---

**Last Updated**: April 2026  
**Status**: Active Development
