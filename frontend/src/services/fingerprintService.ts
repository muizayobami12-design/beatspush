import FingerprintJS from '@fingerprintjs/fingerprintjs';

let fpPromise: Promise<any> | null = null;

/**
 * Initialize FingerprintJS
 * Call this once when app loads
 */
export async function initFingerprint() {
  if (!fpPromise) {
    fpPromise = FingerprintJS.load();
  }
  return fpPromise;
}

/**
 * Get device fingerprint ID
 * Returns a unique ID that persists across incognito mode, VPNs, etc.
 */
export async function getDeviceId(): Promise<string> {
  try {
    const fp = await initFingerprint();
    const result = await fp.get();
    return result.visitorId;
  } catch (error) {
    console.error('Failed to get device fingerprint:', error);
    // Fallback to a session-based ID
    return generateFallbackId();
  }
}

/**
 * Get detailed device information
 * Useful for fraud detection
 */
export async function getDeviceInfo() {
  try {
    const fp = await initFingerprint();
    const result = await fp.get();
    
    return {
      visitorId: result.visitorId,
      confidence: result.confidence.score,
      components: {
        browser: result.components.vendor?.value || 'Unknown',
        browserVersion: result.components.vendorVersion?.value || 'Unknown',
        os: result.components.platform?.value || 'Unknown',
        screen: `${result.components.screenResolution?.value?.[0]}x${result.components.screenResolution?.value?.[1]}`,
        timezone: result.components.timezone?.value || 'Unknown',
        language: result.components.languages?.value?.[0]?.[0] || 'Unknown',
        deviceMemory: result.components.deviceMemory?.value || 'Unknown',
        hardwareConcurrency: result.components.hardwareConcurrency?.value || 'Unknown',
      }
    };
  } catch (error) {
    console.error('Failed to get device info:', error);
    return null;
  }
}

/**
 * Fallback ID generation (when fingerprinting fails)
 * Uses sessionStorage to persist during session
 */
function generateFallbackId(): string {
  if (typeof window === 'undefined') return 'server';
  
  const storageKey = 'device_fallback_id';
  let id = sessionStorage.getItem(storageKey);
  
  if (!id) {
    id = `fallback_${Date.now()}_${Math.random().toString(36).substring(2)}`;
    sessionStorage.setItem(storageKey, id);
  }
  
  return id;
}

/**
 * Check if device fingerprint has changed since last login
 * Returns true if changed (suspicious)
 */
export async function hasDeviceChanged(lastDeviceId: string | null): Promise<boolean> {
  if (!lastDeviceId) return false;
  
  const currentDeviceId = await getDeviceId();
  return currentDeviceId !== lastDeviceId;
}
