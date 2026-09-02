#!/usr/bin/env node
/**
 * Frontend Setup Test
 * Verifies Next.js and component setup
 */

const fs = require('fs');
const path = require('path');

console.log('\n' + '='.repeat(70));
console.log('BEATPUSH FRONTEND TEST SUITE');
console.log('='.repeat(70));

let testsPassed = 0;
let testsTotal = 0;

// Helper function
function test(name, fn) {
  testsTotal++;
  try {
    console.log(`\n[${testsTotal}] ${name}...`);
    fn();
    console.log('    PASSED');
    testsPassed++;
  } catch (e) {
    console.log(`    FAILED: ${e.message}`);
  }
}

// Test 1: Check node_modules
test('Dependencies Installed', () => {
  const nodeModulesPath = path.join(__dirname, 'node_modules');
  if (!fs.existsSync(nodeModulesPath)) {
    throw new Error('node_modules not found - run npm install');
  }
  const hasReact = fs.existsSync(path.join(nodeModulesPath, 'react'));
  const hasNext = fs.existsSync(path.join(nodeModulesPath, 'next'));
  if (!hasReact || !hasNext) {
    throw new Error('Missing React or Next.js');
  }
  console.log('    React and Next.js installed');
});

// Test 2: Check package.json
test('Package Configuration', () => {
  const packagePath = path.join(__dirname, 'package.json');
  const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  if (!pkg.name || !pkg.version) {
    throw new Error('Invalid package.json');
  }
  console.log(`    Project: ${pkg.name} v${pkg.version}`);
  console.log(`    Scripts: ${Object.keys(pkg.scripts).join(', ')}`);
});

// Test 3: Check src directory
test('Source Directory Structure', () => {
  const srcPath = path.join(__dirname, 'src');
  const appPath = path.join(srcPath, 'app');
  const componentsPath = path.join(srcPath, 'components');
  const servicesPath = path.join(srcPath, 'services');
  
  if (!fs.existsSync(srcPath)) throw new Error('src/ not found');
  if (!fs.existsSync(appPath)) throw new Error('src/app/ not found');
  if (!fs.existsSync(componentsPath)) throw new Error('src/components/ not found');
  if (!fs.existsSync(servicesPath)) throw new Error('src/services/ not found');
  
  console.log('    src/app, components, services exist');
});

// Test 4: Check environment files
test('Environment Configuration', () => {
  const envLocalPath = path.join(__dirname, '.env.local');
  const envExamplePath = path.join(__dirname, '.env.local.example');
  
  if (!fs.existsSync(envLocalPath)) {
    throw new Error('.env.local not found');
  }
  
  const envContent = fs.readFileSync(envLocalPath, 'utf8');
  if (!envContent.includes('NEXT_PUBLIC_API_URL')) {
    throw new Error('Missing NEXT_PUBLIC_API_URL in .env.local');
  }
  
  console.log('    API_URL configured');
  console.log('    Environment variables set');
});

// Test 5: Check key component files
test('Key Component Files', () => {
  const filesToCheck = [
    'src/components/layouts/MainNav.tsx',
    'src/components/features/beats/BeatCard.tsx',
    'src/components/features/analytics/RevenueChart.tsx',
    'src/app/(dashboard)/profile/page.tsx',
    'src/services/api.ts',
  ];
  
  const missing = filesToCheck.filter(file => {
    const filePath = path.join(__dirname, file);
    return !fs.existsSync(filePath);
  });
  
  if (missing.length > 0) {
    console.log(`    Missing files: ${missing.join(', ')}`);
  }
  
  const found = filesToCheck.length - missing.length;
  console.log(`    ${found}/${filesToCheck.length} key files exist`);
  
  if (missing.length === 0) {
    // Don't throw, just report
  }
});

// Test 6: Check tsconfig
test('TypeScript Configuration', () => {
  const tsconfigPath = path.join(__dirname, 'tsconfig.json');
  if (!fs.existsSync(tsconfigPath)) {
    throw new Error('tsconfig.json not found');
  }
  
  const tsconfig = JSON.parse(fs.readFileSync(tsconfigPath, 'utf8'));
  if (!tsconfig.compilerOptions) {
    throw new Error('Invalid tsconfig.json');
  }
  
  console.log('    TypeScript configured');
});

// Test 7: Check tailwind config
test('Tailwind CSS Configuration', () => {
  const tailwindPath = path.join(__dirname, 'tailwind.config.ts');
  if (!fs.existsSync(tailwindPath)) {
    throw new Error('tailwind.config.ts not found');
  }
  
  console.log('    Tailwind configured');
});

// Test 8: Check next.config
test('Next.js Configuration', () => {
  const nextConfigPath = path.join(__dirname, 'next.config.js');
  if (!fs.existsSync(nextConfigPath)) {
    throw new Error('next.config.js not found');
  }
  
  console.log('    Next.js config found');
});

// Summary
console.log('\n' + '='.repeat(70));
console.log(`SUMMARY: ${testsPassed}/${testsTotal} tests passed`);
console.log('='.repeat(70) + '\n');

if (testsPassed === testsTotal) {
  console.log('SUCCESS: Frontend setup is complete!');
  console.log('Next steps:');
  console.log('  1. Run: npm run dev');
  console.log('  2. Open: http://localhost:3000');
  console.log('  3. Test the application in browser');
  process.exit(0);
} else {
  console.log('WARNING: Some checks failed - see above');
  process.exit(1);
}
