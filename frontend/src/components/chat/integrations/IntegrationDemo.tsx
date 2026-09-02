/**
 * Integration Demo Component
 * Demonstrates Profile and Social Media integrations
 * Use this component for manual testing and verification
 */

'use client';

import React, { useState } from 'react';
import { ProfileIntegration, useProfileChat } from './ProfileIntegration';
import { SocialMediaIntegration, useSocialMediaAI } from './SocialMediaIntegration';

/**
 * Profile Integration Demo
 */
export function ProfileIntegrationDemo() {
  const [bio, setBio] = useState('');
  const [artistStatement, setArtistStatement] = useState('');

  const { writeBio, craftArtistStatement, suggestImprovements, refineBio, openChat } = useProfileChat({
    onBioUpdate: (newBio, variant) => {
      setBio(newBio);
      console.log(`✅ Bio updated (${variant}):`, newBio);
    },
    onArtistStatementUpdate: (statement) => {
      setArtistStatement(statement);
      console.log('✅ Artist statement updated:', statement);
    },
  });

  return (
    <ProfileIntegration
      bio="Trap and Hip-Hop producer from LA. Making beats that hit different."
      fullName="John Producer"
      location="Los Angeles, CA"
      genres={['Trap', 'Hip-Hop', 'R&B']}
      socialLinks={{
        instagram: '@johnproducer',
        twitter: '@johnproducer',
        spotify: 'johnproducer',
      }}
      beatsCount={145}
      followersCount={2350}
      achievements={['100k+ streams', 'Featured on Spotify playlist', 'Collab with major artist']}
      onBioUpdate={(newBio, variant) => setBio(newBio)}
      onArtistStatementUpdate={(statement) => setArtistStatement(statement)}
    >
      <div className="space-y-6 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-gray-900">Profile Integration Demo</h2>
        
        {/* Bio Section */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            Bio
          </label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Your bio will appear here..."
            className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Artist Statement Section */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            Artist Statement
          </label>
          <textarea
            value={artistStatement}
            onChange={(e) => setArtistStatement(e.target.value)}
            placeholder="Your artist statement will appear here..."
            className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={writeBio}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            ✨ Write Bio
          </button>
          <button
            onClick={craftArtistStatement}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            📝 Artist Statement
          </button>
          <button
            onClick={suggestImprovements}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            💡 Suggest Improvements
          </button>
          <button
            onClick={openChat}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            💬 Open AI Chat
          </button>
        </div>

        {/* Refinement Options */}
        {bio && (
          <div className="pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-2">Refine your bio:</p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => refineBio('Make it more professional')}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                More Professional
              </button>
              <button
                onClick={() => refineBio('Add some humor')}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                Add Humor
              </button>
              <button
                onClick={() => refineBio('Make it shorter')}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                Shorter
              </button>
              <button
                onClick={() => refineBio('Make it longer and more detailed')}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                Longer
              </button>
            </div>
          </div>
        )}

        <div className="pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            💡 <strong>Tip:</strong> Click the AI buttons to open the chat interface with context-aware quick actions.
            The AI will understand your profile data and generate personalized content. Click "Use This Bio" in the chat to auto-fill!
          </p>
        </div>
      </div>
    </ProfileIntegration>
  );
}

/**
 * Social Media Integration Demo
 */
