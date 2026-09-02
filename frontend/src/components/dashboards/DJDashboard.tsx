'use client';

import Link from 'next/link';

export function DJDashboard() {
  return (
    <div className="bg-background text-on-background min-h-screen">
      {/* Header Section */}
      <header className="px-margin-mobile lg:px-margin-desktop py-stack-md lg:py-stack-lg border-b border-outline-variant/10 bg-surface">
        <div className="max-w-container-max mx-auto flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface mb-2">
              DJ Dashboard
            </h2>
            <p className="text-on-surface-variant font-body-lg">
              Manage your mixes, submissions, and earnings.
            </p>
          </div>
          <div className="flex gap-3">
            <button className="bg-surface-container text-on-surface font-label-sm text-label-sm uppercase py-2 px-4 rounded ghost-border hover:bg-surface-container-high transition-colors">
              View Public Profile
            </button>
            <button className="bg-secondary text-on-secondary-fixed font-label-sm text-label-sm uppercase py-2 px-4 rounded hover:opacity-90 transition-opacity">
              Create Mixtape
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 px-margin-mobile lg:px-margin-desktop py-stack-lg bg-background">
        <div className="max-w-container-max mx-auto grid grid-cols-1 lg:grid-cols-12 gap-stack-md">
          {/* Left Column (Main Workflows) */}
          <div className="lg:col-span-8 flex flex-col gap-stack-lg">
            {/* Mixtape Management Bento */}
            <section>
              <div className="flex items-center justify-between mb-stack-sm">
                <h3 className="font-headline-md text-headline-md text-on-surface">
                  Mixtape Management
                </h3>
                <a href="#" className="text-secondary font-label-sm text-label-sm uppercase hover:underline">
                  View All
                </a>
              </div>

              {/* Bento Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Card 1 */}
                <div className="bg-surface-container-low ghost-border rounded-lg overflow-hidden group relative">
                  <div className="h-40 bg-surface-container-high relative">
                    <img
                      alt="Mix Cover"
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuDw1kWFmqohQa5C3xfo-rdanovcYw6Jrf1e0OV_UyO9Sh9gT8lqJV48lGpd1f91_c0vluQA5XCDlaWULJ9jPpi9_Uxt2wrlxZPm0Nj_1JdQR2la8iUO3IVevy5b1Y6j8oAjTClpX2_ZMHHMYdS8F_aanGKkoAnKWsgLyW4JlU2i9KDhopl3B8XSJXlzHyjm-13OsmIitsdpKpGazg1WxUYkbAaSg3NVp5ek6PpfgPb0aoW_Z1UAiK9z"
                      className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity"
                    />
                    <div className="absolute top-2 right-2 bg-secondary text-on-secondary-fixed font-label-sm text-label-sm px-2 py-1 rounded uppercase">
                      Premium
                    </div>
                  </div>
                  <div className="p-4">
                    <h4 className="font-body-lg text-on-surface font-semibold mb-1 truncate">
                      Midnight Voyage Vol. 4
                    </h4>
                    <p className="text-on-surface-variant text-sm mb-4">Deep House • 1h 20m</p>
                    <div className="flex items-center justify-between">
                      <span className="text-secondary font-body-md">$15.00</span>
                      <div className="flex gap-2">
                        <button className="p-2 text-on-surface-variant hover:text-secondary transition-colors">
                          <span className="material-symbols-outlined text-[20px]">edit</span>
                        </button>
                        <button className="p-2 text-on-surface-variant hover:text-secondary transition-colors">
                          <span className="material-symbols-outlined text-[20px]">bar_chart</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card 2 */}
                <div className="bg-surface-container-low ghost-border rounded-lg overflow-hidden group relative">
                  <div className="h-40 bg-surface-container-high relative">
                    <img
                      alt="Mix Cover"
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuCmsdZjcSAm4hw-693vRe6nG3SwfQSvnT-2ykogv0ZCikTdiHccg2Gm5mUnr64CcDldruSAerviQIO3TMh3F_uchCtGEIu3oYR9Xz-oN3ES-Bq5b-kmF92_Q5g-BxL799nvi-vX3eMMCgQS20RU6rSehQObn9kvyztd_RVlT4RY3QsNEfxyjFuEA7iZ60As0yik3bRJcDTju2nb4QLYSYGhEpLqZCL2vRwkjp8vR-6TI2qv5Ah8zH_A"
                      className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity"
                    />
                    <div className="absolute top-2 right-2 bg-surface text-on-surface font-label-sm text-label-sm px-2 py-1 rounded uppercase ghost-border">
                      Free
                    </div>
                  </div>
                  <div className="p-4">
                    <h4 className="font-body-lg text-on-surface font-semibold mb-1 truncate">
                      Summer Anthems
                    </h4>
                    <p className="text-on-surface-variant text-sm mb-4">Afrobeat • 45m</p>
                    <div className="flex items-center justify-between">
                      <span className="text-on-surface-variant font-body-md">2.4k Plays</span>
                      <div className="flex gap-2">
                        <button className="p-2 text-on-surface-variant hover:text-secondary transition-colors">
                          <span className="material-symbols-outlined text-[20px]">edit</span>
                        </button>
                        <button className="p-2 text-on-surface-variant hover:text-secondary transition-colors">
                          <span className="material-symbols-outlined text-[20px]">bar_chart</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Submissions Inbox */}
            <section className="bg-surface-container-lowest ghost-border rounded-lg p-stack-md">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <h3 className="font-headline-md text-headline-md text-on-surface">
                    Submissions Inbox
                  </h3>
                  <span className="bg-secondary text-on-secondary-fixed font-label-sm px-2 py-0.5 rounded-full">
                    3 New
                  </span>
                </div>
                <button className="text-on-surface-variant hover:text-on-surface transition-colors">
                  <span className="material-symbols-outlined">filter_list</span>
                </button>
              </div>

              {/* Submissions List */}
              <div className="flex flex-col">
                {/* List Item 1 */}
                <div className="flex items-center justify-between py-4 border-b border-outline-variant/10 group">
                  <div className="flex items-center gap-4">
                    <img
                      alt="Artist"
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuDqO7FE3reE_0M3p7m2OlM31R1jk1b0KVAbwQ6HJbB9jezLxjWDzIJcDP8BVj9JvJNaIoCV-qwanbt39XyDOJsw_cOmV0zTxbZk9NUDn_yZ0GtMCEK-z0wU6m9ukd-SSqhR15dYhrCQYe0mG82DH3APIdWMuDzwMQ1pT7jB4TM2cr-IbjKAcdF93snu1B4_FT5gkpWcys_tuZBQIVFOvtjMW7AQJPWjtuFO9lXewwS9Ucnml1QDMxNo"
                      className="w-12 h-12 rounded-full object-cover ghost-border"
                    />
                    <div>
                      <p className="font-body-md text-on-surface font-medium">Elevate - Original Mix</p>
                      <p className="text-sm text-on-surface-variant">by YNXG • Amapiano</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="text-secondary font-label-sm text-label-sm uppercase hover:underline">
                      Review
                    </button>
                    <button className="text-error hover:text-error-container transition-colors">
                      <span className="material-symbols-outlined text-[20px]">close</span>
                    </button>
                  </div>
                </div>

                {/* List Item 2 */}
                <div className="flex items-center justify-between py-4 border-b border-outline-variant/10 group">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-surface-container-high flex items-center justify-center ghost-border text-on-surface-variant">
                      <span className="material-symbols-outlined">music_note</span>
                    </div>
                    <div>
                      <p className="font-body-md text-on-surface font-medium">Night Rider</p>
                      <p className="text-sm text-on-surface-variant">by DJ K-Swiss • Tech House</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="text-secondary font-label-sm text-label-sm uppercase hover:underline">
                      Review
                    </button>
                    <button className="text-error hover:text-error-container transition-colors">
                      <span className="material-symbols-outlined text-[20px]">close</span>
                    </button>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* Right Column (Analytics & Calendar) */}
          <div className="lg:col-span-4 flex flex-col gap-stack-md">
            {/* Earnings Summary Card */}
            <div className="bg-surface-container-lowest ghost-border rounded-lg p-stack-md relative overflow-hidden">
              <div
                className="absolute inset-0 opacity-10 pointer-events-none"
                style={{
                  backgroundImage:
                    'radial-gradient(circle at 100% 0%, #D4AF37 0%, transparent 50%)',
                }}
              ></div>
              <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase mb-2">
                Total Earnings (This Month)
              </h3>
              <div className="font-display-lg text-[48px] text-on-surface mb-6">
                $4,250
                <span className="text-secondary text-lg ml-2">↑ 12%</span>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b border-outline-variant/10 pb-2">
                  <span className="text-on-surface-variant">Mix Sales</span>
                  <span className="text-on-surface font-medium">$3,100</span>
                </div>
                <div className="flex justify-between items-center border-b border-outline-variant/10 pb-2">
                  <span className="text-on-surface-variant">Tips & Donations</span>
                  <span className="text-on-surface font-medium">$850</span>
                </div>
                <div className="flex justify-between items-center pb-2">
                  <span className="text-on-surface-variant">Bookings Deposit</span>
                  <span className="text-safari-clay font-medium">$300</span>
                </div>
              </div>
              <button className="w-full mt-6 bg-transparent border border-safari-clay text-safari-clay font-label-sm text-label-sm uppercase py-2 rounded hover:bg-safari-clay/10 transition-colors">
                View Full Report
              </button>
            </div>

            {/* Booking Calendar Mini */}
            <div className="bg-surface-container-lowest ghost-border rounded-lg p-stack-md">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-headline-md text-headline-md text-on-surface text-[22px]">
                  Upcoming Gigs
                </h3>
                <button className="text-on-surface-variant hover:text-on-surface transition-colors">
                  <span className="material-symbols-outlined">calendar_month</span>
                </button>
              </div>

              {/* Gigs List */}
              <div className="space-y-3">
                {/* Gig 1 */}
                <div className="flex gap-4 p-3 bg-surface-container-low rounded ghost-border">
                  <div className="flex flex-col items-center justify-center min-w-[50px] border-r border-outline-variant/20 pr-4">
                    <span className="text-secondary font-label-sm uppercase">Oct</span>
                    <span className="font-headline-md text-on-surface">24</span>
                  </div>
                  <div>
                    <h4 className="font-body-md text-on-surface font-medium">Club Silencio</h4>
                    <p className="text-sm text-on-surface-variant flex items-center gap-1 mt-1">
                      <span className="material-symbols-outlined text-[14px]">location_on</span>
                      Paris, FR
                    </p>
                  </div>
                </div>

                {/* Gig 2 */}
                <div className="flex gap-4 p-3 bg-surface-container-low rounded ghost-border">
                  <div className="flex flex-col items-center justify-center min-w-[50px] border-r border-outline-variant/20 pr-4">
                    <span className="text-safari-clay font-label-sm uppercase">Nov</span>
                    <span className="font-headline-md text-on-surface">02</span>
                  </div>
                  <div>
                    <h4 className="font-body-md text-on-surface font-medium">Boiler Room Set</h4>
                    <p className="text-sm text-on-surface-variant flex items-center gap-1 mt-1">
                      <span className="material-symbols-outlined text-[14px]">location_on</span>
                      London, UK
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Trending Collab Artists Section */}
        <section className="max-w-container-max mx-auto mt-stack-lg border-t border-outline-variant/10 pt-stack-lg">
          <div className="flex items-center justify-between mb-stack-md">
            <h3 className="font-headline-md text-headline-md text-on-surface">
              Trending Collab Artists
            </h3>
            <div className="flex gap-2">
              <button className="w-8 h-8 rounded-full border border-outline-variant/20 flex items-center justify-center text-on-surface-variant hover:text-secondary hover:border-secondary transition-colors">
                <span className="material-symbols-outlined text-[18px]">chevron_left</span>
              </button>
              <button className="w-8 h-8 rounded-full border border-outline-variant/20 flex items-center justify-center text-on-surface-variant hover:text-secondary hover:border-secondary transition-colors">
                <span className="material-symbols-outlined text-[18px]">chevron_right</span>
              </button>
            </div>
          </div>

          {/* Artists Carousel */}
          <div className="flex gap-4 overflow-x-auto pb-4 snap-x scrollbar-hide">
            {/* Artist Card 1 */}
            <div className="min-w-[200px] bg-surface-container-lowest ghost-border rounded-lg p-4 flex flex-col items-center text-center snap-start">
              <img
                alt="Artist"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuBD2qB3Qy-WsP_KdU0VIUP_EWLS06drj0WseY74L229m5ZB6XztbsW2LDanwX8oXf6dNYzBXN82iMgpwve2skAFdWtgeor3O63AMpOS7xp1ir2Co2eE56ty_imm9Iqu_DF_KctnHVDPEEp4cnsiZbFWqtCuFucWjlpV2cwyAG395m_OSBSv7EEAAJePMrF9TBjaY5z0i4dFTKKHvcTm799DMLZ_6kKbXJ_LqUHWUESXUlKVmLGsUDb0"
                className="w-24 h-24 rounded-full object-cover mb-4 ghost-border"
              />
              <h4 className="font-body-md text-on-surface font-medium">Lumiere</h4>
              <p className="text-sm text-on-surface-variant mb-3">Vocalist</p>
              <button className="px-3 py-1 bg-surface-container text-on-surface font-label-sm text-label-sm uppercase rounded-full ghost-border hover:text-secondary transition-colors">
                Invite
              </button>
            </div>

            {/* Artist Card 2 */}
            <div className="min-w-[200px] bg-surface-container-lowest ghost-border rounded-lg p-4 flex flex-col items-center text-center snap-start">
              <img
                alt="Artist"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuB-pimt0E6UapzWv3BBHPQofHMWpavwTX48x8p27byaXQlDVVEy3fbV1Bd0FrNVDPuvSP0sox77EqBdzZWsAao2aH21ZK-gxSaqEbZ9gA5h1JbtQQTM_jvYYgBPOXnSsKSEzipXxId53dNzaTxESB0J6UTkAF1lVM8NudMgBCHKPmy3hGFTIX4puEsuTXugjYnqL7gTLvhveqaptAw24qSytW_YHYeqJVIHGoGFPx0LNKY7uGXRBbAo"
                className="w-24 h-24 rounded-full object-cover mb-4 ghost-border"
              />
              <h4 className="font-body-md text-on-surface font-medium">Brass Tactics</h4>
              <p className="text-sm text-on-surface-variant mb-3">Instrumentalist</p>
              <button className="px-3 py-1 bg-surface-container text-on-surface font-label-sm text-label-sm uppercase rounded-full ghost-border hover:text-secondary transition-colors">
                Invite
              </button>
            </div>

            {/* Artist Card 3 */}
            <div className="min-w-[200px] bg-surface-container-lowest ghost-border rounded-lg p-4 flex flex-col items-center text-center snap-start">
              <div className="w-24 h-24 rounded-full bg-surface-container-high flex items-center justify-center mb-4 ghost-border text-on-surface-variant">
                <span className="material-symbols-outlined text-[32px]">person</span>
              </div>
              <h4 className="font-body-md text-on-surface font-medium">Kizo Beat</h4>
              <p className="text-sm text-on-surface-variant mb-3">Producer</p>
              <button className="px-3 py-1 bg-surface-container text-on-surface font-label-sm text-label-sm uppercase rounded-full ghost-border hover:text-secondary transition-colors">
                Invite
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
