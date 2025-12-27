# Clazzy - AI-Powered Fashion Recommendation System

## Complete Project Prompt for Reconstruction

Build a full-stack Progressive Web App (PWA) called **Clazzy** - an intelligent fashion assistant that uses deep learning, color theory, and MongoDB to help users create perfect outfits for any occasion.

---

## 🎯 Core Features

### 1. **AI-Powered Image Classification**
- Upload clothing images and automatically classify them using ResNet50 deep learning model
- Categories: Top, Bottom, Dress, Shoes, Blazer, Other
- Extract dominant colors using K-means clustering (5 colors per item)
- Generate deep learning feature embeddings for style similarity matching

### 2. **Smart Outfit Recommendations**
- Generate outfit combinations based on:
  - **Occasion**: Casual, Formal, Business, Party, Date, Sports
  - **Color Harmony**: Complementary, Analogous, Triadic color schemes
  - **Style Similarity**: Using ResNet50 feature vectors
  - **Rule-Based Logic**: Prevent invalid combinations (e.g., shirt+shirt)
- Score each outfit on:
  - Color harmony (30%)
  - Style compatibility (30%)
  - Occasion appropriateness (30%)
  - Variety bonus (10%)

### 3. **Digital Wardrobe Management**
- Firebase Authentication for user login
- MongoDB database for persistent storage:
  - Users with preferences (body type, style, favorite colors)
  - Clothing items with metadata (colors, ML embeddings, timestamps)
  - Saved outfits with scoring
  - User activity analytics with 90-day TTL
- Firebase Storage for image uploads
- Local library fallback when offline

### 4. **Progressive Web App (PWA)**
- Installable on mobile and desktop
- Offline support with service workers
- Responsive dark/light theme toggle
- Fast, app-like experience

---

## 🏗️ Technical Architecture

### **Frontend** (React + TypeScript + Vite)
```
client/
├── src/
│   ├── components/
│   │   ├── Header.tsx                    # Navigation bar with theme toggle
│   │   ├── Hero.tsx                      # Landing section
│   │   ├── UserDetailsForm.tsx           # User preferences (body type, style)
│   │   ├── ImageUpload.tsx               # Drag-n-drop upload with preview
│   │   ├── ProgressIndicator.tsx         # Loading states
│   │   ├── OccasionSelector.tsx          # Occasion picker buttons
│   │   ├── MLOutfitCard.tsx              # Display recommended outfits
│   │   ├── Library.tsx                   # Wardrobe gallery view
│   │   ├── ThemeProvider.tsx & ThemeToggle.tsx  # Dark/light mode
│   │   └── ui/                           # Shadcn/ui components (40+ components)
│   ├── lib/
│   │   ├── firebase.ts                   # Firebase config & auth
│   │   ├── mlApi.ts                      # ML backend API client
│   │   ├── localLibrary.ts               # IndexedDB fallback
│   │   ├── queryClient.ts                # TanStack Query setup
│   │   └── utils.ts                      # Tailwind class merge
│   └── pages/
│       ├── Home.tsx                      # Main page workflow
│       └── not-found.tsx                 # 404 page
```

**Key Dependencies:**
- React 18 + React DOM
- TypeScript 5.6
- Vite 5.4 (build tool)
- TanStack Query (data fetching)
- Wouter (routing)
- React Hook Form + Zod (forms & validation)
- Tailwind CSS 3.4 + Radix UI (styling)
- Framer Motion (animations)
- Firebase SDK (auth & storage)
- Vite PWA Plugin + Workbox (PWA functionality)

---

### **Backend - Express Server** (Node.js + TypeScript)
```
server/
├── index.ts                  # Main Express server entry
├── routes.ts                 # API routes (optional legacy)
├── mongoRoutes.ts            # MongoDB REST API endpoints
├── db.ts                     # MongoDB connection handler
├── models.ts                 # Mongoose schemas (User, ClothingItem, Outfit, UserActivity)
├── storage.ts                # File upload handlers
└── vite.ts                   # Vite dev server integration
```

**API Endpoints (MongoDB):**
- `POST /api/users` - Create new user
- `GET /api/users/:firebaseUid` - Get user by Firebase UID
- `PATCH /api/users/:firebaseUid` - Update user preferences
- `POST /api/wardrobe/items` - Add clothing item
- `GET /api/wardrobe/items/:firebaseUid` - Get user's wardrobe
- `PATCH /api/wardrobe/items/:id` - Update item (favorite, worn count)
- `DELETE /api/wardrobe/items/:id` - Delete item
- `POST /api/outfits` - Save outfit
- `GET /api/outfits/:firebaseUid` - Get user's outfits
- `PATCH /api/outfits/:id` - Update outfit
- `DELETE /api/outfits/:id` - Delete outfit
- `GET /api/analytics/:firebaseUid` - Get user statistics
- `POST /api/analytics/track` - Track user activity