export function SocialMediaIntegrationDemo() {
  const [caption, setCaption] = useState('');
  const [hashtags, setHashtags] = useState<string[]>([]);

  const beatData = {
    contentType: 'beat' as const,
    contentTitle: 'Dark Trap Beat - "Midnight"',
    contentDescription: 'Hard-hitting trap beat with dark melody and heavy 808s. Perfect for rap vocals.',
    beatGenre: 'Trap',
    targetPlatforms: ['instagram', 'twitter', 'tiktok'] as const,
  };

  const { generateCaption, suggestHashtags, getEngagementTips, generateCaptionWithTone, openChat } = useSocialMediaAI(
    beatData,
    {
      onCaptionUpdate: (newCaption, platform, tone) => {
        setCaption(newCaption);
        console.log(`✅ Caption updated for ${platform} (${tone}):`, newCaption);
      },
      onHashtagsUpdate: (newHashtags) => {
        setHashtags(newHashtags);
        console.log('✅ Hashtags updated:', newHashtags);
      },
    }
  );

  return (
    <SocialMediaIntegration
      {...beatData}
      onCaptionUpdate={(newCaption, platform, tone) => setCaption(newCaption)}
      onHashtagsUpdate={(newHashtags) => setHashtags(newHashtags)}
    >
      <div className="space-y-6 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-gray-900">Social Media Integration Demo</h2>

        {/* Content Preview */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-2">{beatData.contentTitle}</h3>
          <p className="text-sm text-gray-600 mb-2">{beatData.contentDescription}</p>
          <span className="inline-block px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded">
            {beatData.beatGenre}
          </span>
        </div>

        {/* Caption Section */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            Caption
          </label>
          <textarea
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
            placeholder="Your caption will appear here..."
            className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500">
            {caption.length} characters
          </p>
        </div>

        {/* Platform-Specific Actions */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-gray-700">Generate Caption for Platform:</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              onClick={() => generateCaption('instagram')}
              className="p-3 border-2 border-purple-200 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-all text-left"
            >
              <div className="flex items-center gap-2">
                <span className="text-2xl">📸</span>
                <div>
                  <div className="font-medium text-sm">Instagram</div>
                  <div className="text-xs text-gray-600">Up to 2200 chars</div>
                </div>
              </div>
            </button>

            <button
              onClick={() => generateCaption('twitter')}
              className="p-3 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all text-left"
            >
              <div className="flex items-center gap-2">
                <span className="text-2xl">🐦</span>
                <div>
                  <div className="font-medium text-sm">Twitter</div>
                  <div className="text-xs text-gray-600">Max 280 chars</div>
                </div>
              </div>
            </button>

            <button
              onClick={() => generateCaption('tiktok')}
              className="p-3 border-2 border-pink-200 rounded-lg hover:border-pink-400 hover:bg-pink-50 transition-all text-left"
            >
              <div className="flex items-center gap-2">
                <span className="text-2xl">🎵</span>
                <div>
                  <div className="font-medium text-sm">TikTok</div>
                  <div className="text-xs text-gray-600">Max 150 chars</div>
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Tone Variations */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-gray-700">Or choose a tone:</p>
          <div className="flex flex-wrap gap-2">
            {['hype', 'professional', 'emotional', 'fun', 'mysterious'].map((tone) => (
              <button
                key={tone}
                onClick={() => generateCaptionWithTone(tone as any, 'all')}
                className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors capitalize"
              >
                {tone}
              </button>
            ))}
          </div>
        </div>

        {/* Additional Actions */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={suggestHashtags}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            #️⃣ Get Hashtags
          </button>
          <button
            onClick={getEngagementTips}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            💡 Engagement Tips
          </button>
          <button
            onClick={openChat}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            💬 Open AI Chat
          </button>
        </div>

        {/* Hashtags Display */}
        {hashtags.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">Hashtags:</p>
            <div className="flex flex-wrap gap-2">
              {hashtags.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-sm bg-blue-100 text-blue-700 rounded cursor-pointer hover:bg-blue-200 transition-colors"
                  onClick={() => {
                    navigator.clipboard.writeText(tag);
                    console.log('Copied:', tag);
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            💡 <strong>Tip:</strong> The AI generates 5 caption variations with different tones (hype, professional, emotional, fun, mysterious).
            Click "Use This Caption" in the chat to auto-fill your preferred variation!
          </p>
        </div>
      </div>
    </SocialMediaIntegration>
  );
}

/**
 * Combined Demo Component
 */
export default function IntegrationDemo() {
  const [activeTab, setActiveTab] = useState<'profile' | 'social'>('profile');

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('profile')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'profile'
                ? 'bg-white text-purple-600 shadow-md'
                : 'bg-white/50 text-gray-600 hover:bg-white/80'
            }`}
          >
            Profile Integration
          </button>
          <button
            onClick={() => setActiveTab('social')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'social'
                ? 'bg-white text-purple-600 shadow-md'
                : 'bg-white/50 text-gray-600 hover:bg-white/80'
            }`}
          >
            Social Media Integration
          </button>
        </div>

        {/* Content */}
        {activeTab === 'profile' && <ProfileIntegrationDemo />}
        {activeTab === 'social' && <SocialMediaIntegrationDemo />}
      </div>
    </div>
  );
}
