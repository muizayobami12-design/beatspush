/**
 * HomeScreen - Mobile Home Feed
 * Displays personalized beat recommendations, trending beats, artist updates
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  FlatList,
  TouchableOpacity,
  Text,
  Image,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');
const BEAT_CARD_WIDTH = (width - 32) / 2;

interface Beat {
  id: string;
  title: string;
  artist: string;
  cover: string;
  price: number;
  plays: number;
  rating: number;
  genre: string;
}

interface Artist {
  id: string;
  name: string;
  avatar: string;
  followers: number;
  isFollowing: boolean;
}

export default function HomeScreen() {
  const navigation = useNavigation();
  const [beats, setBeats] = useState<Beat[]>([]);
  const [artists, setArtists] = useState<Artist[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHomeData();
  }, []);

  const loadHomeData = async () => {
    setLoading(true);
    try {
      // Fetch personalized recommendations and trending beats
      const [beatsRes, artistsRes] = await Promise.all([
        fetch('/api/v1/beats?limit=20&trending=true'),
        fetch('/api/v1/users/following?limit=10'),
      ]);

      const beatsData = await beatsRes.json();
      const artistsData = await artistsRes.json();

      setBeats(beatsData.data || []);
      setArtists(artistsData.data || []);
    } catch (error) {
      console.error('Failed to load home data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadHomeData();
    setRefreshing(false);
  };

  const handleFollowArtist = async (artistId: string) => {
    try {
      await fetch(`/api/v1/users/${artistId}/follow`, {
        method: 'POST',
      });
      // Update local state
      setArtists(artists.map(a => 
        a.id === artistId ? { ...a, isFollowing: !a.isFollowing } : a
      ));
    } catch (error) {
      console.error('Follow error:', error);
    }
  };

  const handleBeatPress = (beatId: string) => {
    navigation.navigate('BeatDetail', { id: beatId });
  };

  const renderBeatCard = ({ item }: { item: Beat }) => (
    <TouchableOpacity
      style={{
        width: BEAT_CARD_WIDTH,
        marginBottom: 16,
        borderRadius: 12,
        overflow: 'hidden',
        backgroundColor: '#2a3f5f',
      }}
      onPress={() => handleBeatPress(item.id)}
    >
      <Image
        source={{ uri: item.cover }}
        style={{ width: '100%', height: BEAT_CARD_WIDTH, backgroundColor: '#1f2937' }}
      />
      <View style={{ padding: 12 }}>
        <Text style={{ fontSize: 14, fontWeight: '600', color: '#fff' }} numberOfLines={1}>
          {item.title}
        </Text>
        <Text style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }} numberOfLines={1}>
          {item.artist}
        </Text>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 }}>
          <Text style={{ fontSize: 14, fontWeight: 'bold', color: '#a855f7' }}>
            ₦{item.price.toLocaleString()}
          </Text>
          <Text style={{ fontSize: 12, color: '#6b7280' }}>
            ⭐ {item.rating.toFixed(1)}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderArtist = ({ item }: { item: Artist }) => (
    <TouchableOpacity
      style={{
        alignItems: 'center',
        marginRight: 16,
        width: 80,
      }}
      onPress={() => navigation.navigate('Profile', { artistId: item.id })}
    >
      <Image
        source={{ uri: item.avatar }}
        style={{
          width: 64,
          height: 64,
          borderRadius: 32,
          backgroundColor: '#374151',
          marginBottom: 8,
        }}
      />
      <Text style={{ fontSize: 12, color: '#fff', fontWeight: '600', textAlign: 'center' }}>
        {item.name}
      </Text>
      <TouchableOpacity
        style={{
          marginTop: 6,
          paddingHorizontal: 12,
          paddingVertical: 4,
          backgroundColor: item.isFollowing ? '#374151' : '#a855f7',
          borderRadius: 4,
        }}
        onPress={() => handleFollowArtist(item.id)}
      >
        <Text style={{ fontSize: 10, color: '#fff', fontWeight: '600' }}>
          {item.isFollowing ? 'Following' : 'Follow'}
        </Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#1f2937' }}>
      <ScrollView
        style={{ flex: 1 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Header Section */}
        <View style={{ padding: 16 }}>
          <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#fff' }}>
            Discover Beats
          </Text>
          <Text style={{ fontSize: 14, color: '#9ca3af', marginTop: 4 }}>
            Explore trending and personalized beats
          </Text>
        </View>

        {/* Trending Artists */}
        <View style={{ paddingVertical: 12 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#fff', paddingHorizontal: 16, marginBottom: 12 }}>
            Featured Artists
          </Text>
          <FlatList
            data={artists}
            renderItem={renderArtist}
            keyExtractor={item => item.id}
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{ paddingHorizontal: 16 }}
          />
        </View>

        {/* Trending Beats Grid */}
        <View style={{ paddingHorizontal: 16, paddingVertical: 12 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#fff', marginBottom: 12 }}>
            Trending Now
          </Text>
          <FlatList
            data={beats}
            renderItem={renderBeatCard}
            keyExtractor={item => item.id}
            numColumns={2}
            columnWrapperStyle={{ justifyContent: 'space-between' }}
            scrollEnabled={false}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
