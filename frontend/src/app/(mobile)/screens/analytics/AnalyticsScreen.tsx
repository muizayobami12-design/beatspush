/**
 * AnalyticsScreen - Mobile Analytics Dashboard
 * Real-time earnings, beat performance, audience insights, ML predictions
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  TouchableOpacity,
  Text,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { LineChart, BarChart } from 'react-native-chart-kit';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');

interface EarningsData {
  today: number;
  week: number;
  month: number;
  total: number;
}

interface PerformanceData {
  beatId: string;
  title: string;
  plays: number;
  sales: number;
  revenue: number;
  trend: number; // % change
}

interface Prediction {
  type: 'revenue' | 'growth' | 'trend';
  value: number;
  confidence: number;
  timeframe: string;
}

export default function AnalyticsScreen() {
  const [earnings, setEarnings] = useState<EarningsData>({
    today: 0,
    week: 0,
    month: 0,
    total: 0,
  });
  const [performances, setPerformances] = useState<PerformanceData[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [chartData, setChartData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('month');

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      const [earningsRes, performanceRes, predictionsRes, chartRes] = await Promise.all([
        fetch('/api/v1/analytics/earnings'),
        fetch('/api/v1/analytics/performance?limit=5'),
        fetch('/api/v1/analytics/predictions'),
        fetch(`/api/v1/analytics/chart?range=${timeRange}`),
      ]);

      const earningsData = await earningsRes.json();
      const performanceData = await performanceRes.json();
      const predictionsData = await predictionsRes.json();
      const chartDataRes = await chartRes.json();

      setEarnings(earningsData.data);
      setPerformances(performanceData.data || []);
      setPredictions(predictionsData.data || []);
      setChartData(chartDataRes.data);
    } catch (error) {
      console.error('Analytics load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const EarningsCard = ({ label, value }: { label: string; value: number }) => (
    <View
      style={{
        flex: 1,
        backgroundColor: '#2a3f5f',
        borderRadius: 12,
        padding: 12,
        marginHorizontal: 6,
        marginBottom: 12,
      }}
    >
      <Text style={{ fontSize: 12, color: '#9ca3af', marginBottom: 4 }}>{label}</Text>
      <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#a855f7' }}>
        ₦{value.toLocaleString()}
      </Text>
    </View>
  );

  const PredictionCard = ({ pred }: { pred: Prediction }) => {
    const getIcon = () => {
      switch (pred.type) {
        case 'revenue':
          return '💰';
        case 'growth':
          return '📈';
        case 'trend':
          return '🎯';
        default:
          return '✨';
      }
    };

    return (
      <View
        style={{
          backgroundColor: '#2a3f5f',
          borderRadius: 12,
          padding: 12,
          marginBottom: 12,
          borderLeftWidth: 4,
          borderLeftColor: '#a855f7',
        }}
      >
        <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
          <View style={{ flex: 1 }}>
            <Text style={{ fontSize: 14, fontWeight: '600', color: '#fff', marginBottom: 4 }}>
              {getIcon()} {pred.type.charAt(0).toUpperCase() + pred.type.slice(1)} Prediction
            </Text>
            <Text style={{ fontSize: 12, color: '#9ca3af' }}>
              {pred.timeframe}
            </Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#10b981' }}>
              +{pred.value}%
            </Text>
            <Text style={{ fontSize: 10, color: '#6b7280' }}>
              {(pred.confidence * 100).toFixed(0)}% confidence
            </Text>
          </View>
        </View>
      </View>
    );
  };

  const PerformanceRow = ({ perf }: { perf: PerformanceData }) => (
    <TouchableOpacity
      style={{
        backgroundColor: '#2a3f5f',
        borderRadius: 12,
        padding: 12,
        marginBottom: 12,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <View style={{ flex: 1 }}>
        <Text style={{ fontSize: 14, fontWeight: '600', color: '#fff' }}>
          {perf.title}
        </Text>
        <View style={{ flexDirection: 'row', marginTop: 6 }}>
          <Text style={{ fontSize: 12, color: '#9ca3af', marginRight: 12 }}>
            📊 {perf.plays} plays
          </Text>
          <Text style={{ fontSize: 12, color: '#9ca3af' }}>
            💿 {perf.sales} sales
          </Text>
        </View>
      </View>
      <View style={{ alignItems: 'flex-end' }}>
        <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#10b981' }}>
          ₦{perf.revenue.toLocaleString()}
        </Text>
        <Text
          style={{
            fontSize: 12,
            color: perf.trend >= 0 ? '#10b981' : '#ef4444',
            marginTop: 2,
          }}
        >
          {perf.trend >= 0 ? '↑' : '↓'} {Math.abs(perf.trend)}%
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: '#1f2937', justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#a855f7" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#1f2937' }}>
      <ScrollView style={{ flex: 1, padding: 16 }}>
        {/* Header */}
        <Text style={{ fontSize: 24, fontWeight: 'bold', color: '#fff', marginBottom: 16 }}>
          Your Analytics
        </Text>

        {/* Earnings Summary */}
        <View style={{ marginBottom: 20 }}>
          <View style={{ flexDirection: 'row', marginBottom: 12 }}>
            <EarningsCard label="Today" value={earnings.today} />
            <EarningsCard label="This Week" value={earnings.week} />
          </View>
          <View style={{ flexDirection: 'row' }}>
            <EarningsCard label="This Month" value={earnings.month} />
            <EarningsCard label="Total Earnings" value={earnings.total} />
          </View>
        </View>

        {/* Chart */}
        {chartData && (
          <View style={{ marginBottom: 20, backgroundColor: '#2a3f5f', borderRadius: 12, padding: 12 }}>
            <Text style={{ fontSize: 14, fontWeight: '600', color: '#fff', marginBottom: 12 }}>
              Earnings Trend
            </Text>
            <LineChart
              data={{
                labels: chartData.labels,
                datasets: [
                  {
                    data: chartData.data,
                    color: () => '#a855f7',
                  },
                ],
              }}
              width={width - 56}
              height={200}
              chartConfig={{
                backgroundGradientFrom: '#2a3f5f',
                backgroundGradientTo: '#2a3f5f',
                decimalPlaces: 0,
                color: () => '#6b7280',
                labelColor: () => '#9ca3af',
              }}
            />
          </View>
        )}

        {/* Time Range Filter */}
        <View style={{ flexDirection: 'row', marginBottom: 20 }}>
          {(['week', 'month', 'year'] as const).map(range => (
            <TouchableOpacity
              key={range}
              style={{
                flex: 1,
                paddingVertical: 8,
                paddingHorizontal: 12,
                marginHorizontal: 4,
                backgroundColor: timeRange === range ? '#a855f7' : '#2a3f5f',
                borderRadius: 8,
              }}
              onPress={() => setTimeRange(range)}
            >
              <Text
                style={{
                  textAlign: 'center',
                  color: timeRange === range ? '#fff' : '#9ca3af',
                  fontWeight: '600',
                }}
              >
                {range.charAt(0).toUpperCase() + range.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* AI Predictions */}
        <View style={{ marginBottom: 20 }}>
          <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#fff', marginBottom: 12 }}>
            🤖 AI Predictions
          </Text>
          {predictions.map((pred, idx) => (
            <PredictionCard key={idx} pred={pred} />
          ))}
        </View>

        {/* Top Performing Beats */}
        <View>
          <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#fff', marginBottom: 12 }}>
            Top Performing Beats
          </Text>
          {performances.map(perf => (
            <PerformanceRow key={perf.beatId} perf={perf} />
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
