# NETRA Frontend

AI-Powered Digital Footprint & Security Assessment Platform - Frontend

## Prerequisites

- Node.js 18 or higher
- npm or yarn

## Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
   
   The default API URL is `http://localhost:8000`

## Running the Development Server

```bash
npm run dev
```

The application will be available at: `http://localhost:3000`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API service layer
│   ├── utils/          # Utility functions
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
├── vite.config.js      # Vite configuration
├── tailwind.config.js  # Tailwind CSS configuration
└── package.json        # Dependencies
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Technology Stack

- React 18
- Vite
- React Router
- Tailwind CSS
- Axios
- Recharts (for charts)
- Framer Motion (for animations)

## Development Notes

- The frontend communicates with the backend via REST API
- All API calls go through the services layer
- State management uses React hooks
- Responsive design with Tailwind CSS
- Dark theme by default

## API Integration

The frontend is configured to proxy API requests to the backend:

```javascript
// In vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

## Troubleshooting

**Node.js not found:**
- Download and install Node.js 18 from nodejs.org

**Port already in use:**
- Change port in `vite.config.js` or kill the process using port 3000

**API connection errors:**
- Ensure backend is running on port 8000
- Check API URL in `.env` file
