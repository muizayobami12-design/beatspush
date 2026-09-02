'use client';

import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';

export function ArtistDashboard() {
  const { user } = useAuthStore();
  const artistName = user?.fullName || 'Artist Name';
  const genre = 'Afro-Fusion';

  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col md:flex-row">
      {/* Main Content */}
      <main className="flex-1">
        {/* Cinematic Hero Section */}
        <section className="relative w-full h-[60vh] min-h-[500px] flex items-end pb-stack-lg px-margin-mobile md:px-margin-desktop">
          {/* Background Image */}
          <div className="absolute inset-0 w-full h-full z-0">
            <div
              className="w-full h-full bg-cover bg-center absolute inset-0"
              style={{
                backgroundImage:
                  'url(https://lh3.googleusercontent.com/aida-public/AB6AXuAIjFkxmpb039dBNxYTeu8QYWZ1BbfxaKSR5xtTAh1JPA2CDD6X2Gbujtv1JZoG3hntfp3IfOlYo08PTfQsTeCoZMbzFFoiD5ymKepVPRAxU392LQpY7dHk5Iq9HRACbk1l3ggOKyNHFZmrshIbBpKE3dPTe_6nQggwlvlYONDXaMkvc6T6q4npSqihUGrck972x3_cXj8RQKE2HZfyvu2DkmsD0-nVClVWCZMWQ4PqaEB5IerOAfR7)',
              }}
            ></div>
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent"></div>
          </div>

          {/* Hero Content */}
          <div className="relative z-10 w-full max-w-container-max mx-auto flex flex-col md:flex-row justify-between items-end gap-stack-md">
            <div className="flex-1 max-w-2xl">
              {/* Genre Badge */}
              <div className="flex items-center gap-2 mb-4">
                <span className="px-2 py-1 rounded-full bg-[#8B5E3C] text-white font-label-sm text-[10px] uppercase tracking-wider">
                  {genre}
                </span>
                <span className="px-2 py-1 rounded-full bg-surface-container-high text-on-surface-variant font-label-sm text-[10px] uppercase tracking-wider ghost-border">
                  Verified
                </span>
              </div>

              {/* Artist Name */}
              <h1 className="font-display-lg text-headline-lg-mobile md:text-display-lg text-primary mb-2">
                {artistName}
              </h1>

              {/* Bio */}
              <p className="font-body-lg text-body-md md:text-body-lg text-on-surface-variant mb-6 max-w-xl">
                Pioneering the global soundscape with a fusion of traditional African rhythms and contemporary electronic textures. Chart-topping producer and independent visionary.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-wrap items-center gap-4">
                <button className="px-6 py-3 rounded muted-gold-bg text-black font-label-sm text-label-sm uppercase tracking-wider hover:bg-opacity-90 transition-opacity flex items-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">person_add</span>
                  Follow
                </button>
                <button className="px-6 py-3 rounded border border-[#8B5E3C] text-primary font-label-sm text-label-sm uppercase tracking-wider hover:bg-surface-container-high transition-colors flex items-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">volunteer_activism</span>
                  Tip Artist
                </button>
              </div>
            </div>

            {/* Stats Glass Panel */}
            <div className="glass-panel p-4 rounded-xl ghost-border flex items-center gap-6 w-full md:w-auto">
              <div className="flex flex-col">
                <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-1">
                  Monthly Listeners
                </span>
                <span className="font-headline-md text-headline-md text-secondary">2.4M</span>
              </div>
              <div className="w-px h-12 bg-outline-variant/30"></div>
              <div className="flex flex-col">
                <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mb-1">
                  Global Rank
                </span>
                <span className="font-headline-md text-headline-md text-primary">#42</span>
              </div>
            </div>
          </div>
        </section>

        {/* Main Content Grid */}
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
            {/* Left Column: Top Tracks */}
            <div className="lg:col-span-2 space-y-stack-lg">
              {/* Top Tracks Section */}
              <section>
                <h2 className="font-headline-md text-headline-md text-primary mb-6">
                  Top Tracks
                </h2>

                <div className="flex flex-col">
                  {/* Track Row 1 */}
                  <div className="flex items-center justify-between py-3 border-b border-outline-variant/15 hover:bg-surface-container-low transition-colors group px-2 cursor-pointer">
                    <div className="flex items-center gap-4">
                      <span className="font-label-sm text-label-sm text-on-surface-variant w-4 text-right">
                        1
                      </span>
                      <div className="w-10 h-10 rounded overflow-hidden ghost-border relative">
                        <img
                          alt="Track art"
                          src="https://lh3.googleusercontent.com/aida-public/AB6AXuD9Di7KiXy4zbrE1nWkeGGddXyrzkp_7oD9-WbzCrpKRiEsASbLPpM2iahcBp0EaQ-p9f7NA9poSILDkZewcNyaGXMZHoCGe146Vp4_rvDeLBNiSXMb6EWI-Q6ARFp1zIet7ZntCYEv5EFGIHWH1W6R4hHhjl-sYucW_69iE4teNCbAHXj1tllUX2irFOMlrQ22Pj6DIIqJJdtSFDiYzgOFOQIzsmgs-o3yiqaWbgtYxJo_oEwgu_rl"
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <span
                            className="material-symbols-outlined text-primary text-[20px]"
                            style={{ fontVariationSettings: "'FILL' 1" }}
                          >
                            play_arrow
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-col">
                        <span className="font-body-md text-body-md text-primary">Lagos Nights</span>
                        <span className="font-label-sm text-label-sm text-on-surface-variant">
                          {artistName} • 12.4M streams
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="font-label-sm text-label-sm text-on-surface-variant hidden md:inline-block">
                        3:42
                      </span>
                      <button className="text-on-surface-variant hover:text-secondary transition-colors">
                        <span className="material-symbols-outlined text-[20px]">more_horiz</span>
                      </button>
                    </div>
                  </div>

                  {/* Track Row 2 */}
                  <div className="flex items-center justify-between py-3 border-b border-outline-variant/15 hover:bg-surface-container-low transition-colors group px-2 cursor-pointer">
                    <div className="flex items-center gap-4">
                      <span className="font-label-sm text-label-sm text-on-surface-variant w-4 text-right">
                        2
                      </span>
                      <div className="w-10 h-10 rounded overflow-hidden ghost-border relative">
                        <img
                          alt="Track art"
                          src="https://lh3.googleusercontent.com/aida-public/AB6AXuB3g7pPdCwY-R8Rl8rFYgzOZ9i0jC1khOZV_PP3xCl9T366MIlp5qZ94qXpUS0hjYBfCws7TtX_fJy1pBnC_g_EiwJcw37uqE0ojcMsJz4aoLuNDfhtE5xuv28egTHivmoa5qEsUzZqim1IaKBJH3k43TZo1xqLRqBFJb_1qWxi7sgdM_XRCu7bHq8aYTwjKT9d4uerisq5Wwy_69LGwA_KeKZDaVIF7NY12Bvbsc1o1BUFu_vQGUHn"
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <span
                            className="material-symbols-outlined text-primary text-[20px]"
                            style={{ fontVariationSettings: "'FILL' 1" }}
                          >
                            play_arrow
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-col">
                        <span className="font-body-md text-body-md text-primary">Heritage</span>
                        <span className="font-label-sm text-label-sm text-on-surface-variant">
                          {artistName} ft. Zaria • 8.1M streams
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="font-label-sm text-label-sm text-on-surface-variant hidden md:inline-block">
                        4:15
                      </span>
                      <button className="text-on-surface-variant hover:text-secondary transition-colors">
                        <span className="material-symbols-outlined text-[20px]">more_horiz</span>
                      </button>
                    </div>
                  </div>
                </div>
              </section>
            </div>

            {/* Right Column: Sidebar */}
            <div className="space-y-stack-md">
              {/* Fan Club Card */}
              <div className="bg-[#1A1A1A] rounded-xl p-6 ghost-border relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-secondary/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

                <div className="flex items-center gap-3 mb-4">
                  <span
                    className="material-symbols-outlined text-secondary text-[24px]"
                    style={{ fontVariationSettings: "'FILL' 1" }}
                  >
                    stars
                  </span>
                  <h3 className="font-headline-md text-xl text-primary font-semibold">
                    The Inner Circle
                  </h3>
                </div>

                <p className="font-body-md text-sm text-on-surface-variant mb-6">
                  Join the exclusive fan club for early access to releases, stems, and private studio streams.
                </p>

                <div className="flex items-end gap-1 mb-6">
                  <span className="font-headline-md text-3xl text-secondary font-bold">
                    ₦1,000
                  </span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant mb-1 uppercase">
                    / month
                  </span>
                </div>

                <button className="w-full py-3 rounded muted-gold-bg text-black font-label-sm text-label-sm uppercase tracking-wider hover:bg-opacity-90 transition-opacity">
                  Subscribe Now
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
