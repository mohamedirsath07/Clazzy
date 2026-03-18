# 👔 Clazzy - AI-Powered Outfit Recommendation App

Your intelligent fashion companion that provides AI-powered outfit recommendations with perfect color combinations and complete wardrobe styling for any occasion.

![Clazzy Logo](https://img.shields.io/badge/Clazzy-AI%20Fashion-purple?style=for-the-badge)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

## ✨ Features

### 📱 Install as Mobile App (PWA)
Clazzy can be installed on your phone like a native app - no app store needed!

**Android (Chrome/Edge):**
1. Open Clazzy in Chrome on your Android device
2. Tap the "Install App" banner OR tap the menu (⋮) → "Add to Home screen"
3. The app icon will appear on your home screen

**iPhone/iPad (Safari):**
1. Open Clazzy in Safari on your iOS device
2. Tap the Share button (📤)
3. Scroll down and tap "Add to Home Screen"
4. Tap "Add" to confirm

### 🎨 Smart Outfit Recommendations
- **Color Harmony Analysis**: Uses color theory principles to score outfit combinations
  - Complementary colors (opposite on color wheel): 95% base score
  - Monochromatic (same hue, different brightness): 88%
  - Analogous (adjacent colors): 85%
  - Neutral pairs: 82%
  - Triadic colors: 80%

### 🎯 Occasion-Based Filtering
- **Formal/Business**: Excludes t-shirts and jeans, boosts dress shirts + dark pants
- **Sports**: Filters out dress shirts and jeans, prioritizes athletic wear
- **Party**: Preferences bright, saturated colors
- **Date**: Favors warm, balanced colors
- **Casual**: Balanced scoring for all styles

### 💾 Saved Collection
- Save favorite outfit combinations to local IndexedDB storage
- View saved outfits with images, occasion, and match scores
- Delete individual outfits from collection
- Persistent storage across sessions

### 📚 Smart Library Management
- Upload and organize your wardrobe items
- Automatic categorization into Tops and Bottoms
- Filter by clothing type (All/Tops/Bottoms)
- Select All / Deselect All functionality
- Support for both local (IndexedDB) and cloud (Firebase) storage

### 🎭 User Personalization
- Enter name, age, and gender preferences
- Personalized recommendations based on user profile
- Multiple occasion support

### ✨ Beautiful Animations
- GSAP-powered entrance animations
- Smooth transitions and micro-interactions
- Floating particles background
- Gradient text effects
- Hover effects with scale and glow

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- Python 3.9+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mohamedirsath07/Clazzy.git
cd Clazzy
```

2. **Install frontend dependencies**
```bash
cd Fashion-Style/client
npm install
```

3. **Install backend dependencies**
```bash
cd ../backend
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the `Fashion-Style/client` directory:
```env
# Firebase Configuration (optional)
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_bucket

# Storage Mode
VITE_USE_LOCAL_STORAGE=true  # Set to false to use Firebase
```

### Running the Application

**Terminal 1 - Frontend:**
```bash
cd Fashion-Style/client
npm run dev
```
Frontend will run on `http://localhost:5000`

**Terminal 2 - Backend:**
```bash
cd Fashion-Style/backend
python main.py
```
Backend will run on `http://localhost:8001`

## 🏗️ Architecture

### Frontend (React + TypeScript)
```
Fashion-Style/client/
├── src/
│   ├── components/        # React components
│   │   ├── Hero.tsx      # Landing page with animations
│   │   ├── Library.tsx   # Wardrobe library management
│   │   ├── MLOutfitCard.tsx  # Outfit recommendation cards
│   │   ├── OutfitHistory.tsx # Saved collection modal
│   │   └── ...
│   ├── lib/              # Utilities and APIs
│   │   ├── mlApi.ts      # ML API client & color analysis
│   │   ├── localLibrary.ts   # IndexedDB storage
│   │   ├── firebase.ts   # Firebase integration
│   │   └── outfitHistory.ts  # Saved outfits storage
│   └── pages/
│       └── Home.tsx      # Main application page
```

### Backend (FastAPI + Python)
```
Fashion-Style/backend/
├── main.py                   # FastAPI server
├── color_analyzer.py         # Color extraction (K-means)
├── ml_classifier.py          # Clothing type classifier
├── outfit_recommender.py     # Outfit recommendation logic
├── emergency_recommender.py  # Fallback recommendation
└── requirements.txt
```

## 🎨 Color Harmony Algorithm

The app uses advanced color theory to score outfits:

1. **Extract dominant colors** from each clothing item using K-means clustering
2. **Convert to HSL** color space for analysis
3. **Calculate harmony** based on hue difference:
   - Complementary: 150-210° → 95%
   - Analogous: 0-30° → 85%
   - Triadic: 100-140° → 80%
   - Neutrals (low saturation) → 82%
4. **Apply occasion modifiers**:
   - Formal: +30% for colored shirts + dark pants
   - Sports: +25% for t-shirts + trackpants
   - Party: +15% for saturated colors

## 🛠️ Technologies Used

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **GSAP** - Animation library
- **Tailwind CSS** - Styling
- **Shadcn/ui** - UI components
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **IndexedDB** - Local storage

### Backend
- **FastAPI** - Python web framework
- **TensorFlow/Keras** - ML models
- **OpenCV** - Image processing
- **NumPy/Pandas** - Data manipulation
- **Scikit-learn** - ML utilities

### Storage
- **IndexedDB** - Browser-based local storage
- **Firebase Storage** - Optional cloud storage

## 📝 API Endpoints

### `/predict-type` (POST)
Classify clothing item as TOP or BOTTOM
- **Input**: Image file
- **Output**: `{ predicted_type: ‘top’ | ‘bottom’, confidence: number }`

### `/extract-colors` (POST)
Extract dominant colors from image
- **Input**: Image file
- **Output**: `{ colors: [{ hex, rgb, percentage }], dominant_color: string }`

### `/recommend-outfits` (POST)
Generate outfit recommendations
- **Input**: `{ tops: [...], bottoms: [...], occasion: string }`
- **Output**: `{ recommendations: [{ top, bottom, score }] }`

## 🎯 User Flow

1. **Upload clothes** via device or select from library
2. **Enter profile details** (name, age, gender)
3. **Select occasion** (casual, formal, party, etc.)
4. **Get recommendations** with smart color harmony scoring
5. **Save favorites** to your collection
6. **View saved outfits** anytime from the home page

## 🔧 Configuration

### Storage Mode
Toggle between local (IndexedDB) and cloud (Firebase) storage:
```typescript
// In .env
VITE_USE_LOCAL_STORAGE=true  // Use IndexedDB
VITE_USE_LOCAL_STORAGE=false // Use Firebase
```

### Occasion Rules
Customize occasion-based scoring in `Fashion-Style/client/src/lib/mlApi.ts`:
```typescript
case ‘formal’:
  if (topHSL.l < 0.2) return 0.15; // Exclude dark t-shirts
  if (topHSL.s > 0.3 && bottomHSL.l < 0.3) return 1.30; // Boost dress shirts
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m ‘Add some AmazingFeature’`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Mohamed Irsath**
- GitHub: [@mohamedirsath07](https://github.com/mohamedirsath07)

## 🙏 Acknowledgments

- Color theory principles from professional fashion design
- GSAP for beautiful animations
- Shadcn/ui for component library
- FastAPI for the robust backend framework

---

Made with ❤️ by Mohamed Irsath