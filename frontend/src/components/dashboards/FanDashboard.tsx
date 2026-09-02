'use client';

export function FanDashboard() {
  return (
    <div className="bg-background text-on-background min-h-screen">
      {/* Header */}
      <header className="px-margin-mobile md:px-margin-desktop py-stack-md border-b border-outline-variant/10 bg-surface">
        <div className="max-w-container-max mx-auto">
          <h1 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface mb-2">
            Welcome Back, Alex
          </h1>
          <p className="text-on-surface-variant font-body-lg">
            Discover new sounds and support your favorite artists.
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-stack-md">
          {/* Discovery Feed (Main) */}
          <section className="lg:col-span-8 bg-surface-container-low ghost-border rounded-xl overflow-hidden flex flex-col">
            <div className="p-6 border-b border-outline-variant/20 flex justify-between items-center">
              <h2 className="font-headline-md text-on-surface">Discovery Feed</h2>
              <button className="text-secondary hover:text-secondary-fixed transition-colors">
                <span className="material-symbols-outlined">filter_list</span>
              </button>
            </div>

            {/* Feed Items */}
            <div className="flex flex-col divide-y divide-outline-variant/10">
              {/* Feed Item 1 */}
              <div className="p-6 hover:bg-surface-container transition-colors group cursor-pointer">
                <div className="flex gap-4">
                  <img
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuDiCZTnRQ4kQ2ooek1CTqBxK6ymo9Xp711P4Jp976xfbUYR4ZqHD4WMobiuNjKPtDjEp7Pcj4YphdsuNZT1-w5cfPYKe1Vo850H48Bw4IrFFdJVYoiIkeLCed7yI45-wqALkbRxnYF9wgiH5JgjppbuWbvhfmj-CcWcrTYzWG0KcG6XzxIhScOBDgVoklL2IiCTs2W9NQTvbBwLcJpCzYUj0VnIqtJBbsX8R7_hkGrE3FRYxes05Qy1"
                    alt="Album art"
                    className="w-16 h-16 rounded object-cover ghost-border"
                  />
                  <div className="flex-1">
                    <p className="font-body-md text-on-surface font-semibold">Lagos Nights</p>
                    <p className="font-label-sm text-on-surface-variant mb-2">Oluwa Burna</p>
                    <p className="font-body-md text-body-md text-on-surface-variant text-sm line-clamp-2">
                      A cinematic journey through the vibrant soundscape of Lagos after dark.
                    </p>
                  </div>
                  <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-secondary hover:text-secondary-fixed">
                    <span className="material-symbols-outlined text-[24px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                      play_circle
                    </span>
                  </button>
                </div>
              </div>

              {/* Feed Item 2 */}
              <div className="p-6 hover:bg-surface-container transition-colors group cursor-pointer">
                <div className="flex gap-4">
                  <img
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuB3g7pPdCwY-R8Rl8rFYgzOZ9i0jC1khOZV_PP3xCl9T366MIlp5qZ94qXpUS0hjYBfCws7TtX_fJy1pBnC_g_EiwJcw37uqE0ojcMsJz4aoLuNDfhtE5xuv28egTHivmoa5qEsUzZqim1IaKBJH3k43TZo1xqLRqBFJb_1qWxi7sgdM_XRCu7bHq8aYTwjKT9d4uerisq5Wwy_69LGwA_KeKZDaVIF7NY12Bvbsc1o1BUFu_vQGUHn"
                    alt="Album art"
                    className="w-16 h-16 rounded object-cover ghost-border"
                  />
                  <div className="flex-1">
                    <p className="font-body-md text-on-surface font-semibold">Heritage</p>
                    <p className="font-label-sm text-on-surface-variant mb-2">Oluwa Burna ft. Zaria</p>
                    <p className="font-body-md text-body-md text-on-surface-variant text-sm line-clamp-2">
                      A fusion of traditional African elements with modern production techniques.
                    </p>
                  </div>
                  <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-secondary hover:text-secondary-fixed">
                    <span className="material-symbols-outlined text-[24px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                      play_circle
                    </span>
                  </button>
                </div>
              </div>

              {/* Feed Item 3 */}
              <div className="p-6 hover:bg-surface-container transition-colors group cursor-pointer">
                <div className="flex gap-4">
                  <img
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuD9Di7KiXy4zbrE1nWkeGGddXyrzkp_7oD9-WbzCrpKRiEsASbLPpM2iahcBp0EaQ-p9f7NA9poSILDkZewcNyaGXMZHoCGe146Vp4_rvDeLBNiSXMb6EWI-Q6ARFp1zIet7ZntCYEv5EFGIHWH1W6R4hHhjl-sYucW_69iE4teNCbAHXj1tllUX2irFOMlrQ22Pj6DIIqJJdtSFDiYzgOFOQIzsmgs-o3yiqaWbgtYxJo_oEwgu_rl"
                    alt="Album art"
                    className="w-16 h-16 rounded object-cover ghost-border"
                  />
                  <div className="flex-1">
                    <p className="font-body-md text-on-surface font-semibold">Summer Vibes</p>
                    <p className="font-label-sm text-on-surface-variant mb-2">Zaria & Collective</p>
                    <p className="font-body-md text-body-md text-on-surface-variant text-sm line-clamp-2">
                      Uplifting melodies perfect for the sunny season.
                    </p>
                  </div>
                  <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-secondary hover:text-secondary-fixed">
                    <span className="material-symbols-outlined text-[24px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                      play_circle
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Sidebar */}
          <aside className="lg:col-span-4 space-y-stack-md">
            {/* Featured Artists */}
            <div className="bg-surface-container-low ghost-border rounded-lg p-stack-md">
              <h3 className="font-headline-md text-on-surface mb-4">Featured Artists</h3>
              <div className="space-y-3">
                {/* Artist 1 */}
                <div className="flex items-center gap-3 p-2 hover:bg-surface-container rounded transition-colors cursor-pointer group">
                  <img
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuDiCZTnRQ4kQ2ooek1CTqBxK6ymo9Xp711P4Jp976xfbUYR4ZqHD4WMobiuNjKPtDjEp7Pcj4YphdsuNZT1-w5cfPYKe1Vo850H48Bw4IrFFdJVYoiIkeLCed7yI45-wqALkbRxnYF9wgiH5JgjppbuWbvhfmj-CcWcrTYzWG0KcG6XzxIhScOBDgVoklL2IiCTs2W9NQTvbBwLcJpCzYUj0VnIqtJBbsX8R7_hkGrE3FRYxes05Qy1"
                    alt="Artist"
                    className="w-12 h-12 rounded-full object-cover ghost-border"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="font-body-md text-on-surface font-semibold truncate">Oluwa Burna</p>
                    <p className="font-label-sm text-on-surface-variant text-xs">2.4M listeners</p>
                  </div>
                  <button className="opacity-0 group-hover:opacity-100 transition-opacity text-secondary hover:text-secondary-fixed font-label-sm text-label-sm uppercase">
                    Follow
                  </button>
                </div>

                {/* Artist 2 */}
                <div className="flex items-center gap-3 p-2 hover:bg-surface-container rounded transition-colors cursor-pointer group">
                  <img
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuB3g7pPdCwY-R8Rl8rFYgzOZ9i0jC1khOZV_PP3xCl9T366MIlp5qZ94qXpUS0hjYBfCws7TtX_fJy1pBnC_g_EiwJcw37uqE0ojcMsJz4aoLuNDfhtE5xuv28egTHivmoa5qEsUzZqim1IaKBJH3k43TZo1xqLRqBFJb_1qWxi7sgdM_XRCu7bHq8aYTwjKT9d4uerisq5Wwy_69LGwA_KeKZDaVIF7NY12Bvbsc1o1BUFu_vQGUHn"
                    alt="Artist"
                    className="w-12 h-12 rounded-full object-cover ghost-border"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="font-body-md text-on-surface font-semibold truncate">Zaria</p>
                    <p className="font-label-sm text-on-surface-variant text-xs">1.8M listeners</p>
                  </div>
                  <button className="opacity-0 group-hover:opacity-100 transition-opacity text-secondary hover:text-secondary-fixed font-label-sm text-label-sm uppercase">
                    Follow
                  </button>
                </div>
              </div>
            </div>

            {/* Listening Stats */}
            <div className="bg-surface-container-low ghost-border rounded-lg p-stack-md">
              <h3 className="font-headline-md text-on-surface mb-4">Your Stats</h3>
              <div className="space-y-3">
                <div>
                  <p className="font-label-sm text-on-surface-variant uppercase tracking-wider mb-1">
                    This Month
                  </p>
                  <p className="font-headline-md text-secondary">4.2K</p>
                  <p className="font-label-sm text-on-surface-variant text-xs">Tracks Played</p>
                </div>
                <div className="h-px w-full bg-outline-variant/20"></div>
                <div>
                  <p className="font-label-sm text-on-surface-variant uppercase tracking-wider mb-1">
                    Favorites
                  </p>
                  <p className="font-headline-md text-secondary">142</p>
                  <p className="font-label-sm text-on-surface-variant text-xs">Total Saved</p>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-surface-container-low ghost-border rounded-lg p-stack-md">
              <h3 className="font-headline-md text-on-surface mb-4">Recommendations</h3>
              <button className="w-full py-3 rounded bg-secondary text-on-secondary font-label-sm text-label-sm uppercase font-bold hover:bg-secondary-fixed transition-colors">
                Discover New Music
              </button>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
