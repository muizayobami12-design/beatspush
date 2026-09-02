declare module '@paystack/inline-js' {
  interface PaystackOptions {
    key: string;
    email: string;
    amount: number;
    currency?: string;
    ref?: string;
    metadata?: any;
    channels?: string[];
    onSuccess?: (transaction: any) => void;
    onCancel?: () => void;
  }

  class PaystackPop {
    newTransaction(options: PaystackOptions): void;
    resumeTransaction(accessCode: string): void;
    setup(options: PaystackOptions): {
      openIframe: () => void;
    };
  }

  export default PaystackPop;
}
