# Clazzy - AI-Powered Fashion Outfit Recommender

Clazzy is an intelligent fashion recommendation system that helps you create perfectly coordinated outfits using **color harmony matching** and style analysis.

## Features

- **Separate Top/Bottom Upload** - Dedicated upload sections ensure accurate categorization (no more ML misclassification!)
- **Color Harmony Matching** - Uses color theory (complementary, analogous, triadic) to score outfit combinations
- **Real-time Color Extraction** - Automatically extracts dominant colors from clothing images
- **Wardrobe Library** - Save and organize your clothing items with Firebase integration
- **Occasion-based Suggestions** - Get recommendations for casual, formal, business, party, and more

## How It Works

```
┌─────────────────┐     ┌─────────────────┐
│   Upload Tops   │     │ Upload Bottoms  │
│  (shirts, etc.) │     │  (pants, etc.)  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
    ┌─────────────────────────────────┐
    │     Extract Dominant Colors      │
    └─────────────────┬───────────────┘
                      ▼
    ┌─────────────────────────────────┐
    │   Score ALL Top+Bottom Pairs    │
    │   by Color Harmony Algorithm    │
    └─────────────────┬───────────────┘
                      ▼
    ┌─────────────────────────────────┐
    │   Return Top 3 Best Outfits     │
    └─────────────────────────────────┘
```

### Color Harmony Algorithm

| Harmony Type | Hue Difference | Score |
|--------------|----------------|-------|
| Complementary (opposite colors) | 150-210° | 90-98% |
| Analogous (similar colors) | 0-45° | 80-90% |
| Triadic (120° apart) | 110-130° | 85-93% |
| Split-complementary | 135-165° | 82-90% |
| Neutral colors (black/white/gray) | Any | 85-95% |

## Project Structure

```
Clazzy/
├── Fashion-Style/          # Frontend + Express Server
│   ├── client/             # React + Vite + TailwindCSS
│   │   ├── src/
│   │   │   ├── components/ # UI components (ImageUpload, MLOutfitCard, etc.)
│   │   │   ├── lib/
│   │   │   │   └── mlApi.ts # Color harmony recommendation engine
│   │   │   └── pages/
│   │   │       └── Home.tsx # Main app with top/bottom upload sections
│   │   └── ...
│   └── server/             # Express backend
│
└── clazzy_v2/              # V2 API Backend (FastAPI)
    ├── api/
    │   ├── main.py         # API endpoints
    │   └── config.py       # Configuration
    ├── core/
    │   ├── recommendation/ # Hybrid recommendation engine
    │   ├── personalization/# User preference learning
    │   └── vision/         # Image analysis modules
    └── requirements-minimal.txt
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+

### Running Locally

**1. Start the V2 API Backend (Port 8001)**

```bash
cd clazzy_v2
pip install -r requirements-minimal.txt
python -m uvicorn api.main:app --reload --port 8001
```

**2. Start the Frontend (Port 5000)**

```bash
cd Fashion-Style
npm install
npm run dev
```

**3. Open in Browser**

Visit **http://localhost:5000**

## Usage

1. **Upload Tops** - Add shirts, t-shirts, blouses, jackets to the purple "Upload Tops" section
2. **Upload Bottoms** - Add pants, jeans, skirts, shorts to the blue "Upload Bottoms" section
3. **Select Occasion** - Choose your event type (casual, formal, business, party, date, sports)
4. **Generate Outfits** - Click "Generate Outfits" to get AI-powered recommendations
5. **View Results** - See the top 3 best-matching outfit combinations with harmony scores

## API Endpoints (V2)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with model status |
| `/api/v2/analyze` | POST | Analyze clothing image (color extraction) |
| `/api/v2/recommend` | POST | Get outfit recommendations |
| `/api/v2/score-outfit` | POST | Score a specific outfit |
| `/api/v2/users` | POST | Create user profile |
| `/api/v2/users/{id}` | GET | Get user profile |

## Tech Stack

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS + Radix UI
- Firebase (optional wardrobe storage)

### Backend
- FastAPI (Python 3.10+)
- Pillow (image processing)
- scikit-learn (color clustering)
- Pydantic (validation)

## Environment Variables

Create `.env` in `clazzy_v2/`:

```env
ENVIRONMENT=development
DEBUG=true
MODEL_DIR=./models
CORS_ORIGINS=["http://localhost:3000","http://localhost:5000"]
```

## Recent Updates

### V2.1 - Color Harmony System
- **Fixed**: Top+Top pairing bug - now properly uses separate upload sections
- **New**: Color harmony scoring based on color theory
- **New**: Extracts dominant colors from images using canvas sampling
- **Improved**: User categorization is trusted (no ML misclassification)

### V2.0 - Architecture Upgrade
- FastAPI backend with modular recommendation engine
- Hybrid scoring (color + style + occasion)
- User personalization engine
- Graceful degradation when ML models aren't loaded

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License
