'use client';

export function BeatMarketplace() {
  const beats = [
    { title: 'Midnight Voyage', producer: 'Oluwa Beats', genre: 'Deep House', price: '₦25,000', plays: '12.4K' },
    { title: 'Lagos Nights', producer: 'Sound Engineer', genre: 'Afrobeats', price: '₦18,000', plays: '8.1K' },
    { title: 'Heritage', producer: 'Oluwa Beats', genre: 'Afro-Fusion', price: '₦32,000', plays: '15.2K' },
    { title: 'Summer Anthems', producer: 'Zaria', genre: 'House', price: '₦15,000', plays: '9.5K' },
  ];

  return (
    <div className="bg-background text-on-background min-h-screen">
      {/* Header */}
      <header className="border-b border-outline-variant/15 bg-surface py-stack-lg">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop">
          <h1 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-on-surface mb-2">
            Beat Marketplace
          </h1>
          <p className="text-on-surface-variant font-body-lg">
            Browse and license beats from top producers
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
          {/* Sidebar */}
          <aside className="lg:col-span-3 space-y-stack-md">
            {/* Filter Section */}
            <div className="bg-surface-container-low ghost-border rounded-lg p-stack-md">
              <h3 className="font-headline-md text-on-surface mb-4">Filters</h3>

              {/* Genre Filter */}
              <div className="mb-stack-md">
                <p className="font-label-sm text-on-surface-variant uppercase tracking-wider mb-3">
                  Genre
                </p>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" defaultChecked className="w-4 h-4" />
                    <span className="font-body-md text-on-surface">Afrobeats</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4" />
                    <span className="font-body-md text-on-surface">Hip-Hop</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4" />
                    <span className="font-body-md text-on-surface">House</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="w-4 h-4" />
                    <span className="font-body-md text-on-surface">R&B</span>
                  </label>
                </div>
              </div>

              {/* Price Filter */}
              <div className="mb-stack-md border-t border-outline-variant/15 pt-stack-md">
                <p className="font-label-sm text-on-surface-variant uppercase tracking-wider mb-3">
                  Price Range
                </p>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="price" className="w-4 h-4" />
                    <span className="font-body-md text-on-surface">Under ₦10,000</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="price" defaultChecked className="w-4 h-4" />
                    <span className="font-body-md text-on-surface">₦10,000 - ₦50,000</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="price" className="w-4 h-4" />
                    <span className="font-body-md text-on-surface">Over ₦50,000</span>
                  </label>
                </div>
              </div>

              {/* Apply Filters Button */}
              <button className="w-full mt-stack-md py-2 rounded bg-secondary text-on-secondary font-label-sm text-label-sm uppercase font-bold hover:bg-secondary-fixed transition-colors">
                Apply Filters
              </button>
            </div>

            {/* Top Producers */}
            <div className="bg-surface-container-low ghost-border rounded-lg p-stack-md">
              <h3 className="font-headline-md text-on-surface mb-4">Top Producers</h3>
              <div className="space-y-3">
                {['Oluwa Beats', 'Sound Engineer', 'Zaria'].map((producer) => (
                  <button
                    key={producer}
                    className="w-full text-left px-3 py-2 rounded hover:bg-surface-container transition-colors"
                  >
                    <p className="font-body-md text-on-surface">{producer}</p>
                    <p className="font-label-sm text-on-surface-variant text-xs">View beats</p>
                  </button>
                ))}
              </div>
            </div>
          </aside>

          {/* Beat Grid */}
          <main className="lg:col-span-9">
            {/* Sorting Header */}
            <div className="flex justify-between items-center mb-stack-md">
              <p className="font-body-lg text-on-surface-variant">Showing {beats.length} results</p>
              <select className="bg-surface-container-low border border-outline-variant rounded px-3 py-2 text-on-surface font-body-md focus:ring-1 focus:ring-secondary">
                <option>Trending</option>
                <option>Newest</option>
                <option>Most Popular</option>
                <option>Price: Low to High</option>
                <option>Price: High to Low</option>
              </select>
            </div>

            {/* Beat Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
              {beats.map((beat, idx) => (
                <div
                  key={idx}
                  className="bg-surface-container-low ghost-border rounded-lg overflow-hidden group hover:shadow-lg transition-all duration-300 flex flex-col h-full"
                >
                  {/* Beat Cover */}
                  <div className="relative h-40 bg-surface-container-high overflow-hidden">
                    <div
                      className="w-full h-full bg-gradient-to-br from-secondary/20 to-tertiary/20"
                      style={{
                        backgroundImage: `linear-gradient(135deg, rgba(233, 195, 73, 0.1) 0%, rgba(244, 187, 146, 0.1) 100%)`,
                      }}
                    ></div>
                    {/* Play Button Overlay */}
                    <button className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity">
                      <span
                        className="material-symbols-outlined text-secondary text-[48px]"
                        style={{ fontVariationSettings: "'FILL' 1" }}
                      >
                        play_circle
                      </span>
                    </button>
                  </div>

                  {/* Beat Info */}
                  <div className="p-4 flex flex-col flex-grow">
                    <h3 className="font-body-md text-on-surface font-semibold truncate mb-1">
                      {beat.title}
                    </h3>
                    <p className="font-label-sm text-on-surface-variant text-xs mb-2">
                      {beat.producer}
                    </p>

                    {/* Genre & Plays */}
                    <div className="flex justify-between items-center mb-4 text-xs">
                      <span className="px-2 py-1 bg-surface-container rounded font-label-sm text-on-surface-variant">
                        {beat.genre}
                      </span>
                      <span className="font-label-sm text-on-surface-variant">
                        {beat.plays} plays
                      </span>
                    </div>

                    {/* Price & CTA */}
                    <div className="flex justify-between items-center mt-auto pt-4 border-t border-outline-variant/10">
                      <span className="font-headline-md text-secondary text-lg">{beat.price}</span>
                      <button className="px-4 py-2 rounded bg-secondary text-on-secondary font-label-sm text-label-sm uppercase font-bold hover:bg-secondary-fixed transition-colors">
                        License
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="flex justify-center items-center gap-2 mt-stack-lg pt-stack-lg border-t border-outline-variant/15">
              <button className="px-4 py-2 rounded border border-outline-variant hover:border-secondary text-on-surface font-label-sm">
                ← Previous
              </button>
              <div className="flex gap-1">
                {[1, 2, 3].map((page) => (
                  <button
                    key={page}
                    className={`w-8 h-8 rounded font-label-sm ${
                      page === 1
                        ? 'bg-secondary text-on-secondary'
                        : 'bg-surface-container text-on-surface hover:bg-surface-container-high'
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
              <button className="px-4 py-2 rounded border border-outline-variant hover:border-secondary text-on-surface font-label-sm">
                Next →
              </button>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
