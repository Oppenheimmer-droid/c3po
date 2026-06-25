# C3PO Frontend Development Skill

## Purpose
Guide frontend development and debugging for the C3PO Next.js application.

## Triggers
Use this skill when the user mentions:
- "frontend development"
- "add component"
- "fix frontend bug"
- "add page"
- "style issue"
- "test frontend"

## Project Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx           # Home page
│   │   ├── layout.tsx         # Root layout
│   │   ├── auth/              # Auth pages
│   │   ├── chat/              # Chat pages
│   │   ├── dashboard/         # Dashboard pages
│   │   ├── documents/         # Document management
│   │   └── evaluations/       # Evaluation pages
│   ├── components/            # Reusable components
│   ├── lib/
│   │   ├── api.ts            # API client
│   │   ├── store.ts          # Zustand store
│   │   └── utils.ts          # Utilities
│   ├── services/             # API service modules
│   └── types/                # TypeScript types
├── package.json
├── tailwind.config.ts
└── next.config.js
```

## Common Tasks

### Install Dependencies
```bash
cd /workspace/project/c3po/frontend
npm install
```

### Run Development Server
```bash
cd /workspace/project/c3po/frontend
npm run dev
```

### Build for Production
```bash
cd /workspace/project/c3po/frontend
npm run build
npm start
```

### Lint Code
```bash
cd /workspace/project/c3po/frontend
npm run lint
```

### Run Tests
```bash
cd /workspace/project/c3po/frontend
npm test
```

## Adding New Pages

1. Create route file in `src/app/[route]/page.tsx`
2. Use TypeScript and React patterns
3. Import components from `../components/`
4. Use API services from `./services/`

## Adding Components

1. Create file in `src/components/`
2. Follow naming convention: `ComponentName.tsx`
3. Use Tailwind CSS for styling
4. Export as default or named export

## API Integration

### Using API Service
```typescript
import { chatService } from '@/services';

// In component
const response = await chatService.sendMessage(message);
```

### Adding New API Service
1. Create file in `src/services/[service].service.ts`
2. Use Axios instance from `@/lib/api`
3. Export typed functions

## Environment Variables
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## UI Library
Uses Radix UI primitives for accessibility:
- `@radix-ui/react-dialog`
- `@radix-ui/react-dropdown-menu`
- `@radix-ui/react-tabs`
- `@radix-ui/react-toast`

## Styling
- Tailwind CSS for utility classes
- CSS variables in `globals.css`
- Component-scoped styles when needed

## Common Issues

### Port Already in Use
```bash
# Find and kill process
lsof -i :3000
kill -9 <PID>
```

### Module Not Found
- Check import paths
- Verify `tsconfig.json` paths configuration
- Run `npm install` again

### Build Errors
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

### API Connection Error
- Verify backend is running: `curl http://localhost:8000/health`
- Check NEXT_PUBLIC_API_URL in .env
- Check CORS settings in backend
