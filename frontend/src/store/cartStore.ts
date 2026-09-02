import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Beat } from '@/types';

export interface CartItem {
  beat: Beat;
  licenseType: 'lease' | 'exclusive';
  price: number;
}

interface CartState {
  items: CartItem[];
  
  // Actions
  addToCart: (beat: Beat, licenseType: 'lease' | 'exclusive') => void;
  removeFromCart: (beatId: string) => void;
  updateLicense: (beatId: string, licenseType: 'lease' | 'exclusive') => void;
  clearCart: () => void;
  getTotal: () => number;
  getItemCount: () => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],

      addToCart: (beat, licenseType) => {
        const { items } = get();
        const exists = items.find((item) => item.beat.id === beat.id);
        
        if (exists) {
          // Update license type if beat already in cart
          set({
            items: items.map((item) =>
              item.beat.id === beat.id
                ? {
                    ...item,
                    licenseType,
                    price: licenseType === 'lease' ? beat.price : beat.price * 3,
                  }
                : item
            ),
          });
        } else {
          // Add new item
          set({
            items: [
              ...items,
              {
                beat,
                licenseType,
                price: licenseType === 'lease' ? beat.price : beat.price * 3,
              },
            ],
          });
        }
      },

      removeFromCart: (beatId) => {
        set((state) => ({
          items: state.items.filter((item) => item.beat.id !== beatId),
        }));
      },

      updateLicense: (beatId, licenseType) => {
        set((state) => ({
          items: state.items.map((item) =>
            item.beat.id === beatId
              ? {
                  ...item,
                  licenseType,
                  price:
                    licenseType === 'lease'
                      ? item.beat.price
                      : item.beat.price * 3,
                }
              : item
          ),
        }));
      },

      clearCart: () => set({ items: [] }),

      getTotal: () => {
        const { items } = get();
        return items.reduce((total, item) => total + item.price, 0);
      },

      getItemCount: () => {
        const { items } = get();
        return items.length;
      },
    }),
    {
      name: 'cart-storage',
    }
  )
);
