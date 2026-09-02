// NO IMPORTS - Pure React only
export default function EmergencyTest() {
  return (
    <html>
      <body style={{ margin: 0, padding: '40px', fontFamily: 'Arial', backgroundColor: '#ffeb3b' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h1 style={{ color: '#000', fontSize: '48px', marginBottom: '20px' }}>
            🚨 EMERGENCY TEST PAGE 🚨
          </h1>
          
          <div style={{ backgroundColor: '#f44336', color: 'white', padding: '30px', marginBottom: '20px', borderRadius: '8px' }}>
            <h2 style={{ margin: '0 0 10px 0' }}>If you see this RED box...</h2>
            <p style={{ margin: 0, fontSize: '18px' }}>React is working! The problem is with CSS/imports.</p>
          </div>

          <div style={{ backgroundColor: '#4caf50', color: 'white', padding: '30px', marginBottom: '20px', borderRadius: '8px' }}>
            <h2 style={{ margin: '0 0 10px 0' }}>If you see this GREEN box...</h2>
            <p style={{ margin: 0, fontSize: '18px' }}>HTML is rendering correctly!</p>
          </div>

          <div style={{ backgroundColor: '#2196f3', color: 'white', padding: '30px', marginBottom: '20px', borderRadius: '8px' }}>
            <h2 style={{ margin: '0 0 10px 0' }}>If you see this BLUE box...</h2>
            <p style={{ margin: 0, fontSize: '18px' }}>Inline styles are working!</p>
          </div>

          <div style={{ backgroundColor: 'white', padding: '30px', border: '3px solid #000', borderRadius: '8px' }}>
            <h2 style={{ color: '#000', margin: '0 0 20px 0' }}>INSTRUCTIONS:</h2>
            <ol style={{ color: '#000', fontSize: '16px', lineHeight: '1.8' }}>
              <li>Open DevTools (F12)</li>
              <li>Click the "Console" tab</li>
              <li>Look for RED error messages</li>
              <li>Take a screenshot of the errors</li>
              <li>Share the screenshot with me</li>
            </ol>
            <p style={{ color: '#d32f2f', fontWeight: 'bold', marginTop: '20px', fontSize: '18px' }}>
              The console errors will tell us EXACTLY what's broken!
            </p>
          </div>

          <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#fff3e0', border: '2px solid #ff9800', borderRadius: '8px' }}>
            <h3 style={{ color: '#000', margin: '0 0 10px 0' }}>Current URL:</h3>
            <p style={{ color: '#000', fontFamily: 'monospace', fontSize: '14px' }}>
              You should be at: http://localhost:3000/emergency-test
            </p>
          </div>
        </div>
      </body>
    </html>
  );
}
