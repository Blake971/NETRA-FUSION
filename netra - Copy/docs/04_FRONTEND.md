# NETRA
# Frontend Specification

Version: 2.0

---

# 1. Frontend Technology Stack

- React 18+
- Tailwind CSS
- React Router v6
- Axios
- Recharts
- Framer Motion (animations)

---

# 2. Design System

## 2.1 Color Palette

### Primary Colors
- Background: #0f172a (Slate 900)
- Surface: #1e293b (Slate 800)
- Surface Light: #334155 (Slate 700)
- Primary: #06b6d4 (Cyan 500)
- Primary Hover: #0891b2 (Cyan 600)
- Text Primary: #f8fafc (Slate 50)
- Text Secondary: #94a3b8 (Slate 400)

### Status Colors
- Success: #10b981 (Emerald 500)
- Warning: #f59e0b (Amber 500)
- Error: #ef4444 (Red 500)
- Critical: #dc2626 (Red 600)

## 2.2 Typography

- Font Family: Inter, system-ui, sans-serif
- Headings: Bold, 600-700 weight
- Body: Regular, 400 weight
- Code: Monospace, 500 weight

## 2.3 Spacing

- XS: 0.25rem (4px)
- SM: 0.5rem (8px)
- MD: 1rem (16px)
- LG: 1.5rem (24px)
- XL: 2rem (32px)
- 2XL: 3rem (48px)

## 2.4 Border Radius

- SM: 0.375rem (6px)
- MD: 0.5rem (8px)
- LG: 0.75rem (12px)
- XL: 1rem (16px)
- Full: 9999px

## 2.5 Shadows

- SM: 0 1px 2px 0 rgb(0 0 0 / 0.05)
- MD: 0 4px 6px -1px rgb(0 0 0 / 0.1)
- LG: 0 10px 15px -3px rgb(0 0 0 / 0.1)
- XL: 0 20px 25px -5px rgb(0 0 0 / 0.1)

---

# 3. Page Specifications

## 3.1 Landing Page

### Route
/

### Components
- Navbar
- Hero Section
- Features Grid
- How It Works
- CTA Section
- Footer

### Navbar
**Props**: None
**State**: None
**Actions**: Navigate to Dashboard, Navigate to Login

**Elements**:
- Logo (NETRA)
- Navigation Links: Features, About, Contact
- CTA Button: "Get Started" → /dashboard

### Hero Section
**Props**: None
**State**: None
**Actions**: None

**Elements**:
- Headline: "AI-Powered Security Assessment"
- Subheadline: "Analyze domains, detect vulnerabilities, and generate professional reports"
- Input: Domain search field
- Button: "Scan Now"
- Background: Animated gradient or cybersecurity pattern

### Features Grid
**Props**: None
**State**: None
**Actions**: None

**Elements**:
- Card 1: WHOIS Analysis
- Card 2: DNS Configuration
- Card 3: SSL Validation
- Card 4: Security Headers
- Card 5: Email Security
- Card 6: AI Reports

### Footer
**Props**: None
**State**: None
**Actions**: None

**Elements**:
- Logo
- Links: About, Privacy, Terms
- Copyright

### API Called
None

### State Management
None

### Loading State
None

### Empty State
None

### Error State
None

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation

### Responsive Layout
- Desktop: Full width
- Tablet: Stacked
- Mobile: Stacked, simplified

### Animation
- Hero fade-in
- Card hover effects

---

## 3.2 Dashboard

### Route
/dashboard

### Components
- Sidebar Navigation
- Top Bar
- Risk Score Card
- Recent Scans Table
- Quick Actions
- Stats Overview

### Sidebar Navigation
**Props**: None
**State**: Active page
**Actions**: Navigate to pages

**Elements**:
- Logo
- Nav Items:
  - Dashboard (active)
  - Domain Scan
  - Digital Footprint
  - Google Dork
  - Reports
  - History
  - Settings

