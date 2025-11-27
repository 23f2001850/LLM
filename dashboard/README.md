# LLM Analysis Quiz Bot - Dashboard

Modern, responsive dashboard for monitoring and managing the quiz bot.

## Features

- **Real-time Monitoring**: Live logs and quiz history
- **Dark/Light Theme**: Automatic theme switching with preference persistence
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Statistics Dashboard**: Visual stats for success rate, timing, and performance
- **Quiz Submission**: Direct quiz submission interface
- **History Tracking**: Complete history of all quiz attempts

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- TailwindCSS
- Axios

## Development

### Prerequisites

- Node.js 20+
- npm or yarn

### Setup

1. Install dependencies:
```bash
npm install
```

2. Set environment variables:
Create `.env.local`:
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
```

4. Open browser:
```
http://localhost:3000
```

## Production Build

```bash
npm run build
npm start
```

## Docker Deployment

### Build

```bash
docker build -t quiz-bot-dashboard .
```

### Run

```bash
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_BACKEND_URL=http://backend:8000 \
  quiz-bot-dashboard
```

## Features Detail

### Stats Cards
- Total quizzes processed
- Success count
- Failure count
- Average processing time

### Quiz Submission Form
- Email input
- Secret key authentication
- Quiz URL
- Real-time validation
- Loading states

### History List
- Chronological quiz history
- Status indicators
- Time tracking
- Error details
- Refresh capability

### Live Logs
- Real-time log streaming
- Timestamp tracking
- Auto-scroll
- Console-style display

### Theme Toggle
- Light/Dark mode
- System preference detection
- Local storage persistence
- Smooth transitions

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_BACKEND_URL` | Backend API URL | `http://localhost:8000` |

## Project Structure

```
dashboard/
├── app/
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Home page
├── components/
│   ├── Header.tsx       # Header with status
│   ├── StatsCards.tsx   # Statistics display
│   ├── QuizForm.tsx     # Quiz submission form
│   ├── HistoryList.tsx  # Quiz history
│   ├── LiveLogs.tsx     # Log viewer
│   └── ThemeProvider.tsx # Theme management
├── public/              # Static assets
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── Dockerfile
```

## Customization

### Colors

Edit `tailwind.config.js` to customize color scheme:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      }
    }
  }
}
```

### Components

All components are in `components/` directory and are fully customizable.

## License

MIT License - See root LICENSE file
