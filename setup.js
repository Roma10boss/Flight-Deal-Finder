// setup.js - Initial setup script
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Setting up Weekend Flight Deal Finder...\n');

// Create necessary directories
const directories = ['public', 'data'];
directories.forEach(dir => {
    const dirPath = path.join(__dirname, dir);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
        console.log(`✅ Created ${dir} directory`);
    } else {
        console.log(`📁 ${dir} directory already exists`);
    }
});

// Create .env file if it doesn't exist
const envPath = path.join(__dirname, '.env');
if (!fs.existsSync(envPath)) {
    const envTemplate = `# .env - Environment Variables Configuration

# Server Configuration
PORT=3000
NODE_ENV=development

# Flight API Configuration (Choose one or more)

# Amadeus API (Recommended - Free tier available)
# Get your credentials at: https://developers.amadeus.com
AMADEUS_CLIENT_ID=
AMADEUS_CLIENT_SECRET=

# Skyscanner API (via RapidAPI)
# Get your API key at: https://rapidapi.com/skyscanner/api/skyscanner-flight-search
SKYSCANNER_API_KEY=

# Kiwi.com Tequila API
# Get your API key at: https://tequila.kiwi.com/portal/login
KIWI_API_KEY=

# Email Configuration (for notifications)
EMAIL_SERVICE=gmail
EMAIL_USER=
EMAIL_PASS=
`;
    fs.writeFileSync(envPath, envTemplate);
    console.log('✅ Created .env file - Please add your API credentials');
} else {
    console.log('📁 .env file already exists');
}

// Create .gitignore if it doesn't exist
const gitignorePath = path.join(__dirname, '.gitignore');
if (!fs.existsSync(gitignorePath)) {
    const gitignoreContent = `# Dependencies
node_modules/

# Environment variables
.env

# Data files
data/

# IDE files
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory
coverage/

# Temporary files
temp/
tmp/
`;
    fs.writeFileSync(gitignorePath, gitignoreContent);
    console.log('✅ Created .gitignore file');
} else {
    console.log('📁 .gitignore file already exists');
}

// Check if package.json exists
const packagePath = path.join(__dirname, 'package.json');
if (!fs.existsSync(packagePath)) {
    console.log('⚠️  package.json not found. Please create it first.');
    process.exit(1);
}

// Install dependencies
console.log('\n📦 Installing dependencies...');
try {
    execSync('npm install', { stdio: 'inherit' });
    console.log('✅ Dependencies installed successfully');
} catch (error) {
    console.error('❌ Error installing dependencies:', error.message);
    process.exit(1);
}

// Create default data files
const defaultSettings = {
    baseAirport: 'LAX',
    maxPrice: 300,
    maxFlightTime: 5,
    destinations: ['JFK', 'MIA', 'ORD', 'BOS', 'SEA', 'SFO', 'LAS'],
    lookAheadWeeks: 12,
    email: '',
    emailEnabled: false,
    dealThreshold: 0.7
};

const settingsPath = path.join(__dirname, 'data', 'settings.json');
if (!fs.existsSync(settingsPath)) {
    fs.writeFileSync(settingsPath, JSON.stringify(defaultSettings, null, 2));
    console.log('✅ Created default settings.json');
}

const dealsPath = path.join(__dirname, 'data', 'deals.json');
if (!fs.existsSync(dealsPath)) {
    fs.writeFileSync(dealsPath, '[]');
    console.log('✅ Created empty deals.json');
}

const historyPath = path.join(__dirname, 'data', 'price-history.json');
if (!fs.existsSync(historyPath)) {
    fs.writeFileSync(historyPath, '{}');
    console.log('✅ Created empty price-history.json');
}

console.log('\n🎉 Setup complete! Next steps:\n');
console.log('1. Copy the index.html file to the public directory');
console.log('2. Edit the .env file and add your API credentials');
console.log('3. Run the server with: npm start');
console.log('4. Open http://localhost:3000 in your browser\n');
console.log('📚 For more information, check the README.md file');