### Top Bar
**Props**: User info
**State**: None
**Actions**: Logout, Notifications

**Elements**:
- Search input
- Notification bell
- User avatar
- User dropdown

### Risk Score Card
**Props**: Latest scan data
**State**: Loading, Error, Success
**Actions**: View details, Download report

**Elements**:
- Risk score gauge (0-100)
- Risk level badge (Low/Medium/High/Critical)
- Last scan timestamp
- View details button
- Download report button

### Recent Scans Table
**Props**: Scan history array
**State**: Loading, Error, Empty
**Actions**: View scan, Delete scan, Compare scans

**Elements**:
- Table headers: Domain, Risk Score, Date, Status, Actions
- Table rows: Scan data
- Pagination
- Filter input
- Sort controls

### Quick Actions
**Props**: None
**State**: None
**Actions**: Navigate to pages

**Elements**:
- Button: "New Domain Scan"
- Button: "Digital Footprint"
- Button: "Google Dork Assistant"

### Stats Overview
**Props**: Statistics
**State**: Loading, Error
**Actions**: None

**Elements**:
- Total scans
- High risk domains
- Average risk score
- Scans this week

### API Endpoints
- GET /history
- GET /stats

### State Management
- React hooks (useState, useEffect)
- Context for user data

### Loading State
- Skeleton loaders for cards
- Skeleton table rows
- Loading spinner for stats

### Failure State
- Error message with retry button
- Empty state illustration

### Responsive Layout
- Desktop: Sidebar + Main content
- Tablet: Collapsible sidebar
- Mobile: Bottom navigation, hidden sidebar

### Animation
- Card fade-in
- Table row hover
- Button press effect

---

## 3.3 Domain Scan Page

### Route
/scan

### Components
- Scan Input Form
- Scan Progress
- Scan Results Dashboard

### Scan Input Form
**Props**: None
**State**: Input value, Validation status
**Actions**: Submit scan, Clear input

**Elements**:
- Domain input field
- Validation message
- Scan button
- Advanced options toggle
  - Include subdomain discovery
  - Include email security
  - Include CT logs

### Scan Progress
**Props**: Scan status
**State**: Progress percentage, Current module
**Actions**: Cancel scan

**Elements**:
- Progress bar
- Module status list:
  - WHOIS: Pending/Running/Complete/Failed
  - DNS: Pending/Running/Complete/Failed
  - SSL: Pending/Running/Complete/Failed
  - Headers: Pending/Running/Complete/Failed
  - Email: Pending/Running/Complete/Failed
  - IP: Pending/Running/Complete/Failed
- Cancel button

### Scan Results Dashboard
**Props**: Scan results JSON
**State**: Loading, Error, Success
**Actions**: Download PDF, Save to history, Share

**Elements**:
- Risk score card
- AI Summary card
- WHOIS section
- DNS section
- SSL section
- Headers section
- Email section
- IP section
- CT logs section
- Recommendations list
- Download PDF button
- Save button

### API Endpoints
- POST /scan
- GET /scan/{id}

### State Management
- React hooks
- Scan context for progress updates

### Loading State
- Progress bar animation
- Module status indicators

### Empty State
- "Enter a domain to begin scanning"

### Error State
- Error message with specific reason
- Retry button
- Back to input button

### Responsive Layout
- Desktop: Full width results
- Tablet: Stacked sections
- Mobile: Accordion sections

### Animation
- Progress bar fill
- Module status transitions
- Result card fade-in

---

## 3.4 Digital Footprint Page

### Route
/footprint

### Components
- Search Form
- Footprint Results

### Search Form
**Props**: None
**State**: Input values (name, email, domain)
**Actions**: Submit search, Clear form

**Elements**:
- Name input (optional)
- Email input (optional)
- Domain input (optional)
- At least one required validation
- Search button

### Footprint Results
**Props**: Footprint data
**State**: Loading, Error, Success
**Actions**: Export results, Save to history

