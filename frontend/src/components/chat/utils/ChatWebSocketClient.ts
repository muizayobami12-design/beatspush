/**
 * ChatWebSocketClient - WebSocket client for AI Chat Interface
 * Handles connection management, authentication, and message queuing
 */

import type {
  ChatMessagePayload,
  StreamingChunk,
  WebSocketClientConfig,
  WebSocketCallbacks,
} from '../types';
import { WEBSOCKET_CONFIG, API_ENDPOINTS } from '../constants';

export class ChatWebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts: number;
  private reconnectDelays: number[];
  private messageQueue: ChatMessagePayload[] = [];
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  
  private config: WebSocketClientConfig;
  private callbacks: WebSocketCallbacks;
  private isConnecting = false;
  private isManualClose = false;

  constructor(config: WebSocketClientConfig, callbacks: WebSocketCallbacks = {}) {
    this.config = config;
    this.callbacks = callbacks;
    this.maxReconnectAttempts = config.maxReconnectAttempts ?? WEBSOCKET_CONFIG.MAX_RECONNECT_ATTEMPTS;
    this.reconnectDelays = config.reconnectDelays ?? WEBSOCKET_CONFIG.RECONNECT_DELAYS;
  }

  /**
   * Establish WebSocket connection with JWT authentication
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    this.isManualClose = false;

    try {
      // Build WebSocket URL with JWT token as query parameter
      const wsUrl = this.buildWebSocketUrl();
      
      this.ws = new WebSocket(wsUrl);

      // Set up event handlers
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);

      // Wait for connection to establish (with timeout)
      await this.waitForConnection();
    } catch (error) {
      this.isConnecting = false;
      throw new Error(`Failed to connect: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Gracefully disconnect WebSocket
   */
  disconnect(): void {
    this.isManualClose = true;
    this.stopHeartbeat();
    this.clearReconnectTimeout();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.reconnectAttempts = 0;
    this.messageQueue = [];
  }

  /**
   * Send message through WebSocket
   * Queues message if not connected
   */
  send(message: ChatMessagePayload): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('Failed to send message:', error);
        this.messageQueue.push(message);
      }
    } else {
      // Queue message for later delivery
      this.messageQueue.push(message);
      
      // Attempt to reconnect if not already connecting
      if (!this.isConnecting && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnect();
      }
    }
  }

  /**
   * Check if WebSocket is currently connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get current connection state
   */
  getReadyState(): number | null {
    return this.ws?.readyState ?? null;
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  private buildWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const baseUrl = process.env.NEXT_PUBLIC_WS_URL || `${protocol}//${host}`;
    
    // Remove protocol if already present in baseUrl
    const cleanBaseUrl = baseUrl.replace(/^(ws|wss):\/\//, '');
    
    // Build full URL with auth token
    return `${protocol}//${cleanBaseUrl}${API_ENDPOINTS.WS_CHAT}?token=${encodeURIComponent(this.config.token)}`;
  }

  private async waitForConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error('Connection timeout'));
      }, 10000); // 10 second timeout

      if (this.ws) {
        const checkConnection = () => {
          if (this.ws?.readyState === WebSocket.OPEN) {
            clearTimeout(timeout);
            resolve();
          } else if (this.ws?.readyState === WebSocket.CLOSED || this.ws?.readyState === WebSocket.CLOSING) {
            clearTimeout(timeout);
            reject(new Error('Connection failed'));
          }
        };

        this.ws.addEventListener('open', checkConnection);
        this.ws.addEventListener('error', () => {
          clearTimeout(timeout);
          reject(new Error('Connection error'));
        });
      }
    });
  }

  private handleOpen(): void {
    console.log('[ChatWebSocket] Connected');
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    
    // Start heartbeat
    this.startHeartbeat();
    
    // Flush queued messages
    this.flushQueue();
    
    // Notify callback
    this.callbacks.onOpen?.();
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const chunk: StreamingChunk = JSON.parse(event.data);
      this.callbacks.onMessage?.(chunk);
    } catch (error) {
      console.error('[ChatWebSocket] Failed to parse message:', error);
    }
  }

  private handleError(event: Event): void {
    console.error('[ChatWebSocket] Error:', event);
    this.callbacks.onError?.(new Error('WebSocket error'));
  }

  private handleClose(event: CloseEvent): void {
    console.log('[ChatWebSocket] Closed:', event.code, event.reason);
    this.stopHeartbeat();
    this.isConnecting = false;
    
    // Notify callback
    this.callbacks.onClose?.();
    
    // Attempt reconnection if not a manual close
    if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnect();
    } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[ChatWebSocket] Max reconnection attempts reached');
      this.callbacks.onError?.(new Error('Max reconnection attempts reached'));
    }
  }

  private reconnect(): void {
    const delay = this.reconnectDelays[Math.min(this.reconnectAttempts, this.reconnectDelays.length - 1)];
    
    console.log(`[ChatWebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`);
    
    this.clearReconnectTimeout();
    
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect().catch((error) => {
        console.error('[ChatWebSocket] Reconnection failed:', error);
      });
    }, delay);
  }

  private flushQueue(): void {
    if (this.messageQueue.length === 0) {
      return;
    }

    console.log(`[ChatWebSocket] Flushing ${this.messageQueue.length} queued messages`);
    
    const queue = [...this.messageQueue];
    this.messageQueue = [];
    
    queue.forEach((message) => {
      this.send(message);
    });
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        try {
          this.ws.send(JSON.stringify({ type: 'ping' }));
        } catch (error) {
          console.error('[ChatWebSocket] Heartbeat failed:', error);
        }
      }
    }, WEBSOCKET_CONFIG.HEARTBEAT_INTERVAL_MS);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private clearReconnectTimeout(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }
}
