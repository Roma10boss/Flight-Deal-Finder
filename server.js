// Complete Flight Deal Finder Server
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const axios = require('axios');
const cron = require('node-cron');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Data directories
const DATA_DIR = path.join(__dirname, 'data');
const DEALS_FILE = path.join(DATA_DIR, 'deals.json');
const HISTORY_FILE = path.join(DATA_DIR, 'price-history.json');
const SETTINGS_FILE = path.join(DATA_DIR, 'settings.json');

// In-memory data store
let currentDeals = [];
let priceHistory = {};
let settings = {
    baseAirport: 'LAX',
    maxPrice: 300,
    maxFlightTime: 5,
    destinations: ['JFK', 'MIA', 'ORD', 'BOS', 'SEA', 'SFO', 'LAS'],
    lookAheadWeeks: 12,
    email: '',
    emailEnabled: false,
    dealThreshold: 0.7
};

// API Integration Configuration
const API_CONFIG = {
    // Amadeus API (Primary)
    amadeus: {
        enabled: process.env.AMADEUS_CLIENT_ID && process.env.AMADEUS_CLIENT_SECRET,
        clientId: process.env.AMADEUS_CLIENT_ID,
        clientSecret: process.env.AMADEUS_CLIENT_SECRET,
        baseUrl: 'https://api.amadeus.com/v2'
    },
    // Skyscanner API (Backup)
    skyscanner: {
        enabled: process.env.SKYSCANNER_API_KEY,
        apiKey: process.env.SKYSCANNER_API_KEY,
        baseUrl: 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices'
    },
    // Kiwi.com API (Backup)
    kiwi: {
        enabled: process.env.KIWI_API_KEY,
        apiKey: process.env.KIWI_API_KEY,
        baseUrl: 'https://api.tequila.kiwi.com/v2'
    }
};

// Initialize data directory
async function initDataDirectory() {
    try {
        await fs.mkdir(DATA_DIR, { recursive: true });
        
        // Load existing data
        try {
            const dealsData = await fs.readFile(DEALS_FILE, 'utf8');
            currentDeals = JSON.parse(dealsData);
        } catch (err) {
            console.log('No existing deals found');
        }
        
        try {
            const historyData = await fs.readFile(HISTORY_FILE, 'utf8');
            priceHistory = JSON.parse(historyData);
        } catch (err) {
            console.log('No price history found');
        }
        
        try {
            const settingsData = await fs.readFile(SETTINGS_FILE, 'utf8');
            settings = { ...settings, ...JSON.parse(settingsData) };
        } catch (err) {
            console.log('No settings found, using defaults');
        }
    } catch (error) {
        console.error('Error initializing data directory:', error);
    }
}

// Save data to files
async function saveData() {
    try {
        await fs.writeFile(DEALS_FILE, JSON.stringify(currentDeals, null, 2));
        await fs.writeFile(HISTORY_FILE, JSON.stringify(priceHistory, null, 2));
        await fs.writeFile(SETTINGS_FILE, JSON.stringify(settings, null, 2));
    } catch (error) {
        console.error('Error saving data:', error);
    }
}

// Amadeus API Authentication
let amadeusToken = null;
let amadeusTokenExpiry = null;

async function getAmadeusToken() {
    if (amadeusToken && amadeusTokenExpiry && Date.now() < amadeusTokenExpiry) {
        return amadeusToken;
    }

    try {
        const response = await axios.post('https://api.amadeus.com/v1/security/oauth2/token', 
            `grant_type=client_credentials&client_id=${API_CONFIG.amadeus.clientId}&client_secret=${API_CONFIG.amadeus.clientSecret}`,
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }
        );

        amadeusToken = response.data.access_token;
        amadeusTokenExpiry = Date.now() + (response.data.expires_in * 1000) - 60000; // Refresh 1 minute early
        return amadeusToken;
    } catch (error) {
        console.error('Error getting Amadeus token:', error);
        throw error;
    }
}

// Search flights using Amadeus API
async function searchAmadeusFlights(from, to, departDate, returnDate) {
    if (!API_CONFIG.amadeus.enabled) return null;

    try {
        const token = await getAmadeusToken();
        const response = await axios.get(`${API_CONFIG.amadeus.baseUrl}/shopping/flight-offers`, {
            headers: {
                'Authorization': `Bearer ${token}`
            },
            params: {
                originLocationCode: from,
                destinationLocationCode: to,
                departureDate: departDate,
                returnDate: returnDate,
                adults: 1,
                currencyCode: 'USD',
                max: 10
            }
        });

        return response.data.data.map(offer => ({
            id: offer.id,
            airline: offer.validatingAirlineCodes[0],
            flight: `${offer.itineraries[0].segments[0].carrierCode}${offer.itineraries[0].segments[0].number}`,
            from: from,
            to: to,
            departDate: departDate,
            departTime: offer.itineraries[0].segments[0].departure.at.split('T')[1].substring(0, 5),
            returnDate: returnDate,
            returnTime: offer.itineraries[1].segments[0].arrival.at.split('T')[1].substring(0, 5),
            price: parseFloat(offer.price.total),
            duration: parseDuration(offer.itineraries[0].duration),
            url: `https://www.amadeus.com/flights/${from}/${to}`
        }));
    } catch (error) {
        console.error('Amadeus API error:', error);
        return null;
    }
}