**Elements**:
- Exposure score card
- Visibility level
- Found items:
  - Public websites
  - GitHub repositories
  - News mentions
  - Public profiles
  - Social media links
- Export button
- Save button

### API Endpoints
- POST /footprint

### State Management
- React hooks

### Loading State
- Skeleton cards
- Loading spinner

### Empty State
- "Enter information to search digital footprint"

### Error State
- Error message
- Retry button

### Responsive Layout
- Desktop: Grid layout
- Tablet: Stacked
- Mobile: Stacked

### Animation
- Card fade-in
- Score gauge animation

---

## 3.5 Google Dork Assistant Page

### Route
/dork

### Components
- Domain Input
- Generated Queries

### Domain Input
**Props**: None
**State**: Input value
**Actions**: Generate queries, Clear input

**Elements**:
- Domain input field
- Generate button
- Query type checkboxes:
  - File search
  - Login pages
  - Directory listings
  - GitHub
  - Pastebin

### Generated Queries
**Props**: Queries array
**State**: Loading, Error, Success
**Actions**: Copy query, Open in Google, Export all

**Elements**:
- Query list with:
  - Query string
  - Description
  - Purpose
  - Copy button
  - Open button
- Export all button

### API Endpoints
- POST /dork

### State Management
- React hooks

### Loading State
- Loading spinner
- Skeleton query cards

### Empty State
- "Enter a domain to generate Google dork queries"

### Error State
- Error message
- Retry button

### Responsive Layout
- Desktop: List view
- Tablet: List view
- Mobile: Stacked cards

### Animation
- Card fade-in
- Copy success animation

---

## 3.6 Reports Page

### Route
/reports

### Components
- Reports List
- Report Viewer

### Reports List
**Props**: Reports array
**State**: Loading, Error, Empty
**Actions**: View report, Download report, Delete report

**Elements**:
- Table headers: Domain, Date, Risk Score, Actions
- Table rows: Report data
- Filter by date
- Filter by risk level
- Search input

### Report Viewer
**Props**: Report data
**State**: Loading, Error
**Actions**: Download PDF, Share, Print

**Elements**:
- PDF preview
- Download button
- Share button
- Print button
- Back button

### API Endpoints
- GET /reports
- GET /report/{id}
- POST /generate-report

### State Management
- React hooks

### Loading State
- Skeleton table rows
- Loading spinner for PDF

### Empty State
- "No reports generated yet"

### Error State
- Error message
- Retry button

### Responsive Layout
- Desktop: Table + Preview
- Tablet: Stacked
- Mobile: List only, preview in modal

### Animation
- Table row hover
- Modal fade-in

---

## 3.7 Scan History Page

### Route
/history

### Components
- History Table
- Scan Details Modal

### History Table
**Props**: History array
**State**: Loading, Error, Empty
**Actions**: View details, Delete scan, Compare scans

**Elements**:
- Table headers: Domain, Date, Risk Score, Status, Actions
- Table rows: Scan data
- Pagination
- Filter by date range
- Filter by risk level
- Search input
- Sort controls

### Scan Details Modal
**Props**: Scan data
**State**: Loading, Error
**Actions**: Close, Download report, Re-scan

**Elements**:
- Modal header
- Scan summary
- Risk score
- Module results
- AI summary
- Close button
- Download button
- Re-scan button

### API Endpoints
- GET /history
- GET /scan/{id}
- DELETE /scan/{id}

### State Management
- React hooks
- Modal state

### Loading State
- Skeleton table rows
- Loading spinner in modal

### Empty State
- "No scan history yet"

### Error State
- Error message
- Retry button

### Responsive Layout
- Desktop: Full table
- Tablet: Stacked cards
- Mobile: Simplified table

### Animation
- Modal fade-in
- Table row hover

---

## 3.8 Settings Page

### Route
/settings

### Components
- Settings Form

### Settings Form
**Props**: User settings
**State**: Form values, Save status
**Actions**: Save settings, Reset to defaults

