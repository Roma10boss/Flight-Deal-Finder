# Weekend Flight Deal Finder

A web-based application that automatically scrapes the internet to find cheap flight deals for weekend getaways. Get notified when prices drop below historical averages!

![Flight Deal Finder Screenshot](screenshot.png)

## Features

- 🔍 **Automated Flight Searching**: Automatically searches for flights from your home airport to multiple destinations
- 📊 **Price History Tracking**: Tracks historical prices and identifies deals when prices drop below average
- 📧 **Email Notifications**: Get notified when exceptional deals are found
- 📅 **Weekend-focused**: Specifically searches for Friday-to-Sunday/Monday trips
- 🖥️ **Web Dashboard**: Beautiful interface to view deals, configure settings, and analyze trends
- 📈 **Price Charts**: Visualize price trends over time for different routes
- ⚙️ **Customizable**: Set your home airport, destinations, price limits, and more

## Project Structure

```
weekend-flight-deal-finder/
│
├── server.js              # Express backend server
├── public/               
│   └── index.html        # Frontend website (single file)
├── data/                 # Data storage directory
│   ├── deals.json        # Current flight deals
│   ├── price-history.json # Historical price data
│   └── config.json       # User configuration
├── package.json          # Project dependencies
└── README.md            # Documentation (this file)
```

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/weekend-flight-deal-finder.git
cd weekend-flight-deal-finder
```

### 2. Install dependencies
```bash
npm install
```

### 3. Create required directories
```bash
mkdir data public
```

### 4. Move files to proper locations
- Copy the HTML website to `public/index.html`
- Ensure `server.js` is in the root directory

## Configuration

### Initial Setup

1. Start the server:
   ```bash
   npm start
   ```

2. Open your browser and go to `http://localhost:3000`

3. Click on the "Settings" tab to configure:
   - **Home Airport**: Your departure airport code (e.g., LAX, JFK)
   - **Maximum Price**: Your budget limit
   - **Destinations**: Choose which cities you want to visit
   - **Email**: Enter your email to receive deal notifications

### Email Configuration

To enable email notifications, edit `server.js` and update the email transporter settings:

```javascript
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: 'your-email@gmail.com',    // Your email
        pass: 'your-app-password'        // Your app password
    }
});
```

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the app password instead of your regular password

## Usage

### Starting the Server
```bash
npm start
```
The application will be available at `http://localhost:3000`

### Development Mode (with auto-restart)
```bash
npm run dev
```

### How It Works

1. **Scheduled Searches**: The server automatically searches for flights every day at 6 AM
2. **Deal Detection**: Compares current prices with historical averages
3. **Notifications**: Sends emails when prices drop significantly below average
4. **Web Interface**: Access the dashboard to view deals, adjust settings, and see trends

## API Integration (Important!)

The current implementation uses simulated flight data for demonstration purposes. To make this work with real flight data, you'll need to integrate with a flight search API. Some options:

### 1. Skyscanner API
- Sign up at [RapidAPI](https://rapidapi.com/skyscanner/api/skyscanner-flight-search)
- Replace the `simulateFlightResults` function with actual API calls

### 2. Amadeus API
- Get API keys from [Amadeus for Developers](https://developers.amadeus.com)
- Implement flight search using their SDK

### 3. Kiwi.com API
- Register at [Kiwi.com Partners](https://partners.kiwi.com)
- Use their Tequila API for flight searches

### 4. Web Scraping
- Use Puppeteer or Playwright for browser automation
- Scrape flight search websites (check their terms of service)

### Example API Integration

```javascript
async function searchFlights(from, to, departDate, returnDate) {
    // Example with Skyscanner API
    const options = {
        method: 'GET',
        url: 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/' + 
             `${from}/${to}/${departDate}/${returnDate}`,
        headers: {
            'X-RapidAPI-Key': 'YOUR-API-KEY',
            'X-RapidAPI-Host': 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com'
        }
    };
    
    const response = await axios.request(options);
    // Process and return flight data
}
```

## API Endpoints

The server provides these API endpoints:

- `GET /api/deals` - Get current flight deals
- `POST /api/refresh` - Manually refresh flight deals
- `GET /api/price-history` - Get historical price data
- `GET /api/config` - Get saved configuration
- `POST /api/config` - Save configuration

## Customization

### Adding New Destinations

1. Through the UI: Use the "Add Destination" feature in Settings
2. Programmatically: Update the `destinations` array in the config

### Changing Search Criteria

Modify the configuration object:
```javascript
{
    baseAirport: "LAX",
    maxPrice: 300,
    maxFlightTime: 5,       // hours
    destinations: ["NYC", "MIA", "LAS"],
    tripDuration: { min: 2, max: 3 },
    lookAheadWeeks: 12,
    emailNotification: {
        enabled: true,
        email: "your-email@example.com",
        dealThreshold: 0.7  // 30% below average
    }
}
```

### Styling the Website

The website uses inline CSS for simplicity. To customize the appearance:
1. Edit the `<style>` section in `public/index.html`
2. Modify CSS variables for quick theme changes:
   ```css
   :root {
       --primary-color: #3498db;
       --secondary-color: #2980b9;
       --accent-color: #e74c3c;
   }
   ```

## Deployment

### Deploy to Heroku

1. Install Heroku CLI and login
2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

3. Set environment variables:
   ```bash
   heroku config:set NODE_ENV=production
   ```

4. Deploy:
   ```bash
   git push heroku main
   ```

### Deploy to AWS/DigitalOcean

1. Set up a VPS with Node.js installed
2. Clone the repository
3. Install dependencies and PM2:
   ```bash
   npm install
   npm install -g pm2
   ```

4. Start with PM2:
   ```bash
   pm2 start server.js --name flight-deals
   pm2 save
   ```

## Troubleshooting

### Common Issues

1. **No deals found**
   - Check your configuration settings
   - Ensure destinations are properly formatted (3-letter codes)
   - Verify the data directory has write permissions

2. **Email notifications not working**
   - Verify email configuration in server.js
   - Check spam folder
   - Ensure app passwords are set up correctly

3. **Price history not updating**
   - Check if data/price-history.json has write permissions
   - Look for errors in the console logs

### Debugging

Enable debug logging:
```javascript
// Add to server.js
const DEBUG = true;

function log(...args) {
    if (DEBUG) console.log(...args);
}
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Future Enhancements

- [ ] Real flight API integration
- [ ] Mobile app companion
- [ ] Price prediction using ML
- [ ] Multi-city trip support
- [ ] Calendar integration
- [ ] Social sharing features
- [ ] User accounts and preferences
- [ ] Advanced filtering options
- [ ] Price alerts via SMS/WhatsApp

## License

This project is licensed under the ISC License.

## Disclaimer

This tool is for educational purposes. Always verify flight information and prices directly with airlines or travel agencies before booking. Be respectful of website terms of service when implementing web scraping.

## Support

If you have questions or need help:

Contat me