// Search flights using Skyscanner API
async function searchSkyscannerFlights(from, to, departDate, returnDate) {
    if (!API_CONFIG.skyscanner.enabled) return null;

    try {
        const response = await axios.get(
            `${API_CONFIG.skyscanner.baseUrl}/browsequotes/v1.0/US/USD/en-US/${from}/${to}/${departDate}`,
            {
                headers: {
                    'X-RapidAPI-Key': API_CONFIG.skyscanner.apiKey,
                    'X-RapidAPI-Host': 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com'
                },
                params: {
                    inboundpartialdate: returnDate
                }
            }
        );

        return response.data.Quotes.map(quote => ({
            id: quote.QuoteId,
            airline: quote.OutboundLeg.CarrierIds[0],
            flight: `${quote.OutboundLeg.CarrierIds[0]}${Math.floor(Math.random() * 1000) + 100}`,
            from: from,
            to: to,
            departDate: departDate,
            departTime: '08:00', // Skyscanner doesn't provide specific times in browse quotes
            returnDate: returnDate,
            returnTime: '18:00',
            price: quote.MinPrice,
            duration: 300, // Estimated
            url: `https://www.skyscanner.com/transport/flights/${from}/${to}/${departDate}/${returnDate}`
        }));
    } catch (error) {
        console.error('Skyscanner API error:', error);
        return null;
    }
}

// Search flights using Kiwi API
async function searchKiwiFlights(from, to, departDate, returnDate) {
    if (!API_CONFIG.kiwi.enabled) return null;

    try {
        const response = await axios.get(`${API_CONFIG.kiwi.baseUrl}/search`, {
            headers: {
                'apikey': API_CONFIG.kiwi.apiKey
            },
            params: {
                fly_from: from,
                fly_to: to,
                date_from: departDate,
                date_to: departDate,
                return_from: returnDate,
                return_to: returnDate,
                flight_type: 'round',
                adults: 1,
                curr: 'USD',
                max_stopovers: 1,
                limit: 10
            }
        });

        return response.data.data.map(flight => ({
            id: flight.id,
            airline: flight.airlines[0],
            flight: `${flight.airlines[0]}${flight.route[0].flight_no}`,
            from: from,
            to: to,
            departDate: departDate,
            departTime: new Date(flight.dTime * 1000).toTimeString().substring(0, 5),
            returnDate: returnDate,
            returnTime: new Date(flight.route[flight.route.length - 1].aTime * 1000).toTimeString().substring(0, 5),
            price: flight.price,
            duration: flight.duration.departure / 60, // Convert to minutes
            url: flight.deep_link
        }));
    } catch (error) {
        console.error('Kiwi API error:', error);
        return null;
    }
}