**MongoDB Schemas:**
```typescript
User {
  firebaseUid: string (unique, indexed)
  email: string
  displayName?: string
  preferences: {
    bodyType: 'slim' | 'athletic' | 'curvy' | 'plus-size'
    stylePreference: Array<'casual' | 'formal' | 'sporty' | 'trendy' | 'classic' | 'bohemian'>
    favoriteColors: string[]
    occasionFrequency: { casual, formal, business, party, date, sports }
  }
  totalUploads: number
  totalOutfitsGenerated: number
  createdAt, lastLoginAt
}

ClothingItem {
  userId: ObjectId
  firebaseUid: string (indexed)
  filename: string
  type: 'top' | 'bottom' | 'dress' | 'shoes' | 'blazer' | 'other'
  dominantColor: string
  colors: [{ hex, rgb, hsv, percentage }]
  imageUrl: string
  confidence: number
  mlEmbedding: number[]  // ResNet50 features
  isFavorite: boolean
  timesWorn: number
  uploadedAt, lastWornAt
}

Outfit {
  userId: ObjectId
  firebaseUid: string
  occasion: 'casual' | 'formal' | 'business' | 'party' | 'date' | 'sports'
  items: [{ itemId, filename, type, color, imageUrl }]
  score: number (0-100)
  harmonyScore, styleScore, occasionScore: number
  isFavorite: boolean
  timesWorn: number
  createdAt, lastWornAt
}

UserActivity {
  userId: ObjectId
  firebaseUid: string
  action: 'upload_item' | 'generate_outfit' | 'save_outfit' | ...
  metadata: any
  timestamp: Date (TTL index: 90 days auto-delete)
}
```

**Key Dependencies:**
- Express 4.21
- Mongoose 8.19 (MongoDB ODM)
- MongoDB driver 6.20
- Dotenv (environment variables)
- Express Session + Passport (auth middleware)
- WebSocket (ws) for real-time features

---

### **ML Backend** (Python + FastAPI)
```
backend/
├── main.py                   # FastAPI server entry
├── ml_classifier.py          # ResNet50 clothing classifier
├── color_analyzer.py         # K-means color extraction
├── outfit_recommender.py     # Outfit generation engine
└── requirements.txt
```

**Endpoints:**
- `GET /` - Health check
- `POST /predict-type` - Classify clothing image
  - Input: Image file
  - Output: `{ predicted_type, confidence, colors[5], dominant_color }`
- `POST /recommend-outfits` - Generate outfit recommendations
  - Input: `occasion` (form), `max_items` (default: 2)
  - Output: `{ occasion, recommendations[], total_items_analyzed }`

**ML Pipeline:**
1. **ResNet50 Classifier** (`ml_classifier.py`)
   - Pre-trained ImageNet weights
   - Transfer learning for clothing categories
   - Outputs: Class prediction + 2048-dim feature embeddings

2. **K-means Color Analyzer** (`color_analyzer.py`)
   - Extract 5 dominant colors per image
   - RGB → HSV → Hex conversion
   - Color naming using webcolors library
   - Calculate color percentages

3. **Outfit Recommender** (`outfit_recommender.py`)
   - **Color Harmony**:
     - Complementary (180° hue difference)
     - Analogous (30-60° hue range)
     - Triadic (120° spacing)
   - **Style Similarity**: Cosine similarity of ResNet50 embeddings
   - **Occasion Rules**:
     ```python
     'formal': [('blazer', 'top', 'bottom'), ('dress',)]
     'casual': [('top', 'bottom'), ('dress',)]
     'party': [('dress',), ('top', 'bottom')]
     ```
   - **Anti-Duplication**: Track used items to prevent shirt+shirt combos

**Python Dependencies:**
```
fastapi==0.100.0
uvicorn==0.22.0
tensorflow>=2.16.0
scikit-learn>=1.3.0
opencv-python>=4.8.0
Pillow>=10.0.0
numpy>=1.24.0
colormath>=3.0.0
webcolors>=1.13
```

---

## 🗄️ Database & Storage

