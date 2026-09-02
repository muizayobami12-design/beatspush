export default function SimpleTest() {
  return (
    <div style={{ padding: '20px', backgroundColor: 'red', color: 'white', fontSize: '24px' }}>
      <h1>SIMPLE TEST PAGE</h1>
      <p>If you see this RED background, React is working!</p>
      <p>If you see this text, the page is rendering!</p>
      <div style={{ backgroundColor: 'blue', padding: '20px', marginTop: '20px' }}>
        <p>Blue box test</p>
      </div>
      <div style={{ backgroundColor: 'green', padding: '20px', marginTop: '20px' }}>
        <p>Green box test</p>
      </div>
    </div>
  );
}