// Fallback: Generate simulated flight data
function generateSimulatedFlights(from, to, departDate, returnDate) {
    const airlines = ['United', 'American', 'Delta', 'Southwest', 'JetBlue', 'Alaska', 'Spirit'];
    const numFlights = Math.floor(Math.random() * 5) + 3;
    const flights = [];

    // Airline website mappings
    const airlineUrls = {
        'United': 'https://www.united.com',
        'American': 'https://www.aa.com',
        'Delta': 'https://www.delta.com',
        'Southwest': 'https://www.southwest.com',
        'JetBlue': 'https://www.jetblue.com',
        'Alaska': 'https://www.alaskaair.com',
        'Spirit': 'https://www.spirit.com'
    };

    for (let i = 0; i < numFlights; i++) {
        const airline = airlines[Math.floor(Math.random() * airlines.length)];
        const price = Math.floor(Math.random() * 300) + 100;
        const duration = Math.floor(Math.random() * 240) + 120;
        
        // Create a more realistic booking URL
        const baseUrl = airlineUrls[airline] || 'https://www.google.com/travel/flights';
        const bookingUrl = `${baseUrl}/flights?q=${from}%20to%20${to}`;

        flights.push({
            id: `${from}${to}${Date.now()}${i}`,
            airline: airline,
            flight: `${airline.substring(0, 2).toUpperCase()}${Math.floor(Math.random() * 900) + 100}`,
            from: from,
            to: to,
            departDate: departDate,
            departTime: `${String(Math.floor(Math.random() * 24)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
            returnDate: returnDate,
            returnTime: `${String(Math.floor(Math.random() * 24)).padStart(2, '0')}:${String(Math.floor(Math.random() * 60)).padStart(2, '0')}`,
            price: price,
            duration: duration,
            url: bookingUrl
        });
    }

    return flights;
}

// Main flight search function
async function searchFlights(from, to, departDate, returnDate) {
    // Try APIs in order of preference
    let results = null;

    // Try Amadeus first
    if (API_CONFIG.amadeus.enabled) {
        results = await searchAmadeusFlights(from, to, departDate, returnDate);
    }

    // Try Skyscanner if Amadeus fails
    if (!results && API_CONFIG.skyscanner.enabled) {
        results = await searchSkyscannerFlights(from, to, departDate, returnDate);
    }

    // Try Kiwi if others fail
    if (!results && API_CONFIG.kiwi.enabled) {
        results = await searchKiwiFlights(from, to, departDate, returnDate);
    }

    // Fallback to simulated data
    if (!results) {
        console.log('All APIs failed, using simulated data');
        results = generateSimulatedFlights(from, to, departDate, returnDate);
    }

    return results;
}

// Scan for weekend deals
async function scanForDeals() {
    const deals = [];
    const weekends = generateWeekendDates(settings.lookAheadWeeks);

    console.log(`Scanning for deals from ${settings.baseAirport} to ${settings.destinations.length} destinations`);

    for (const destination of settings.destinations) {
        for (const weekend of weekends) {
            try {
                const flights = await searchFlights(
                    settings.baseAirport,
                    destination,
                    weekend.depart,
                    weekend.return
                );

                // Process flights to find deals
                for (const flight of flights) {
                    // Skip flights that don't meet criteria
                    if (flight.price > settings.maxPrice || flight.duration > settings.maxFlightTime * 60) {
                        continue;
                    }

                    // Update price history
                    const route = `${flight.from}-${flight.to}`;
                    if (!priceHistory[route]) {
                        priceHistory[route] = { prices: [], average: 0 };
                    }

                    priceHistory[route].prices.push(flight.price);
                    
                    // Keep only last 52 weeks of data
                    if (priceHistory[route].prices.length > 52) {
                        priceHistory[route].prices.shift();
                    }

                    // Calculate average
                    const avg = priceHistory[route].prices.reduce((a, b) => a + b, 0) / priceHistory[route].prices.length;
                    priceHistory[route].average = avg;

                    // Check if this is a deal
                    if (flight.price < avg * 0.9) { // 10% below average
                        flight.dealScore = (avg - flight.price) / avg;
                        deals.push(flight);
                    }
                }

                // Add delay to respect API rate limits
                await new Promise(resolve => setTimeout(resolve, 1000));
            } catch (error) {
                console.error(`Error searching ${destination}:`, error);
            }
        }
    }

    return deals;
}

// Generate weekend dates
function generateWeekendDates(weeks) {
    const weekends = [];
    const today = new Date();

    for (let i = 1; i <= weeks; i++) {
        // Find next Friday
        const friday = new Date(today);
        friday.setDate(today.getDate() + (i * 7) - today.getDay() + 5);
        
        // Return on Sunday
        const sunday = new Date(friday);
        sunday.setDate(friday.getDate() + 2);

        weekends.push({
            depart: friday.toISOString().split('T')[0],
            return: sunday.toISOString().split('T')[0]
        });
    }

    return weekends;
}

// Send email notification
async function sendEmailNotification(deals) {
    if (!settings.emailEnabled || !settings.email || deals.length === 0) {
        return;
    }

    // Filter deals by threshold
    const goodDeals = deals.filter(deal => deal.dealScore >= settings.dealThreshold);
    if (goodDeals.length === 0) return;

    try {
        // Configure email transporter
        const transporter = nodemailer.createTransport({
            service: process.env.EMAIL_SERVICE || 'gmail',
            auth: {
                user: process.env.EMAIL_USER,
                pass: process.env.EMAIL_PASS
            }
        });

        // Create HTML email
        const html = `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .header { background-color: #0066FF; color: white; padding: 20px; text-align: center; }
                    .deals { margin: 20px 0; }
                    .deal { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                    .price { font-size: 24px; font-weight: bold; color: #0066FF; }
                    .savings { color: #4CAF50; font-weight: bold; }
                    .button { display: inline-block; background-color: #0066FF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Flight Deal Alert!</h1>
                    <p>${goodDeals.length} amazing deals found from ${settings.baseAirport}</p>
                </div>
                <div class="deals">
                    ${goodDeals.map(deal => `
                        <div class="deal">
                            <h3>${deal.from} → ${deal.to}</h3>
                            <p class="price">${deal.price}</p>
                            <p class="savings">${Math.round(deal.dealScore * 100)}% below average!</p>
                            <p><strong>Dates:</strong> ${deal.departDate} - ${deal.returnDate}</p>
                            <p><strong>Airline:</strong> ${deal.airline} (${deal.flight})</p>
                            <a href="${deal.url}" class="button">Book Now</a>
                        </div>
                    `).join('')}
                </div>
                <p>Visit your dashboard to see all deals and manage your preferences.</p>
            </body>
            </html>
        `;

        await transporter.sendMail({
            from: process.env.EMAIL_USER,
            to: settings.email,
            subject: `Flight Deal Alert: ${goodDeals.length} deals from ${settings.baseAirport}!`,
            html: html
        });

        console.log(`Email sent with ${goodDeals.length} deals`);
    } catch (error) {
        console.error('Error sending email:', error);
    }
}

// API Routes
app.get('/api/deals', (req, res) => {
    res.json(currentDeals);
});

app.get('/api/settings', (req, res) => {
    res.json(settings);
});

app.post('/api/settings', async (req, res) => {
    try {
        settings = { ...settings, ...req.body };
        await saveData();
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Failed to save settings' });
    }
});

app.get('/api/price-history', (req, res) => {
    res.json(priceHistory);
});

app.post('/api/refresh', async (req, res) => {
    try {
        console.log('Manual refresh triggered');
        const deals = await scanForDeals();
        
        // Sort by deal score
        deals.sort((a, b) => b.dealScore - a.dealScore);
        
        currentDeals = deals;
        await saveData();
        
        res.json({ success: true, deals: deals });
    } catch (error) {
        console.error('Refresh error:', error);
        res.status(500).json({ error: 'Failed to refresh deals' });
    }
});

app.post('/api/search', async (req, res) => {
    try {
        const { from, to, departDate, returnDate } = req.body;
        const results = await searchFlights(from, to, departDate, returnDate);
        res.json(results);
    } catch (error) {
        console.error('Search error:', error);
        res.status(500).json({ error: 'Search failed' });
    }
});

// Serve frontend
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// Schedule automatic scans
function scheduleScans() {
    // Run every day at 6 AM
    cron.schedule('0 6 * * *', async () => {
        console.log('Running scheduled scan');
        try {
            const deals = await scanForDeals();
            currentDeals = deals.sort((a, b) => b.dealScore - a.dealScore);
            await saveData();
            await sendEmailNotification(deals);
            console.log(`Scheduled scan complete. Found ${deals.length} deals.`);
        } catch (error) {
            console.error('Scheduled scan error:', error);
        }
    });

    console.log('Scheduled daily scans at 6 AM');
}

// Utility functions
function parseDuration(isoDuration) {
    // Convert ISO 8601 duration to minutes
    const regex = /PT(\d+H)?(\d+M)?/;
    const match = isoDuration.match(regex);
    let minutes = 0;
    
    if (match[1]) {
        minutes += parseInt(match[1]) * 60;
    }
    if (match[2]) {
        minutes += parseInt(match[2]);
    }
    
    return minutes;
}

// Initialize and start server
async function start() {
    try {
        await initDataDirectory();
        
        // Check which APIs are configured
        console.log('API Configuration:');
        console.log('- Amadeus:', API_CONFIG.amadeus.enabled ? 'Enabled' : 'Disabled');
        console.log('- Skyscanner:', API_CONFIG.skyscanner.enabled ? 'Enabled' : 'Disabled');
        console.log('- Kiwi:', API_CONFIG.kiwi.enabled ? 'Enabled' : 'Disabled');
        
        if (!API_CONFIG.amadeus.enabled && !API_CONFIG.skyscanner.enabled && !API_CONFIG.kiwi.enabled) {
            console.warn('WARNING: No flight APIs configured. Using simulated data only.');
        }
        
        // Start server
        app.listen(port, () => {
            console.log(`Flight Deal Finder server running on port ${port}`);
        });
        
        // Schedule automatic scans
        scheduleScans();
        
        // Run initial scan if no deals exist
        if (currentDeals.length === 0) {
            console.log('No deals found, running initial scan...');
            const deals = await scanForDeals();
            currentDeals = deals.sort((a, b) => b.dealScore - a.dealScore);
            await saveData();
            console.log(`Initial scan complete. Found ${deals.length} deals.`);
        }
    } catch (error) {
        console.error('Startup error:', error);
        process.exit(1);
    }
}

// Start the application
start();

// Handle graceful shutdown
process.on('SIGTERM', async () => {
    console.log('SIGTERM received. Shutting down gracefully...');
    await saveData();
    process.exit(0);
});

process.on('SIGINT', async () => {
    console.log('SIGINT received. Shutting down gracefully...');
    await saveData();
    process.exit(0);
});