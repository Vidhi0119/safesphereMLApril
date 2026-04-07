# Frontend Integration Setup Guide

This guide will help you integrate the SafeSphere ML API with your React frontend.

## Step 1: Install Required Dependencies

In your frontend project directory, install the charting library:

```bash
npm install recharts
```

Or if using yarn:

```bash
yarn add recharts
```

## Step 2: File Structure

Make sure your frontend has the following structure:

```
frontend/
├── src/
│   ├── components/
│   │   └── Dashboard.jsx          (Updated component)
│   ├── config/
│   │   └── api.js                  (API configuration)
│   ├── services/
│   │   └── safetyService.js        (API service functions)
│   └── utils/
│       ├── geolocation.js          (Location utilities)
│       └── colorUtils.js            (Color utilities)
```

## Step 3: Environment Variables

Create a `.env` file in your frontend root directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

Or update your existing `.env` file to include this variable.

## Step 4: Update FastAPI CORS Settings

The `app.py` file has been updated to include CORS middleware. If you're running your frontend on a different port, update the `allow_origins` list in `app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Default React port
        "http://localhost:5000",  # Alternative port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000"
    ],
    # ... rest of config
)
```

## Step 5: Start the Services

### Terminal 1: Start FastAPI Backend
```bash
cd SafeSphere-ml
python app.py
```

The API will run on `http://localhost:8000`

### Terminal 2: Start React Frontend
```bash
cd frontend
npm start
# or
yarn start
```

## Step 6: Test the Integration

1. Open your browser and navigate to your React app (usually `http://localhost:3000`)
2. The Dashboard will automatically:
   - Request your location permission
   - Fetch safety data from the API
   - Display the data in a bar chart
   - Update the safety score banner with color-coded values

## Features Implemented

### ✅ Automatic Location Detection
- Uses browser's Geolocation API
- Falls back to default Mumbai coordinates if permission denied

### ✅ Real-time Safety Data
- Fetches data from FastAPI on component mount
- Displays 10 nearest locations with safety scores

### ✅ Interactive Bar Chart
- Shows all 10 locations with their safety scores
- Color-coded bars (darker red = lower safety, lighter red = higher safety)
- Tooltips show full location names

### ✅ Dynamic Safety Score Display
- Banner color changes based on average safety score
- Percentage display (10-100%)
- Status text (Secure/Moderate/At Risk)

### ✅ Error Handling
- Shows error messages if API is unreachable
- Retry button to fetch data again
- Loading states during API calls

## API Endpoints Used

1. **GET** `/` - Health check
2. **POST** `/predict-safety` - Get safety prediction
   - Request: `{ latitude: number, longitude: number }`
   - Response: `{ locations: [...], average_safety_score: number, average_safety_percentage: number }`

## Troubleshooting

### Issue: CORS Error
**Solution**: Make sure the FastAPI server has CORS middleware enabled and your frontend URL is in the `allow_origins` list.

### Issue: Location Permission Denied
**Solution**: The app will automatically use default Mumbai coordinates. You can manually update coordinates in the code if needed.

### Issue: API Not Responding
**Solution**: 
1. Check if FastAPI server is running on port 8000
2. Verify the API URL in `frontend/src/config/api.js`
3. Check browser console for detailed error messages

### Issue: Chart Not Displaying
**Solution**: 
1. Ensure `recharts` is installed: `npm install recharts`
2. Check browser console for errors
3. Verify data is being received from the API

## Color Scheme

The safety scores use a red gradient:
- **Score 1-2**: Dark red (#8B0000) - Very unsafe
- **Score 3-4**: Medium-dark red - Unsafe
- **Score 5-6**: Medium red - Moderate
- **Score 7-8**: Light red - Safe
- **Score 9-10**: Very light red (#FFE5E5) - Very safe

## Next Steps

You can extend this integration by:
- Adding a map visualization with markers
- Implementing real-time location tracking
- Adding filters for location types
- Creating detailed location information modals
- Adding export functionality for safety reports

