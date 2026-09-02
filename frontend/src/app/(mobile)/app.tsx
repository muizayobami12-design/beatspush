/**
 * React Native Mobile App Setup
 * iOS + Android app entry point
 * Uses Expo for cross-platform development
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';

// Keep the splash screen visible while we fetch resources
SplashScreen.preventAutoHideAsync();

// Navigation setup
const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// ============ SCREEN IMPORTS ============

// Auth screens
import LoginScreen from './screens/auth/LoginScreen';
import RegisterScreen from './screens/auth/RegisterScreen';
import OnboardingScreen from './screens/auth/OnboardingScreen';

// Home tabs
import HomeScreen from './screens/home/HomeScreen';
import DiscoverScreen from './screens/discover/DiscoverScreen';
import MessagesScreen from './screens/messages/MessagesScreen';
import ProfileScreen from './screens/profile/ProfileScreen';

// Feature screens
import BeatsScreen from './screens/beats/BeatsScreen';
import BeatDetailScreen from './screens/beats/BeatDetailScreen';
import TipsScreen from './screens/tips/TipsScreen';
import BookingsScreen from './screens/bookings/BookingsScreen';
import AnalyticsScreen from './screens/analytics/AnalyticsScreen';
import NotificationsScreen from './screens/notifications/NotificationsScreen';

// ============ AUTH STACK ============

function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        animationEnabled: true,
        cardStyleInterpolator: ({ current, layouts }) => {
          return {
            cardStyle: {
              transform: [
                {
                  translateX: current.progress.interpolate({
                    inputRange: [0, 1],
                    outputRange: [layouts.screen.width, 0],
                  }),
                },
              ],
            },
          };
        },
      }}
    >
      <Stack.Screen name="Onboarding" component={OnboardingScreen} />
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

// ============ HOME TABS ============

function HomeTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: true,
        tabBarActiveTintColor: '#a855f7',
        tabBarInactiveTintColor: '#6b7280',
        tabBarStyle: {
          backgroundColor: '#1f2937',
          borderTopColor: '#374151',
          paddingBottom: 8,
          paddingTop: 8,
        },
        headerStyle: {
          backgroundColor: '#1f2937',
          borderBottomColor: '#374151',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          title: 'BeatPush',
          tabBarIcon: ({ color, size }) => (
            <Icon name="home" type="material" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Discover"
        component={DiscoverScreen}
        options={{
          title: 'Discover',
          tabBarIcon: ({ color, size }) => (
            <Icon name="search" type="material" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Beats"
        component={BeatsScreen}
        options={{
          title: 'Beats',
          tabBarIcon: ({ color, size }) => (
            <Icon name="music-note" type="material" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Messages"
        component={MessagesScreen}
        options={{
          title: 'Messages',
          tabBarIcon: ({ color, size }) => (
            <Icon name="mail" type="material" color={color} size={size} />
          ),
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <Icon name="person" type="material" color={color} size={size} />
          ),
        }}
      />
    </Tab.Navigator>
  );
}

// ============ ROOT NAVIGATOR ============

function RootNavigator() {
  const [isSignedIn, setIsSignedIn] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    // Check if user is already signed in
    const checkAuth = async () => {
      try {
        const token = await getStoredToken();
        setIsSignedIn(!!token);
      } catch (e) {
        console.error('Auth check error:', e);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (isLoading) {
    return null; // Splash screen will be shown
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isSignedIn ? (
          <>
            <Stack.Group>
              <Stack.Screen name="HomeTabs" component={HomeTabs} />
            </Stack.Group>

            {/* Modal screens */}
            <Stack.Group screenOptions={{ presentation: 'modal' }}>
              <Stack.Screen name="Tips" component={TipsScreen} />
              <Stack.Screen name="Bookings" component={BookingsScreen} />
              <Stack.Screen name="Analytics" component={AnalyticsScreen} />
              <Stack.Screen name="Notifications" component={NotificationsScreen} />
              <Stack.Screen name="BeatDetail" component={BeatDetailScreen} />
            </Stack.Group>
          </>
        ) : (
          <Stack.Group screenOptions={{ headerShown: false }}>
            <Stack.Screen name="Auth" component={AuthStack} />
          </Stack.Group>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// ============ MAIN APP COMPONENT ============

export default function App() {
  const [fontsLoaded] = useFonts({
    'Poppins-Bold': require('./assets/fonts/Poppins-Bold.ttf'),
    'Poppins-Regular': require('./assets/fonts/Poppins-Regular.ttf'),
    'Poppins-SemiBold': require('./assets/fonts/Poppins-SemiBold.ttf'),
  });

  React.useEffect(() => {
    if (fontsLoaded) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded]);

  if (!fontsLoaded) {
    return null;
  }

  return (
    <>
      <StatusBar barStyle="light-content" backgroundColor="#1f2937" />
      <RootNavigator />
    </>
  );
}

// ============ UTILITY FUNCTIONS ============

async function getStoredToken() {
  // In production, use React Native AsyncStorage
  return null;
}