### **MongoDB Atlas**
- Cloud-hosted database (free tier M0)
- Collections: `users`, `clothingitems`, `outfits`, `useractivities`
- Indexes on `firebaseUid`, `userId`, `type`, `occasion`, `timestamp`
- TTL index on `useractivities` (90-day retention)

### **Firebase**
- **Authentication**: Email/password, Google OAuth
- **Storage**: Image uploads in `/uploads/{userId}/{filename}`
- **Firestore** (optional): Real-time sync alternative

### **File Storage**
- Local uploads directory: `client/public/uploads/`
- Images served via static middleware

---

## 🎨 UI/UX Design

### **Design System**
- **Framework**: Tailwind CSS 3.4 + CSS variables
- **Component Library**: Radix UI primitives
- **Theme**: Dark mode default (toggle to light)
- **Colors**: 
  - Primary: Purple-600 (#7C3AED)
  - Accent: Pink-500, Blue-500
  - Neutrals: Slate-900 to Slate-50
- **Typography**: Inter font family
- **Icons**: Lucide React + React Icons

### **Key UI Components** (40+ Shadcn/ui components)
- Button, Card, Badge, Avatar, Progress
- Dialog, Sheet, Dropdown Menu, Select, Popover
- Form, Input, Textarea, Checkbox, Switch, Slider
- Toast, Alert, Accordion, Tabs, Carousel
- Tooltip, Hover Card, Context Menu
- (All in `client/src/components/ui/`)

### **Page Layout**
```
┌─────────────────────────────────────────┐
│  Header (Logo, Theme Toggle, User)     │
├─────────────────────────────────────────┤
│  Hero Section (Title, Tagline)         │
├─────────────────────────────────────────┤
│  User Details Form (Body, Style)       │
├─────────────────────────────────────────┤
│  Image Upload (Drag & Drop)            │
│  → Shows preview + AI classification   │
├─────────────────────────────────────────┤
│  Occasion Selector (6 buttons)         │
├─────────────────────────────────────────┤
│  ML Outfit Recommendations Grid        │
│  → Cards with items + scores           │
├─────────────────────────────────────────┤
│  Wardrobe Library (Gallery)            │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
clazzy/
├── .env                          # Environment variables
├── .gitignore
├── package.json                  # Node dependencies
├── tsconfig.json                 # TypeScript config
├── vite.config.ts                # Vite build config
├── tailwind.config.ts            # Tailwind CSS config
├── postcss.config.js
├── components.json               # Shadcn/ui config
├── drizzle.config.ts             # Drizzle ORM (optional Postgres)
├── vercel.json                   # Deployment config
├── Clazzy_Logo.jpg               # App logo
│
├── client/                       # React frontend
│   ├── index.html
│   ├── public/
│   │   └── uploads/              # User-uploaded images
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── index.css
│       ├── components/ (20+ files)
│       ├── lib/ (5 files)
│       └── pages/ (2 files)
│
├── server/                       # Express backend
│   ├── index.ts
│   ├── db.ts
│   ├── models.ts
│   ├── mongoRoutes.ts
│   ├── routes.ts
│   ├── storage.ts
│   └── vite.ts
│
├── backend/                      # Python ML
│   ├── main.py
│   ├── ml_classifier.py
│   ├── color_analyzer.py
│   ├── outfit_recommender.py
│   └── requirements.txt
│
├── shared/
│   └── schema.ts                 # Shared TypeScript types
│
└── concat-map/                   # Dependency (internal)
```

---

## 🚀 Setup & Run Instructions

### **1. Prerequisites**
- Node.js 20+
- Python 3.10+
- MongoDB Atlas account (or local MongoDB)
- Firebase project (Auth + Storage enabled)

### **2. Environment Variables** (`.env`)
```bash
# MongoDB
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/clazzy?retryWrites=true&w=majority

# Server
PORT=8000
NODE_ENV=development

# Frontend
VITE_API_URL=http://localhost:8000
```

### **3. Install Dependencies**
```bash
# Node.js (Frontend + Backend)
npm install

# Python (ML Backend)
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
# or: source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### **4. Firebase Setup**
1. Create Firebase project at https://console.firebase.google.com
2. Enable Authentication (Email/Password + Google)
3. Enable Storage with rule:
   ```
   allow read, write: if request.auth != null;
   ```
4. Copy config to `client/src/lib/firebase.ts`:
   ```typescript
   const firebaseConfig = {
     apiKey: "YOUR_API_KEY",
     authDomain: "YOUR_AUTH_DOMAIN",
     projectId: "YOUR_PROJECT_ID",
     storageBucket: "YOUR_STORAGE_BUCKET",
     messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
     appId: "YOUR_APP_ID"
   };
   ```

### **5. Run Development Servers**

**Terminal 1 - Node.js Backend:**
```bash
npm run dev
# Runs Express server on http://localhost:8000
# Auto-connects to MongoDB
# Serves Vite dev server + API
```

**Terminal 2 - Python ML Backend:**
```bash
cd backend
.venv\Scripts\Activate.ps1
python main.py
# Runs FastAPI on http://localhost:8000 (ML endpoints)
# Loads ResNet50 model on first request
```

### **6. Build for Production**
```bash
# Build frontend + backend
npm run build

# Start production server
npm start
```

---

## 🔑 Key Implementation Details

### **Workflow: User Uploads Image**
1. User drags/drops image in `ImageUpload.tsx`
2. Frontend sends to Express `/api/upload` → saves to Firebase Storage
3. Frontend calls ML `/predict-type` → ResNet50 classifies
4. ML returns `{ type, confidence, colors[], dominant_color }`
5. Frontend displays preview with AI tags
6. User clicks "Add to Wardrobe" → saves to MongoDB via `/api/wardrobe/items`

### **Workflow: Generate Outfit**
1. User selects occasion (e.g., "Formal") in `OccasionSelector.tsx`
2. Frontend calls ML `/recommend-outfits?occasion=formal&max_items=3`
3. ML backend:
   - Loads all images from `uploads/` directory
   - Classifies each with ResNet50
   - Extracts colors with K-means
   - Generates combinations using `outfit_recommender.py`:
     - Filter by occasion rules (`formal` → blazer+top+bottom or dress)
     - Calculate color harmony scores
     - Calculate style similarity (cosine of embeddings)
     - Rank by total score
   - Returns top 5 outfits
4. Frontend displays in `MLOutfitCard.tsx` grid
5. User clicks "Save Outfit" → stores in MongoDB via `/api/outfits`

### **Anti-Duplication Logic** (`outfit_recommender.py`)
```python
def _generate_combinations(items_by_type, pattern, used_items=set()):
    """
    Generate outfit combinations WITHOUT reusing items.
    
    Example:
    - pattern = ('top', 'bottom')
    - items_by_type = { 'top': [shirt1, shirt2], 'bottom': [pants1] }
    - used_items tracks already-selected item IDs
    
    Ensures:
    - No duplicate items in same outfit (shirt1 + shirt1)
    - No invalid combos (shirt + shirt, pants + pants)
    """
    if not pattern:
        yield []
        return
    
    current_type = pattern[0]
    remaining = pattern[1:]
    
    for item in items_by_type.get(current_type, []):
        item_id = item.get('id') or item.get('filename') or str(item)
        
        if item_id in used_items:
            continue  # Skip already-used items
        
        new_used = used_items | {item_id}
        
        for rest in _generate_combinations(items_by_type, remaining, new_used):
            yield [item] + rest
```

### **Color Harmony Scoring** (`color_analyzer.py`)
```python
def calculate_color_harmony(color1_hex, color2_hex):
    # Convert hex → HSV
    h1, s1, v1 = hex_to_hsv(color1_hex)
    h2, s2, v2 = hex_to_hsv(color2_hex)
    
    hue_diff = abs(h1 - h2)
    
    # Complementary: ~180° (opposite on color wheel)
    if 160 <= hue_diff <= 200:
        return 0.9
    
    # Analogous: 30-60° (adjacent colors)
    elif 30 <= hue_diff <= 60:
        return 0.85
    
    # Triadic: ~120° (evenly spaced)
    elif 110 <= hue_diff <= 130:
        return 0.8
    
    # Monochromatic: same hue, different saturation/value
    elif hue_diff < 15:
        return 0.7
    
    else:
        return 0.5  # Neutral/clashing
```

---

## 🎯 Advanced Features to Implement

### **Phase 1 (MVP - Current)**
- ✅ Image upload + classification
- ✅ Color extraction
- ✅ Outfit recommendations
- ✅ MongoDB persistence
- ✅ Firebase auth
- ✅ PWA support

### **Phase 2 (Enhancements)**
- [ ] Image editing (crop, rotate, filters)
- [ ] Outfit calendar (plan weekly outfits)
- [ ] Weather integration (suggest season-appropriate clothes)
- [ ] Social sharing (Instagram, Pinterest)
- [ ] Multi-language support

### **Phase 3 (AI Upgrades)**
- [ ] Fine-tune ResNet50 on fashion dataset (DeepFashion)
- [ ] GAN-based virtual try-on
- [ ] Body shape detection from selfie
- [ ] Personalized recommendations (collaborative filtering)
- [ ] Trend analysis from social media

---

## 🧪 Testing

### **Backend Tests** (Optional)
```bash
# API endpoint tests
npm test  # If test suite configured

# Manual testing with REST client
# Use VS Code REST Client extension with .rest files
```

### **ML Model Tests**
```python
# Test classifier
from ml_classifier import get_classifier
classifier = get_classifier()
result = classifier.predict(open('test_shirt.jpg', 'rb').read())
print(result)  # Should classify correctly

# Test color analyzer
from color_analyzer import get_color_analyzer
analyzer = get_color_analyzer()
colors = analyzer.extract_colors(open('test_red_dress.jpg', 'rb').read())
print(colors[0]['hex'])  # Should be close to red (#FF0000)
```

---

## 📊 Performance Optimization

### **Frontend**
- Code splitting with React lazy loading
- Image optimization (WebP format, lazy loading)
- TanStack Query caching (5-minute stale time)
- Service worker caching (offline assets)

### **Backend**
- MongoDB indexes on frequently queried fields
- Connection pooling (Mongoose default)
- Gzip compression for API responses
- TTL indexes for auto-cleanup

### **ML**
- Model lazy loading (load on first request, not startup)
- Batch inference for multiple images
- Cached feature embeddings (store in MongoDB)
- GPU acceleration (if available)

---

## 🔒 Security

- Firebase Auth tokens for API authentication
- CORS configured for frontend domain only
- MongoDB connection string in `.env` (never commit)
- Input validation with Zod schemas
- File upload size limits (5MB max)
- XSS protection via React (auto-escapes)
- HTTPS in production (Vercel default)

---

## 🚢 Deployment

### **Option 1: Vercel (Recommended)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Configure:
# - Add MONGODB_URI to environment variables
# - Add Firebase config to environment variables
# - Set Python runtime for /backend (serverless functions)
```

### **Option 2: Railway**
- Deploy Node.js app from GitHub
- Add Python worker for ML backend
- Configure environment variables
- Auto-deploy on git push

### **Option 3: Docker**
```dockerfile
# Multi-stage build
FROM node:20 AS frontend
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.10 AS ml
WORKDIR /ml
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .

FROM node:20
WORKDIR /app
COPY --from=frontend /app/dist ./dist
COPY --from=ml /ml ./backend
COPY package*.json ./
RUN npm install --production
EXPOSE 8000
CMD ["npm", "start"]
```

---

## 📝 License

MIT License - Free for personal and commercial use

---

## 👥 Credits

- **ResNet50**: Microsoft Research
- **Color Theory**: Adobe Color, Paletton
- **UI Components**: Shadcn/ui, Radix UI
- **Icons**: Lucide, React Icons

---

## 📞 Support

For issues or questions:
- GitHub Issues: [your-repo]/issues
- Email: your-email@example.com
- Discord: [your-community-link]

---

## 🎉 Getting Started Checklist

- [ ] Clone/create project structure
- [ ] Install Node.js dependencies (`npm install`)
- [ ] Set up Python virtual environment
- [ ] Install Python dependencies (`pip install -r requirements.txt`)
- [ ] Create MongoDB Atlas cluster
- [ ] Create Firebase project
- [ ] Configure `.env` file
- [ ] Update `firebase.ts` with your config
- [ ] Run `npm run dev` (Node backend)
- [ ] Run `python backend/main.py` (ML backend)
- [ ] Open http://localhost:8000
- [ ] Upload test images
- [ ] Generate first outfit! 🎊

---

**Total Development Time Estimate**: 80-120 hours for full implementation

**Tech Stack Summary**:
- Frontend: React + TypeScript + Vite + Tailwind
- Backend: Express + MongoDB + Mongoose
- ML: FastAPI + TensorFlow + scikit-learn
- Auth: Firebase Authentication
- Storage: Firebase Storage + MongoDB
- Deployment: Vercel / Railway / Docker

**Key Differentiators**:
1. True deep learning (ResNet50, not simple rules)
2. Scientific color theory (not random matching)
3. Persistent MongoDB storage (not just local)
4. PWA installable app (not just website)
5. Real-time ML inference (not pre-computed)

---

This prompt contains everything needed to rebuild Clazzy from scratch. Happy coding! 🚀👗✨