**Elements**:
- Section: General
  - Theme toggle (Dark/Light)
  - Language selector
  - Timezone selector

- Section: Notifications
  - Email notifications toggle
  - Scan completion notifications toggle
  - High risk alerts toggle

- Section: API
  - API key display
  - Regenerate API key button

- Section: Data
  - Export all data button
  - Delete all data button (with confirmation)

- Save button
- Reset button

### API Endpoints
- GET /settings
- PUT /settings
- DELETE /data

### State Management
- React hooks
- Form state

### Loading State
- Save button loading state

### Empty State
None

### Error State
- Error message
- Retry button

### Responsive Layout
- Desktop: Two-column form
- Tablet: Stacked
- Mobile: Stacked

### Animation
- Button press effect
- Toggle switch animation

---

# 4. Shared Components

## 4.1 Button

**Props**:
- variant: primary, secondary, danger, ghost
- size: sm, md, lg
- disabled: boolean
- loading: boolean
- icon: ReactNode

**State**: None
**Actions**: onClick

**Elements**:
- Button element
- Icon (if provided)
- Loading spinner (if loading)
- Text

## 4.2 Card

**Props**:
- title: string
- children: ReactNode
- hoverable: boolean

**State**: None
**Actions**: None

**Elements**:
- Card container
- Title (if provided)
- Content

## 4.3 Modal

**Props**:
- isOpen: boolean
- onClose: function
- title: string
- children: ReactNode

**State**: None
**Actions**: onClose

**Elements**:
- Overlay
- Modal container
- Header with close button
- Content
- Footer (if provided)

## 4.4 Loading Spinner

**Props**:
- size: sm, md, lg

**State**: None
**Actions**: None

**Elements**:
- Spinner animation

## 4.5 Status Badge

**Props**:
- status: success, warning, error, critical, info
- text: string

**State**: None
**Actions**: None

**Elements**:
- Badge with color based on status
- Text

## 4.6 Risk Gauge

**Props**:
- score: number (0-100)
- size: sm, md, lg

**State**: None
**Actions**: None

**Elements**:
- Gauge chart
- Score display
- Risk level label

---

# 5. State Management

## 5.1 Global State (Context)

### UserContext
- User data
- Authentication status
- Settings

### ScanContext
- Current scan
- Scan history
- Scan status

### ThemeContext
- Current theme
- Theme toggle function

## 5.2 Local State

- Component-specific state using useState
- Form state
- Modal open/close state
- Loading states

---

# 6. API Integration

## 6.1 Axios Configuration

- Base URL from environment variable
- Request interceptors for auth
- Response interceptors for error handling
- Timeout configuration

## 6.2 Error Handling

- Network errors
- 4xx errors
- 5xx errors
- Timeout errors
- User-friendly error messages

## 6.3 Retry Logic

- Automatic retry for failed requests
- Exponential backoff
- Max retry attempts

---

# 7. Performance

## 7.1 Code Splitting

- React.lazy for route-based splitting
- Dynamic imports for heavy components

## 7.2 Caching

- API response caching
- Local storage for user settings
- Session storage for temporary data

## 7.3 Optimization

- Memoization with React.memo
- useCallback for event handlers
- useMemo for expensive calculations

---

# 8. Accessibility

## 8.1 Keyboard Navigation

- Tab order
- Focus indicators
- Keyboard shortcuts

## 8.2 Screen Reader Support

- ARIA labels
- Alt text for images
- Semantic HTML

## 8.3 Color Contrast

- WCAG AA compliance
- Sufficient contrast ratios

---

# 9. Responsive Design

## 9.1 Breakpoints

- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## 9.2 Layout Adaptation

- Flexible grids
- Stacking on mobile
- Hidden elements on small screens

---

# 10. Animations

## 10.1 Framer Motion

- Page transitions
- Modal animations
- Card hover effects
- Loading animations

## 10.2 CSS Animations

- Spinner animations
- Pulse effects
- Fade transitions

---

END OF FRONTEND SPECIFICATION
